## Why

Actualmente, el sistema BoletoYa cuenta con el submódulo 01 (registro, login y logout), donde todos los usuarios son registrados únicamente como `PASAJERO` y poseen una única columna de rol estático. Para dar soporte a la operación del sistema, se requiere el Submódulo 02 (Gestión de Usuarios, Roles y Permisos) que implementa los requisitos funcionales RF-05, RF-07 y RF-08:
1. Permitir que los usuarios autenticados visualicen en su dashboard únicamente los módulos autorizados según su(s) rol(es) (soporte de roles combinados como Administrador de Cooperativa + Pasajero).
2. Permitir al `ADMIN_GENERAL` asignar y revocar roles secundarios a usuarios registrados, manteniendo el rol `PASAJERO` como inmutable y base permanente.
3. Permitir al `ADMIN_GENERAL` gestionar la baja (borrado lógico) y rehabilitación de usuarios, impidiendo el acceso de cuentas inactivas con mensajes claros.

## What Changes

- **Modelo de Datos y Migración Alembic (N:M Roles)**:
  - Creación de tabla `user_roles(user_id, role)` con llave primaria compuesta y llaves foráneas.
  - Migración de datos existentes: vinculación de cada usuario existente con el rol base `PASAJERO`.
  - Eliminación de la columna única `role` en la tabla `users` a favor de la relación N:M.
  - Normalización del enum de roles a `ADMIN_GENERAL`, `ADMIN_COOPERATIVA`, `SECRETARIA_COOPERATIVA`, `PASAJERO` (alineado a `PROJECT.md`).
- **Seguridad y Control de Acceso Centralizado**:
  - Modificación de `permissions.py` para validar pertenencia contra el conjunto de roles activos del usuario (`current_user.roles`).
  - La verificación de roles en el backend se realiza siempre contra la base de datos (inmediatez ante revocaciones de acceso).
  - Bloqueo de auto-operación: un `ADMIN_GENERAL` no puede darse de baja a sí mismo ni revocar su propio rol de administrador (retorna HTTP 403 Forbidden).
  - Ajuste del mensaje de rechazo de autenticación para cuentas inactivas en `auth_service.py` a: `"Su cuenta se encuentra inactiva. Contacte al administrador"` (CP-31).
- **Backend API (Gestión de Usuarios)**:
  - Repositorio `UserRepository` extendido con paginación, conteo, búsqueda insensible a mayúsculas/minúsculas (`ILIKE`) por nombre, apellido y correo, y filtro de estado `include_inactive`.
  - Servicio `UserService` con validaciones de negocio: garantía de rol base `PASAJERO`, detección de estados inválidos (reactivar cuenta ya activa o desactivar cuenta ya inactiva), protección de auto-modificación.
  - Router `/api/v1/usuarios`:
    - `GET /api/v1/usuarios`: listado paginado con búsqueda (`search`, `page`, `size`, `include_inactive`), restringido a `ADMIN_GENERAL`.
    - `PUT /api/v1/usuarios/{id}/roles`: actualización de roles secundarios, restringido a `ADMIN_GENERAL`.
    - `PATCH /api/v1/usuarios/{id}/estado`: activación/desactivación lógica (`is_active`), restringido a `ADMIN_GENERAL`.
- **Frontend — Layout y Navegación Dinámica por Roles**:
  - Refactorización de `DashboardView.vue` a un layout estructurado (`DashboardLayout.vue`) con barra lateral (Sidebar) reactiva a los roles del usuario logueado (`authStore.user.roles`), soporte para colapsar/expandir en escritorio con un clic, menú desplegable (drawer/overlay) responsive para dispositivos móviles y vista principal `<RouterView>`.
  - Implementación de `DashboardHomeView.vue` con la bienvenida al usuario.
  - Generación de rutas hijas para cada módulo del sistema:
    - Módulos reales: `/dashboard/usuarios` (`UsersView.vue`).
    - Módulos placeholders: vistas vacías con el nombre del módulo para Cooperativas, Rutas generales, Precios generales, Rutas de cooperativa, Buses, Turnos, Tarifas específicas, Reservas y Perfil.
  - Navigation Guard extendido en Vue Router para validar `meta.requiresRoles` en rutas protegidas.
- **Frontend — Directorio y Gestión de Usuarios**:
  - Módulo `users.service.ts` con tipado estricto para consumo de los endpoints de usuarios.
  - Store Pinia `users.store.ts` o composable para manejo de lista de usuarios, paginación, filtros de búsqueda con debounce y feedback de carga/error.
  - Vista `UsersView.vue`:
    - Tabla con tokens semánticos de Tailwind / shadcn-vue (sin emojis, usando `@lucide/vue`).
    - Columnas: Nombre completo, Correo electrónico, Rol(es) (badges), Estado (badge Activo/Inactivo), Fecha de registro y Acciones.
    - Modal de confirmación para dar de baja / habilitar usuario.
    - Modal selector múltiple de roles: checkbox "Pasajero" marcado y bloqueado (`disabled`) permanentemente.
    - Deshabilitación de botones de acción sobre la propia fila del usuario autenticado.
- **Pruebas Automatizadas Unitarias**:
  - Suite de pruebas unitarias en backend (pytest) cubriendo límites de paginación, búsquedas vacías, validación de schemas, auto-modificación denegada (403), idempotencia de roles y transiciones de estado.
  - Suite de pruebas unitarias en frontend (vitest) cubriendo renderizado condicional del menú según rol/combinación de roles, invariabilidad del rol pasajero, debounce de búsqueda y guards de navegación.

## Capabilities

### New Capabilities
- `module-access-by-role`: Renderizado condicional y dinámico de los módulos del menú lateral en base a los roles asignados al usuario autenticado, soportando roles únicos y combinados (RF-05).
- `user-directory`: Consulta paginada y filtrado por texto (nombre, apellido, email) del directorio de usuarios del sistema para el Administrador General.
- `user-role-assignment`: Asignación y revocación de roles secundarios desde interfaz administrativa con persistencia en base de datos, garantizando que el rol "Pasajero" sea permanente e inmutable (RF-07).
- `user-status-management`: Inactivación (borrado lógico) y rehabilitación de cuentas de usuario por parte del Administrador General, y rechazo de inicio de sesión con mensaje formal cuando la cuenta está inactiva (RF-08).

### Modified Capabilities
- `user-login`: Actualización del control de acceso para responder con el mensaje exacto `"Su cuenta se encuentra inactiva. Contacte al administrador"` si `is_active` es falso (CP-31). Adaptación de la respuesta de perfil para retornar lista de roles `roles: list[UserRole]`.
- `route-protection`: Soporte de autorización granular en backend (`require_role`) y frontend (router guard) para evaluar múltiples roles por usuario (`roles: UserRole[]`).

## Impact

- **Backend**:
  - Nueva migración Alembic (`create_user_roles_table_and_migrate_data`).
  - Modelos afectados: `User` (eliminación de columna `role`, incorporación de relación `roles`), nueva tabla `user_roles`.
  - Nuevo router `api/v1/users_router.py`, nuevo service `services/user_service.py`, repositorio actualizado `repositories/user_repository.py`.
  - Actualización de `schemas/user_schemas.py`, `core/permissions.py`, `core/dependencies.py` y `services/auth_service.py`.
- **Frontend**:
  - Actualización del tipo `User` en `services/auth.service.ts` (`roles: UserRole[]`).
  - Creación de `DashboardLayout.vue`, `UsersView.vue`, `DashboardHomeView.vue` y `ModulePlaceholderView.vue`.
  - Actualización de `router/index.ts` con rutas anidadas bajo `/dashboard/` y guard por roles.
  - Nuevos servicios y stores: `services/users.service.ts`, `stores/users.store.ts`.
- **Base de Datos**:
  - Modificación estructural: creación de tabla `user_roles(user_id, role)` con índice/PK compuesta, y drop de columna `users.role`.
- **Compatibilidad**:
  - Los usuarios existentes mantendrán su sesión válida o actualizarán su estado a `roles: ["PASAJERO"]` sin pérdida de datos.

