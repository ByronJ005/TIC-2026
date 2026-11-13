## Why

Los módulos de Seguridad (submódulos 01 a 03) ya están implementados, pero el módulo "Cooperativas" sigue siendo un placeholder en el dashboard. Sin cooperativas registradas ni administradores vinculados a ellas no se pueden construir rutas, buses, turnos ni tarifas por cooperativa, y no existe la restricción de pertenencia (`ADMIN_COOPERATIVA` solo administra su cooperativa) que exige `PROJECT.md`. El Submódulo 04 (`submodule04.md`) cubre:

1. **RF-09**: gestión de cooperativas por el `ADMIN_GENERAL` (registro, edición, baja lógica y reactivación).
2. **RF-10**: asignación de hasta 3 administradores de cooperativa por cooperativa.

## What Changes

- **Base de datos (migración Alembic)**
  - Nueva tabla `cooperatives(id, name, ruc, address, phone, email, logo_url, is_active, created_at, updated_at)` con `UNIQUE(ruc)`, índice único sobre `lower(name)` y `CHECK` de longitud del RUC (13) y del nombre.
  - `users`: nueva columna nullable `cooperativa_id` (FK a `cooperatives.id`, `ON DELETE SET NULL`, indexada). Un usuario pertenece como máximo a una cooperativa (RN-10.2).
- **Gestión de cooperativas (RF-09)**
  - `GET /api/v1/cooperativas` (lista paginada con búsqueda), `GET /api/v1/cooperativas/{id}`, `POST /api/v1/cooperativas`, `PUT /api/v1/cooperativas/{id}`, `PATCH /api/v1/cooperativas/{id}/estado`. Todos exclusivos de `ADMIN_GENERAL`.
  - Nombre: obligatorio, único (sin distinguir mayúsculas), máx. 100, solo letras, números, espacios, guion medio y apóstrofe. RUC: 13 dígitos validados con el algoritmo de RUC ecuatoriano en backend (módulos 10 y 11), único e inmutable.
  - Dirección, teléfono y correo institucional reutilizan los validadores existentes (`validate_address`, `validate_phone`, validador de email del registro). No generan casos de prueba propios.
  - Logo opcional: enlace (URL `http/https`) o subida de imagen (`POST /api/v1/cooperativas/{id}/logo`, PNG/JPG/WEBP, máx. 2 MB), almacenada en disco local y servida como archivo estático.
  - Cooperativa desactivada: se rechaza (409 `COOPERATIVA_INACTIVA`) cualquier edición o cambio de administradores; el frontend redirige al Inicio con "La cooperativa ha sido desactivada". Los administradores de una cooperativa inactiva pierden acceso a sus funciones operativas pero conservan los módulos de Pasajero; se expone una dependencia reutilizable (`require_active_cooperativa`) para los módulos futuros.
- **Asignación de administradores (RF-10)**
  - `GET /api/v1/cooperativas/{id}/administradores`, `GET /api/v1/cooperativas/{id}/administradores/elegibles?search=` y `PUT /api/v1/cooperativas/{id}/administradores` (reemplaza el conjunto asignado; máx. 3).
  - Elegibles: rol `ADMIN_COOPERATIVA`, activos y sin cooperativa (más los ya asignados a la cooperativa actual). Desvincular conserva el rol y deja `cooperativa_id = NULL`.
  - Validación en backend del tope de 3 y de la exclusividad con bloqueo de filas para evitar condiciones de carrera.
- **Auditoría**: no existe infraestructura previa, por lo que se crea la tabla `audit_logs(id, user_id, action, module, entity, entity_id, result, created_at)` y un `AuditService` reutilizable. Se registran crear cooperativa, editar, cambio de estado y cambios de administradores, sin datos sensibles.
- **Frontend**
  - Vista `CooperativasView.vue` (reemplaza el placeholder en `/dashboard/cooperativas`) con selector de vista tabla o tarjetas, formulario de registro, pantalla/diálogo de edición (engranaje) y sección "Personal de cooperativa" con modal "Gestionar administradores" (búsqueda, selección múltiple, deshabilitado al llegar a 3).
  - `cooperativas.service.ts`, store Pinia y composables de formulario; validadores de nombre y RUC en `useFormValidation.ts`. Componentes shadcn-vue, iconos `@lucide/vue`, tokens del tema Soft Pop, sin emojis.
- **Pruebas**: pytest (validador de RUC, servicios, repositorios, routers, permisos 403 por rol, concurrencia del tope de 3) y vitest (validadores, store, composables, componentes). El 403 por rol se cubre como prueba unitaria y no como CP.

## Capabilities

### New Capabilities
- `cooperative-management`: Registro, consulta (tabla/tarjetas), edición, baja lógica y reactivación de cooperativas con validaciones de nombre, RUC y logo, e inmutabilidad del RUC (RF-09, CP-46 a CP-60).
- `cooperative-administrators`: Asignación y desvinculación de hasta 3 administradores por cooperativa desde el modal de gestión, con filtro de elegibles y búsqueda (RF-10, CP-61 a CP-64).

### Modified Capabilities
<!-- Ninguna: los requisitos de las capacidades existentes de Seguridad no cambian. -->

## Impact

- **Backend**
  - Nueva migración Alembic. Modelos: nuevo `Cooperativa` y `User` (columna `cooperativa_id`).
  - Nuevos: `repositories/cooperativa_repository.py`, `services/cooperativa_service.py`, `services/cooperativa_administrators_service.py`, `services/logo_storage_service.py`, `schemas/cooperativa_schemas.py`, `api/v1/cooperativas_router.py`, validadores `validate_ruc`, `validate_cooperativa_name` en `schemas/validators.py`.
  - Modificados: `core/permissions.py` (`require_active_cooperativa`), `core/config.py` y `.env.example` (directorio y tamaño máximo de logos), `main.py` (router y montaje de estáticos), `models/__init__.py`.
  - Posible dependencia: `python-multipart` para la subida del logo (se verifica si ya está instalada; es la única necesaria).
- **Frontend**: nueva vista, componentes, servicio y store; cambios en `router/index.ts` (reemplazo del placeholder) y `useFormValidation.ts`.
- **Seguridad**: validación de tipo real y tamaño del archivo del logo, nombre de archivo generado por el servidor (nunca el original) y URLs limitadas a `http/https`.
- **Alcance excluido**: rutas, buses, turnos y tarifas de cooperativa (submódulos futuros); aquí solo se deja disponible `require_active_cooperativa` y `users.cooperativa_id` para ellos.
