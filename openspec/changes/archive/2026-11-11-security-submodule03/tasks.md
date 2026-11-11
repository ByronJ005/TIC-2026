## 1. Base de datos y modelos

- [x] 1.1 Agregar a `User` en `backend/src/models/user.py` las columnas nullable `phone` (String(10)), `address` (String(150)), `birth_date` (Date) y `password_changed_at` (DateTime con zona horaria).
- [x] 1.2 Crear el modelo `PasswordResetToken` (`id`, `user_id` FK con `ON DELETE CASCADE`, `token_hash` único e indexado, `expires_at`, `used_at`, `created_at`) y registrarlo en `models/__init__.py`.
- [x] 1.3 Generar migración Alembic reversible (columnas nuevas de `users` y tabla `password_reset_tokens`) y ejecutar `alembic upgrade head`.

## 2. Configuración y correo

- [x] 2.1 Agregar a `backend/src/core/config.py` las variables `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_USE_TLS`, `MAIL_FROM_ADDRESS`, `MAIL_FROM_NAME` y `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES` (30 por defecto), sin secretos reales como valores por defecto.
- [x] 2.2 Actualizar `backend/.env.example` con los nombres de las variables nuevas (valores de ejemplo para Mailtrap, sin credenciales reales).
- [x] 2.3 Crear `backend/src/services/email_service.py` con el protocolo `EmailSender` y `SmtpEmailSender` (`smtplib`, STARTTLS según `SMTP_USE_TLS`), más la dependencia `get_email_sender` para `Depends`. No registrar credenciales ni tokens.
- [x] 2.4 Documentar en el README o en comentarios cómo obtener las credenciales de Mailtrap Sandbox (SMTP Settings del inbox) y completar el `.env` local.

## 3. Validadores y schemas

- [x] 3.1 Agregar a `backend/src/schemas/validators.py` las constantes (`MIN_BIRTH_YEAR`, `PHONE_LENGTH`, `ADDRESS_MAX_LENGTH`, mensajes de error de los CP-38 a CP-41 y CP-42) y los validadores `validate_phone_format`, `validate_address_length` y `validate_birth_date(value, today=None)`. Reutilizar `validate_name_format` y `validate_password_format`.
- [x] 3.2 Crear `backend/src/schemas/password_recovery_schemas.py` con `ForgotPasswordRequest` (correo requerido y formato) y `ResetPasswordRequest` (token y nueva contraseña con el validador del registro), y su respuesta con `message`.
- [x] 3.3 Crear `backend/src/schemas/profile_schemas.py` con `ProfileUpdate`, `ProfileResponse` (perfil, `message`, `access_token` opcional). Ningún campo de email ni documento en la entrada.

## 4. Repositorios

- [x] 4.1 Crear `backend/src/repositories/password_reset_token_repository.py`: crear token, buscar por hash, invalidar tokens vigentes de un usuario y marcar token como usado.
- [x] 4.2 Extender `UserRepository` con `update_profile(user, ...)` y `update_password(user, hashed_password, changed_at)`, ambos con una única confirmación de transacción.

## 5. Servicios

- [x] 5.1 Crear `backend/src/services/password_recovery_service.py`: `request_reset` (casos de D3, tokens anteriores invalidados, envío con `BackgroundTasks`) y `reset_password` (D1: un solo uso, vigencia, cuenta activa, formato de contraseña, `password_changed_at`).
- [x] 5.2 Crear `backend/src/services/profile_service.py` con el orden de validación de D6, atomicidad y emisión de token nuevo al cambiar la contraseña.
- [x] 5.3 Actualizar `core/dependencies.py` (`get_current_user`) para rechazar con 401 los tokens con `iat` anterior a `password_changed_at`.

## 6. Routers

- [x] 6.1 Agregar a `backend/src/api/v1/auth_router.py` `POST /auth/forgot-password` y `POST /auth/reset-password` (solo reciben input, llaman al service y devuelven DTOs).
- [x] 6.2 Crear `backend/src/api/v1/profile_router.py` con `GET /perfil` y `PUT /perfil` (solo `get_current_user`) y registrarlo en `main.py`.

## 7. Pruebas unitarias backend (pytest)

- [x] 7.1 `backend/tests/unit/test_profile_validators.py` con los casos límite de celular, dirección y fecha (D5).
- [x] 7.2 `backend/tests/unit/test_password_recovery_service.py` con `EmailSender` falso: correos, tokens (vigente, límite, vencido, reutilizado, invalidado, inexistente, manipulado), cuenta inactiva, hash almacenado, fallo del sender.
- [x] 7.3 `backend/tests/unit/test_profile_service.py`: obligatorios, formato, opcionales, contraseñas "todo o nada", actual incorrecta, igual a la actual, formato, confirmación, atomicidad, token nuevo.
- [x] 7.4 `backend/tests/unit/test_email_service.py` con `smtplib` simulado.
- [x] 7.5 `backend/tests/unit/test_session_invalidation.py` para `get_current_user` con `password_changed_at`.
- [x] 7.6 Tests de API en `backend/tests/` para `forgot-password`, `reset-password` y `perfil`.
- [x] 7.7 Actualizar los tests existentes de autenticación que dependan de `UserResponse` o de `get_current_user`.

## 8. Frontend — validadores, servicios y stores

- [x] 8.1 Agregar a `frontend/src/composables/useFormValidation.ts` `validatePhone`, `validateAddress` y `validateBirthDate` con las constantes y mensajes de los CP (reutilizar `validateName` y `validatePassword`).
- [x] 8.2 Crear `frontend/src/services/password-recovery.service.ts` y `frontend/src/services/profile.service.ts` con tipos estrictos (sin `any`).
- [x] 8.3 Crear el store de perfil (`stores/profile.store.ts`) y el composable `useProfileForm` (validación, regla "todo o nada", restauración de datos).
- [x] 8.4 Actualizar `auth.store.ts` para reemplazar el token y el usuario tras un cambio de contraseña.

## 9. Frontend — vistas y rutas

- [x] 9.1 Crear `ForgotPasswordView.vue` y `ResetPasswordView.vue` con componentes shadcn-vue, tokens del tema, iconos `@lucide/vue` y mensajes de los CP.
- [x] 9.2 Agregar el enlace "¿Olvidaste tu contraseña?" en `LoginView.vue`.
- [x] 9.3 Crear `ProfileView.vue` y reemplazar el placeholder de `/dashboard/perfil`. Email y Documento deshabilitados. Campo de fecha con `min` y `max` (hoy).
- [x] 9.4 Actualizar `router/index.ts`: rutas `/forgot-password` y `/reset-password` como rutas de invitado.

## 10. Pruebas unitarias frontend (vitest)

- [x] 10.1 Ampliar `validators.spec.ts` con celular, dirección y fecha.
- [x] 10.2 `ForgotPasswordView.spec.ts` y `ResetPasswordView.spec.ts`.
- [x] 10.3 `ProfileView.spec.ts` o `useProfileForm.spec.ts` y `profile.store.spec.ts`.
- [x] 10.4 Actualizar `auth.store.spec.ts` y `router.spec.ts`.

## 11. Verificación integral

- [x] 11.1 Ejecutar `pytest` y confirmar 0 fallos.
- [x] 11.2 Ejecutar `npm run test:unit` y `npm run lint`.
- [x] 11.3 Con Mailtrap configurado, validar manualmente CP-33 a CP-42 y los escenarios nuevos (token vencido, reutilizado, cuenta inactiva, contraseña actual incorrecta).
- [x] 11.4 Actualizar `submodule03.md` con los CP ajustados (CP-33, CP-37, CP-41, CP-42, RN-06.1, RN-06.4) y los CP nuevos.
