## 1. Infraestructura y configuración

- [x] 1.1 Crear `backend/src/core/config.py` con `Settings` (pydantic-settings): `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- [x] 1.2 Crear `backend/src/core/database.py` con engine SQLAlchemy, `SessionLocal`, `Base` declarativa
- [x] 1.3 Crear `backend/.env` y `backend/.env.example` con las variables requeridas (DB credentials, JWT secret)
- [x] 1.4 Crear `backend/src/main.py` con app FastAPI, incluir CORS middleware (origins del frontend dev server), y montar el router de auth
- [x] 1.5 Configurar Alembic: `alembic init`, actualizar `alembic/env.py` para usar `Base.metadata` y `settings.database_url`
- [x] 1.6 Agregar `httpx` a `requirements.txt` (necesario para TestClient en tests)

## 2. Modelo y migración de base de datos

- [x] 2.1 Crear modelo `User` en `backend/src/models/user.py`: id, document_type (Enum CEDULA/PASAPORTE), document_number, first_name, last_name, email, hashed_password, role (Enum con PASAJERO por defecto), is_active, created_at, updated_at. Constraints: UNIQUE en email, UNIQUE en (document_type, document_number)
- [x] 2.2 Crear modelo `BlacklistedToken` en `backend/src/models/blacklisted_token.py`: id, jti (UNIQUE, indexed), expires_at
- [x] 2.3 Crear `backend/src/models/__init__.py` exportando ambos modelos
- [x] 2.4 Generar migración Alembic (`alembic revision --autogenerate -m "create users and blacklisted_tokens tables"`) y ejecutar (`alembic upgrade head`)

## 3. Schemas Pydantic

- [x] 3.1 Crear `backend/src/schemas/user_schemas.py`: `UserCreate` (con validadores de cédula, pasaporte, email, contraseña, nombres), `UserResponse` (sin password)
- [x] 3.2 Crear `backend/src/schemas/auth_schemas.py`: `LoginRequest` (email, password), `TokenResponse` (access_token, token_type)
- [x] 3.3 Implementar validador de cédula ecuatoriana (algoritmo módulo 10) como función reutilizable en los schemas
- [x] 3.4 Implementar validador de pasaporte (alfanumérico, 6-20 caracteres) en los schemas
- [x] 3.5 Implementar validador de nombres/apellidos (letras Unicode, espacios, guiones, apóstrofes, max 50 chars)
- [x] 3.6 Implementar validador de contraseña (mín 8 chars, 1 mayúscula, 1 minúscula, 1 número)
- [x] 3.7 Implementar normalización de email (trim + lowercase) en `UserCreate` y `LoginRequest`

## 4. Utilidades de seguridad

- [x] 4.1 Crear `backend/src/core/security.py`: funciones `hash_password`, `verify_password` (bcrypt, factor 12), `create_access_token` (JWT con sub, role, jti, exp), `decode_access_token`
- [x] 4.2 Crear `backend/src/core/dependencies.py`: `get_db` (session generator), `get_current_user` (extrae y valida JWT del header Authorization, verifica blacklist, retorna User)
- [x] 4.3 Crear `backend/src/core/permissions.py`: `require_role(*roles)` como dependency inyectable (para uso futuro por otros módulos)

## 5. Repository layer

- [x] 5.1 Crear `backend/src/repositories/user_repository.py`: `get_by_email`, `get_by_document`, `create_user`, `get_by_id`
- [x] 5.2 Crear `backend/src/repositories/token_repository.py`: `add_to_blacklist`, `is_blacklisted` (buscar por jti)

## 6. Service layer

- [x] 6.1 Crear `backend/src/services/auth_service.py` con función `register_user`: validar unicidad de email y documento, hashear contraseña, crear usuario con rol PASAJERO, retornar UserResponse
- [x] 6.2 Función `login_user` en `auth_service.py`: buscar por email normalizado, verificar contraseña, generar JWT, retornar TokenResponse
- [x] 6.3 Función `logout_user` en `auth_service.py`: extraer jti del token, agregar a blacklist con expires_at del token
- [x] 6.4 Función `get_current_user_profile` en `auth_service.py`: retornar datos del usuario autenticado (UserResponse)

## 7. Router (API endpoints)

- [x] 7.1 Crear `backend/src/api/v1/auth_router.py` con APIRouter prefix `/api/v1/auth`
- [x] 7.2 Endpoint `POST /register`: recibe UserCreate, llama a auth_service.register_user, retorna 201 + UserResponse
- [x] 7.3 Endpoint `POST /login`: recibe LoginRequest, llama a auth_service.login_user, retorna 200 + TokenResponse
- [x] 7.4 Endpoint `POST /logout`: requiere autenticación (Depends get_current_user), llama a auth_service.logout_user, retorna 200
- [x] 7.5 Endpoint `GET /me`: requiere autenticación, retorna UserResponse del usuario actual
- [x] 7.6 Registrar auth_router en `main.py`

## 8. Frontend — API client y service

- [x] 8.1 Crear `frontend/src/services/api-client.ts`: wrapper de fetch con base URL configurable, inyección de Authorization header desde localStorage, interceptor de respuesta 401 (limpiar token, redirigir a /login con mensaje "Sesión expirada")
- [x] 8.2 Crear `frontend/src/services/auth.service.ts`: funciones `register(data)`, `login(credentials)`, `logout()`, `getProfile()` usando api-client

## 9. Frontend — Store de autenticación

- [x] 9.1 Crear `frontend/src/stores/auth.store.ts` (Pinia): state (user, token, isAuthenticated), actions (login, logout, loadUserFromToken, checkAuth), persistencia de token en localStorage
- [x] 9.2 Implementar listener de `storage` event en el store para sincronizar logout entre pestañas (cuando el token se elimina de localStorage en otra pestaña, limpiar estado y redirigir a /login)

## 10. Frontend — Composable de validación

- [x] 10.1 Crear `frontend/src/composables/useFormValidation.ts`: validadores de cédula ecuatoriana (mismo algoritmo módulo 10 del backend), pasaporte (alfanumérico 6-20), email (formato con @ y TLD), contraseña (8+ chars, mayúscula, minúscula, número), nombres (letras, espacios, guiones, apóstrofes, max 50)
- [x] 10.2 Cada validador retorna `{ isValid: boolean, errorMessage: string }` para uso directo en formularios

## 11. Frontend — Vistas (páginas)

- [x] 11.1 Crear `frontend/src/views/RegisterView.vue`: formulario con shadcn-vue (Input, Button, Select para tipo doc, Label, FormField), validación reactiva usando `useFormValidation`, llamada a `auth.service.register`, toast de éxito, redirect a /login tras 2 segundos
- [x] 11.2 Crear `frontend/src/views/LoginView.vue`: formulario con email y contraseña (shadcn-vue), validación de campos vacíos, llamada a `auth.service.login`, guardar token en store, redirect a /dashboard
- [x] 11.3 Crear `frontend/src/views/DashboardView.vue`: página placeholder con saludo al usuario, botón "Cerrar sesión" en menú/header, llamada a store.logout al hacer clic
- [x] 11.4 Aplicar diseño visual consistente con el tema Soft Pop de shadcn-vue: tokens semánticos, modo claro/oscuro, responsive

## 12. Frontend — Routing y guards

- [x] 12.1 Actualizar `frontend/src/router/index.ts`: definir rutas `/login`, `/register`, `/dashboard`, con meta `requiresAuth` en rutas protegidas y meta `guestOnly` en login/register
- [x] 12.2 Implementar navigation guard `beforeEach`: si ruta requiere auth y no hay token → redirect a /login; si ruta es guestOnly y hay token → redirect a /dashboard
- [x] 12.3 Agregar headers anti-caché en las respuestas del navigation guard para rutas protegidas (via meta tag o service worker — evaluar en implementación)

## 13. Tests backend (pytest)

- [x] 13.1 Configurar estructura de tests: `backend/tests/conftest.py` con fixtures de DB de test (SQLite en memoria o PostgreSQL de test), TestClient de FastAPI, fixture de usuario de prueba
- [x] 13.2 Test `test_password_hashing`: verificar que hash_password y verify_password funcionan correctamente, que el hash no es igual al plain text
- [x] 13.3 Test `test_jwt_token_creation`: verificar que create_access_token genera un token con sub, role, jti, exp correctos
- [x] 13.4 Test `test_jwt_token_expired`: verificar que un token expirado es rechazado por decode_access_token
- [x] 13.5 Test `test_blacklist_blocks_token`: verificar que un token cuyo jti está en blacklist es rechazado por get_current_user
- [x] 13.6 Test `test_cedula_validation`: casos válidos e inválidos del algoritmo de cédula ecuatoriana
- [x] 13.7 Test `test_passport_validation`: alfanumérico válido, caracteres especiales rechazados, longitud fuera de rango
- [x] 13.8 Test `test_email_normalization`: verificar trim + lowercase en login y registro
- [x] 13.9 Test `test_duplicate_email_rejected`: registro con email existente retorna error HTTP adecuado
- [x] 13.10 Test `test_duplicate_document_rejected`: registro con documento existente retorna error HTTP adecuado
- [x] 13.11 Test `test_register_assigns_pasajero`: verificar que el usuario creado siempre tiene role PASAJERO
- [x] 13.12 Test `test_login_returns_token`: login exitoso retorna access_token y token_type
- [x] 13.13 Test `test_login_wrong_password`: login con contraseña incorrecta retorna mensaje genérico "Credenciales incorrectas"
- [x] 13.14 Test `test_protected_endpoint_without_token`: GET /me sin Authorization retorna 401

## 14. Tests frontend (vitest)

- [x] 14.1 Test `test_cedula_validator`: mismos casos que backend — cédulas válidas e inválidas con algoritmo módulo 10
- [x] 14.2 Test `test_password_validator`: contraseñas que cumplen y no cumplen las reglas (8 chars, mayúscula, minúscula, número)
- [x] 14.3 Test `test_email_validator`: emails válidos e inválidos
- [x] 14.4 Test `test_name_validator`: nombres con caracteres válidos e inválidos, longitud máxima
- [x] 14.5 Test `test_auth_store_login`: verificar que el store actualiza user, token, isAuthenticated tras login exitoso (mock de API)
- [x] 14.6 Test `test_auth_store_logout`: verificar que el store limpia token, user, isAuthenticated y remueve de localStorage
- [x] 14.7 Test `test_navigation_guard`: ruta protegida sin token redirige a /login, ruta guest con token redirige a /dashboard
