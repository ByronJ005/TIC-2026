## Why

Los submódulos 01 (registro, login, logout) y 02 (roles, usuarios) ya existen. Falta el Submódulo 03 (Gestión de Perfil y Recuperación de Cuenta, `submodule03.md`), que cubre:

1. **RF-03**: que cualquier usuario que olvidó su contraseña pueda restablecerla mediante un enlace enviado a su correo registrado.
2. **RF-06**: que cualquier usuario autenticado pueda actualizar su información de perfil (Nombres, Apellidos, Contraseña, Celular, Dirección y Fecha de nacimiento).

Durante la exploración se aclararon ambigüedades del documento original. Las decisiones resultantes se aplican en esta propuesta y modifican algunos CP y reglas de negocio (ver "Ajustes a los requisitos originales").

## What Changes

- **Base de datos (migración Alembic)**
  - `users`: nuevas columnas nullable `phone` (celular), `address` (dirección), `birth_date` (fecha de nacimiento) y `password_changed_at` (timestamp con zona horaria, nullable).
  - Nueva tabla `password_reset_tokens(id, user_id FK ON DELETE CASCADE, token_hash UNIQUE, expires_at, used_at, created_at)`. El token en claro nunca se guarda.
- **Recuperación de contraseña (RF-03)**
  - `POST /api/v1/auth/forgot-password`: valida el correo (vacío, formato, no registrado) y, si la cuenta existe y está activa, genera un token, invalida los tokens anteriores del usuario y envía el correo.
  - `POST /api/v1/auth/reset-password`: recibe token y nueva contraseña (validador del submódulo 01), verifica vigencia y uso único, guarda la contraseña, marca el token como usado y actualiza `password_changed_at`.
  - Vigencia del enlace: 30 minutos (`PASSWORD_RESET_TOKEN_EXPIRE_MINUTES`). Un solo uso. Solicitar un enlace nuevo invalida los anteriores.
- **Correo electrónico**
  - Puerto `EmailSender` con implementación SMTP basada en `smtplib` (sin dependencias nuevas). El proveedor para pruebas es Mailtrap Email Sandbox; cambiar de proveedor solo requiere cambiar variables de entorno.
  - Variables nuevas: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_USE_TLS`, `MAIL_FROM_ADDRESS`, `MAIL_FROM_NAME`, `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES` (en `config.py` y `.env.example`; `FRONTEND_URL` ya existe).
- **Perfil (RF-06)**
  - `GET /api/v1/perfil` y `PUT /api/v1/perfil` para el usuario autenticado. Email y documento no son editables.
  - Nombres y Apellidos reutilizan los validadores del submódulo 01. La nueva contraseña reutiliza `validate_password_format`.
  - Nuevos validadores: celular (10 dígitos numéricos), dirección (máx. 150) y fecha de nacimiento (entre 1/ene/1900 y hoy, calculado al validar).
  - Cambio de contraseña: contraseña actual, nueva y confirmación son "todo o nada". La actual debe ser correcta y la nueva distinta de la actual. Tras el cambio, se invalidan las demás sesiones y se devuelve un token nuevo para mantener la sesión actual.
- **Sesiones**
  - `get_current_user` rechaza (401) tokens cuyo `iat` sea anterior a `password_changed_at`.
- **Frontend**
  - Vistas `ForgotPasswordView.vue` (`/forgot-password`) y `ResetPasswordView.vue` (`/reset-password?token=...`), enlace "¿Olvidaste tu contraseña?" en `LoginView.vue`.
  - Vista `ProfileView.vue` en `/dashboard/perfil` (reemplaza el placeholder), con `profile.service.ts`, `password-recovery.service.ts` y un store o composable para cada flujo.
  - Validadores de celular, dirección y fecha en `useFormValidation.ts`.
- **Pruebas unitarias** (backend con pytest y frontend con vitest) para cada componente, cubriendo casos adicionales a los CP (límites, errores, estados inválidos, tokens vencidos o reutilizados).

### Ajustes a los requisitos originales

| Elemento | Cambio |
|---|---|
| CP-33 | Mensaje de éxito: "Hemos procesado tu solicitud. Si el correo corresponde a una cuenta activa, recibirás un enlace en los próximos minutos." Se muestra también (sin enviar correo) cuando la cuenta está inactiva. |
| CP-35, CP-36 | Sin cambios. |
| CP-37 | Se divide: (a) datos personales sin tocar la contraseña, (b) cambio de contraseña con la actual y confirmación. |
| CP-41 | El tope superior es la fecha de hoy. Mensaje: "La fecha de nacimiento debe estar entre 1900 y la fecha actual". |
| CP-42 | Se aplica a Nombres y Apellidos. La parte de Contraseña pasa a la regla "todo o nada". |
| RN-06.1 | Nombres y Apellidos obligatorios. Contraseña opcional con la regla "todo o nada". |
| RN-06.4 | La fecha de nacimiento no puede ser anterior al 1/ene/1900 ni posterior a hoy. |
| CP nuevos | Ver specs `password-recovery` y `user-profile`. |

## Capabilities

### New Capabilities
- `password-recovery`: Solicitud de enlace de restablecimiento por correo y definición de nueva contraseña mediante token de un solo uso con vigencia (RF-03, CP-33 a CP-36).
- `user-profile`: Consulta y actualización del perfil propio, incluyendo validaciones de campos y cambio de contraseña con contraseña actual (RF-06, CP-37 a CP-42).

### Modified Capabilities
- `route-protection`: Los tokens emitidos antes de un cambio o restablecimiento de contraseña dejan de ser válidos.

## Impact

- **Backend**
  - Nueva migración Alembic. Modelos: `User` (4 columnas) y nuevo `PasswordResetToken`.
  - Nuevos: `repositories/password_reset_token_repository.py`, `services/password_recovery_service.py`, `services/profile_service.py`, `services/email_service.py` (puerto y adaptador SMTP), `api/v1/profile_router.py`, schemas para recuperación y perfil, validadores nuevos en `schemas/validators.py`.
  - Modificados: `core/config.py`, `core/dependencies.py` (validación de `password_changed_at`), `api/v1/auth_router.py`, `main.py`, `.env.example`.
- **Frontend**: nuevas vistas, servicios y stores; cambios en `router/index.ts` (rutas públicas y reemplazo del placeholder de Perfil), `LoginView.vue` y `useFormValidation.ts`.
- **Operación**: el usuario debe configurar Mailtrap y completar su `.env` local. La cuota gratuita de Mailtrap Sandbox es de 50 correos al mes.
- **Seguridad conocida**: CP-35 mantiene la diferenciación de correos no registrados (decisión aceptada), por lo que la enumeración de correos sigue posible (el registro, CP-01, ya la permite).

