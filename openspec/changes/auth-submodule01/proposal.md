## Why

BoletoYa no tiene sistema de autenticación implementado. Sin este submódulo, ningún otro módulo (Cooperativas, Reservas) puede funcionar porque no hay forma de identificar usuarios ni proteger endpoints. Es el pilar 0 de la aplicación y bloquea todo el desarrollo posterior.

## What Changes

- **Nuevo modelo `User`** en PostgreSQL con campos: tipo de documento, número de documento, nombres, apellidos, email (UNIQUE), contraseña hasheada, rol, timestamps.
- **Tabla `blacklisted_tokens`** para invalidación de JWT en logout.
- **API REST** bajo `/api/v1/auth/` con endpoints: `POST /register`, `POST /login`, `POST /logout`, `GET /me`.
- **Schemas Pydantic** para validación backend: cédula ecuatoriana (algoritmo módulo 10), pasaporte (alfanumérico), email, contraseña (mín. 8 chars, mayúscula, minúscula, número), nombres/apellidos (solo letras, espacios, guiones, apóstrofes; max 50 chars).
- **Utilidades de seguridad**: hashing bcrypt (passlib, factor 12), generación/verificación JWT (python-jose, access token 30 min), dependency `get_current_user`.
- **Páginas Vue**: `RegisterView.vue`, `LoginView.vue`, `DashboardView.vue` (placeholder PASAJERO).
- **Store Pinia `auth`**: estado de autenticación, token, datos de usuario.
- **Service frontend `auth.service.ts`**: llamadas HTTP centralizadas a la API de auth.
- **Composable `useFormValidation`**: validadores de cédula, pasaporte, email, contraseña, nombres — mismas reglas que el backend.
- **Navigation guards**: protección de rutas, redirección a `/login` sin sesión, redirección a `/dashboard` si ya autenticado.
- **Interceptor HTTP**: detecta 401 → limpia token → redirige a login con mensaje "Sesión expirada".
- **Sincronización multi-pestaña**: listener de `storage` event para detectar logout en otra pestaña.
- **Tests automatizados**: ~13 tests backend (pytest) + ~7 tests frontend (vitest).

## Capabilities

### New Capabilities
- `user-registration`: Registro público de usuarios con validación de cédula ecuatoriana, pasaporte, email, contraseña y datos personales. Asigna rol PASAJERO automáticamente.
- `user-login`: Autenticación por email + contraseña con JWT. Normalización de email (trim + lowercase). Redirección a dashboard según rol.
- `user-logout`: Cierre de sesión con invalidación de JWT via blacklist. Protección contra uso post-logout (botón atrás, otra pestaña, token expirado).
- `route-protection`: Guards de navegación frontend y dependency de autenticación backend. Rutas protegidas requieren sesión válida.

### Modified Capabilities
_Ninguna. No existen specs previos._

## Impact

- **Backend**: Nuevos archivos en `src/models/`, `src/schemas/`, `src/repositories/`, `src/services/`, `src/api/`, `src/core/`. Migración Alembic para tablas `users` y `blacklisted_tokens`.
- **Frontend**: Nuevas vistas en `views/`, nuevo store en `stores/`, nuevo service en `services/`, nuevo composable, actualización de `router/index.ts`.
- **Dependencias backend**: `httpx` (para TestClient en tests). Las demás (`fastapi`, `python-jose`, `passlib`, `bcrypt`, `SQLAlchemy`, `alembic`, `pydantic-settings`) ya están en `requirements.txt`.
- **Dependencias frontend**: Posiblemente `axios` para HTTP client (evaluar en diseño si usar fetch nativo). Las demás ya están.
- **Base de datos**: 2 tablas nuevas (`users`, `blacklisted_tokens`), constraints UNIQUE en email y document_number.
- **Configuración**: Variables de entorno en `.env` para JWT_SECRET_KEY, DATABASE_URL, etc.
