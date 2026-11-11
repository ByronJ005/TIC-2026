## Context

Los submódulos 01 y 02 están completos y archivados. La arquitectura es obligatoria (Router → Service → Repository; Component → Store/Composable → API Service). Estado relevante del código:

- `User` no tiene celular, dirección, fecha de nacimiento ni marca de cambio de contraseña.
- Las sesiones son JWT sin estado (`sub`, `jti`, `iat`, `exp`) con lista negra por `jti` (`blacklisted_tokens`). No hay forma de invalidar todas las sesiones de un usuario.
- `schemas/validators.py` y `useFormValidation.ts` contienen los validadores del registro (nombre, email, contraseña) y sus constantes de mensaje.
- `config.py` (pydantic-settings) ya expone `FRONTEND_URL`. No existe infraestructura de correo.
- El módulo "Perfil" existe como placeholder en `/dashboard/perfil`.

## Goals / Non-Goals

**Goals:**
- Implementar RF-03 (restablecer contraseña) y RF-06 (actualizar perfil) con los CP del documento, ajustados por las decisiones de la exploración.
- Reutilizar los validadores de Nombres y Contraseña del submódulo 01 sin duplicarlos.
- Enviar correos con un componente reemplazable, configurado solo por variables de entorno.
- Cubrir con pruebas unitarias casos adicionales a los CP.

**Non-Goals:**
- Verificación de correo en el registro, cambio de email o de documento.
- Rate limiting de solicitudes de recuperación (queda como mejora futura).
- Plantillas de correo HTML elaboradas o internacionalización.
- Cerrar la enumeración de correos de CP-35 y CP-01 (decisión aceptada por el usuario).
- Proveedor de correo de producción: solo Mailtrap Email Sandbox en pruebas.

## Decisions

### D1: Token de restablecimiento — aleatorio, hasheado, un solo uso
Se genera con `secrets.token_urlsafe(32)`. Se guarda su hash SHA-256 en `password_reset_tokens` (`token_hash UNIQUE`), con `expires_at` y `used_at`. SHA-256 es suficiente porque el token tiene alta entropía; bcrypt no aporta.

- Vigencia: `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES` (30 por defecto). Un token es válido si `used_at IS NULL` y `now < expires_at`.
- Al crear un token, los tokens vigentes y no usados del mismo usuario se marcan como usados (`used_at = now`).
- Todos los fallos de validación del token (inexistente, vencido, usado, cuenta inactiva) devuelven el mismo error: "El enlace de restablecimiento es inválido o ha expirado".
- *Alternativa descartada:* JWT firmado de corta vida. No permite uso único sin tabla de revocación y ya existe el modelo de tabla para tokens.

### D2: Puerto `EmailSender` con adaptador SMTP
`services/email_service.py` define el protocolo `EmailSender.send(to, subject, body)` y la implementación `SmtpEmailSender` con `smtplib` (STARTTLS cuando `SMTP_USE_TLS=true`). Se inyecta vía `Depends` en el servicio de recuperación. Sin dependencias nuevas.

- Variables: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_USE_TLS`, `MAIL_FROM_ADDRESS`, `MAIL_FROM_NAME`, `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES` en `Settings` y `.env.example`.
- Mailtrap Email Sandbox: `sandbox.smtp.mailtrap.io`, puerto `2525`, credenciales de "SMTP Settings" del inbox. Cuota gratuita de 50 correos al mes.
- El envío se programa con `BackgroundTasks` de FastAPI para no bloquear la respuesta ni exponer diferencias de tiempo. Los errores de envío se registran sin token ni credenciales y no se propagan al usuario.
- El cuerpo del correo contiene el enlace `{FRONTEND_URL}/reset-password?token=...` y la vigencia. Nunca la contraseña.

### D3: Respuestas del endpoint `forgot-password`
| Caso | Respuesta |
|---|---|
| Correo vacío o solo espacios | 422, "Se requiere el correo electrónico" (CP-36) |
| Formato inválido | 422, "Correo electrónico inválido" (validador del submódulo 01) |
| No registrado | 404, "El correo ingresado no corresponde a una cuenta registrada en el sistema" (CP-35) |
| Registrado e inactivo | 200, mensaje del CP-33, sin token ni correo |
| Registrado y activo | 200, mensaje del CP-33, token creado y correo enviado |

El mensaje del CP-33 se define como constante en el servicio y se reutiliza en el frontend a partir del campo `message` de la respuesta.

### D4: Invalidación de sesiones con `password_changed_at`
`users.password_changed_at` se actualiza en el restablecimiento y en el cambio desde el perfil. `get_current_user` rechaza con 401 ("Sesión revocada o inválida") si el `iat` del token es menor que `int(password_changed_at.timestamp())`. `iat` se emite en segundos enteros, por lo que la comparación es `iat < floor(password_changed_at)`.

- En el cambio desde el perfil, la sesión actual debe sobrevivir: la respuesta incluye un `access_token` nuevo emitido en o después de `password_changed_at`, y el frontend reemplaza el token almacenado.
- Limitación conocida: un token emitido en el mismo segundo del cambio se considera válido. Es aceptable en este prototipo.
- *Alternativa descartada:* poner en lista negra todos los `jti` activos. No existe un índice de sesiones por usuario.

### D5: Validadores nuevos junto a los existentes (sin duplicar)
En `validators.py` se agregan `validate_phone_format`, `validate_address_length` y `validate_birth_date`, con sus constantes de mensaje, y se reutilizan `validate_name_format` y `validate_password_format`. El espejo en `useFormValidation.ts` agrega `validatePhone`, `validateAddress` y `validateBirthDate`.

- `validate_birth_date(value, today)`: recibe la fecha de referencia como parámetro opcional (por defecto `date.today()`) para que las pruebas no dependan del reloj. Rango: `date(1900, 1, 1) <= value <= today`.
- Constantes con nombre: `MIN_BIRTH_YEAR = 1900`, `PHONE_LENGTH = 10`, `ADDRESS_MAX_LENGTH = 150`.
- Celular: si hay caracteres no numéricos, error "El celular solo debe contener números"; si es numérico y su longitud es distinta de 10, "El número de celular debe tener exactamente 10 dígitos". Los valores vacíos o solo espacios se tratan como "sin valor" (nulo). Un valor con espacios internos o en los extremos y contenido se considera no numérico.
- Dirección: se recorta y se limita a 150 caracteres.
- El input de fecha del frontend usa `min="1900-01-01"` y `max` igual a hoy, pero el backend sigue siendo la fuente de verdad.
- Riesgo: "hoy" se calcula con la fecha del servidor. Un usuario en otra zona horaria cerca de la medianoche podría ver un desfase de un día. Aceptable para el prototipo.

### D6: Contrato de `PUT /api/v1/perfil`
`ProfileUpdate` (DTO): `first_name`, `last_name`, `phone?`, `address?`, `birth_date?`, `current_password?`, `new_password?`, `confirm_password?`. El router solo recibe el DTO y llama a `ProfileService`.

Orden de validación en el servicio (todo se aplica en una única transacción: si algo falla, nada se persiste):
1. Nombres y Apellidos no vacíos → "Los campos obligatorios no pueden quedar vacíos"; luego formato → "Los nombres/apellidos proporcionados contienen caracteres inválidos".
2. Celular, dirección y fecha (si se informan).
3. Si cualquiera de los tres campos de contraseña tiene contenido, deben estar todos: faltante de la actual → "Debe ingresar su contraseña actual para cambiarla"; faltante de la nueva o de la confirmación → "Este campo es requerido".
4. Contraseña actual correcta → de lo contrario "La contraseña actual es incorrecta".
5. Nueva con formato válido, igual a la confirmación y distinta de la actual → "La nueva contraseña debe ser diferente de la actual".

Respuesta: `ProfileResponse` con el perfil actualizado, `message` ("Perfil actualizado exitosamente" o "Contraseña actualizada exitosamente" si cambió la contraseña) y `access_token` solo si la contraseña cambió. Los campos `email` y `document_*` no existen en el DTO de entrada, así que se ignoran por construcción.

### D7: Frontend — vistas públicas, perfil y regla de "todo o nada"
- `/forgot-password` y `/reset-password` son rutas de invitado (como login y registro): con sesión activa redirigen al dashboard.
- `ProfileView.vue` reemplaza el placeholder de `/dashboard/perfil`. Usa un composable `useProfileForm` que contiene la validación de campos, la regla de contraseñas "todo o nada", la restauración de datos anteriores ante error (CP-42) y las llamadas a `profile.service.ts` a través de un store de perfil.
- Los componentes no hacen llamadas HTTP; usan `profile.service.ts` y `password-recovery.service.ts`.
- Tras cambiar la contraseña, el store de autenticación reemplaza el token con el devuelto por el backend.

## Architecture & Layering

```
Backend
  auth_router   → PasswordRecoveryService → UserRepository
                                          → PasswordResetTokenRepository
                                          → EmailSender (SMTP)
  profile_router → ProfileService         → UserRepository
  dependencies.get_current_user ─ compara iat con password_changed_at

Frontend
  ForgotPasswordView / ResetPasswordView / ProfileView
     → composables (useProfileForm, ...) / stores
     → password-recovery.service.ts / profile.service.ts
     → REST API
```

Permisos: `GET/PUT /perfil` solo requieren `get_current_user` (todos los roles). Los endpoints de recuperación son públicos. No se agregan reglas de rol nuevas.

## UI/UX & Design Guidelines

- Componentes shadcn-vue existentes y tokens semánticos del tema Soft Pop. Sin emojis; iconos solo de `@lucide/vue` (por ejemplo `Mail`, `KeyRound`, `User`, `CheckCircle2`, `AlertCircle`, `Loader2`).
- Compatible con modo claro y oscuro.
- Mensajes de error junto al campo; notificación de éxito visible tras actualizar.
- Campos de contraseña con `autocomplete` adecuado (`current-password`, `new-password`).

## Risks / Trade-offs

- **Enumeración de correos (CP-35)**: sigue posible por decisión del usuario; el mensaje del CP-33 solo evita revelar el estado de cuentas inactivas.
- **Cuota Mailtrap (50 correos/mes)**: puede agotarse durante las pruebas manuales; las pruebas unitarias usan un `EmailSender` falso y no consumen cuota.
- **Migración**: columnas nuevas nullable, sin pérdida de datos. La migración debe ser reversible.
- **`password_changed_at` y reloj**: se compara en segundos enteros; documentado en D4.

## Automated Testing Strategy

Pruebas unitarias para cada componente, con casos adicionales a los CP. Las pruebas del backend usan un `EmailSender` falso y repositorios en memoria o sesión de prueba; ninguna prueba envía correos reales.

### Backend (pytest, en `backend/tests/unit/`)
- **`test_profile_validators.py`**: celular con 9, 10 y 11 dígitos, vacío, solo espacios, letras, guion, espacios y `+`; dirección con 150 y 151 caracteres, vacía y con espacios en los extremos; fecha con 31/dic/1899, 1/ene/1900, hoy, mañana y fecha inválida; el límite superior sigue a la fecha de referencia inyectada (año actual calculado, no fijo).
- **`test_password_recovery_service.py`**: correo con mayúsculas y espacios; vacío y formato inválido; no registrado; inactivo (sin token ni correo); token vigente, justo en el límite de expiración, vencido, reutilizado, invalidado por un segundo envío, inexistente, vacío y manipulado; cuenta desactivada tras emitir el token; el hash se guarda y el token en claro no; nueva contraseña inválida no consume el token; éxito actualiza `password_changed_at`; fallo del `EmailSender` no propaga el error.
- **`test_profile_service.py`**: Nombres y Apellidos vacíos, solo espacios, con caracteres inválidos y de 51 caracteres; actualización sin cambios; campos opcionales vaciados; `email`/`document` no modificables; contraseña: solo la actual, solo la nueva, solo la confirmación, actual incorrecta, nueva igual a la actual, formato inválido, confirmación distinta, éxito con token nuevo y `password_changed_at` actualizado; atomicidad ante falla de contraseña.
- **`test_email_service.py`**: el adaptador SMTP con `smtplib` simulado (STARTTLS, login, remitente y destinatario, error de conexión, configuración ausente); el cuerpo contiene el enlace y no registra el token.
- **`test_session_invalidation.py`**: `get_current_user` con token anterior, igual y posterior a `password_changed_at`, y con `password_changed_at` nulo.
- **Tests de API** (`backend/tests/`): `forgot-password`, `reset-password` y `perfil` con códigos HTTP y mensajes de los CP.

### Frontend (vitest, en `frontend/src/__tests__/`)
- **`validators.spec.ts`** (ampliado): `validatePhone`, `validateAddress` y `validateBirthDate` con los mismos límites que el backend.
- **`ForgotPasswordView.spec.ts`**: correo vacío, formato inválido, no registrado (CP-35), éxito (CP-33) y deshabilitado del botón durante el envío.
- **`ResetPasswordView.spec.ts`**: token ausente, token inválido o vencido, contraseña inválida, confirmación distinta y éxito con redirección a login.
- **`ProfileView.spec.ts` / `useProfileForm.spec.ts`**: restauración de datos tras error (CP-42), regla "todo o nada" de contraseñas, `max` de fecha igual a hoy, Email y Documento deshabilitados y notificaciones de éxito.
- **`profile.store.spec.ts` y `auth.store.spec.ts`**: reemplazo del token tras cambiar la contraseña y manejo de errores del backend.
- **`router.spec.ts`**: `/forgot-password` y `/reset-password` accesibles sin sesión y redirigidos con sesión.

