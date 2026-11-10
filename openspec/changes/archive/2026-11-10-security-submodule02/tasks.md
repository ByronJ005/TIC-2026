## 1. Migración y Modelos de Base de Datos

- [x] 1.1 Actualizar enum `UserRole` en `backend/src/models/user.py` para incluir `ADMIN_GENERAL`, `ADMIN_COOPERATIVA`, `SECRETARIA_COOPERATIVA` y `PASAJERO`.
- [x] 1.2 Crear el modelo de asociación `UserRoleAssociation` o tabla secundaria `user_roles(user_id, role)` con llave primaria compuesta y llave foránea con borrado en cascada.
- [x] 1.3 Actualizar el modelo `User` en `backend/src/models/user.py`: retirar la columna individual `role` y configurar la relación `roles` como colección de roles.
- [x] 1.4 Generar migración Alembic que cree la tabla `user_roles`, migre los roles de los usuarios existentes asignándoles `PASAJERO` (y su rol previo mapeado), y elimine la columna antigua `role` de la tabla `users`.
- [x] 1.5 Ejecutar la migración con `alembic upgrade head` y verificar la integridad de la base de datos.

## 2. Schemas Pydantic y Validaciones Backend

- [x] 2.1 Actualizar `UserResponse` en `backend/src/schemas/user_schemas.py` para exponer `roles: list[UserRole]` en lugar de un único `role`.
- [x] 2.2 Crear schema `UserRolesUpdate` en `backend/src/schemas/user_schemas.py` para la asignación de roles, validando que el listado contenga roles válidos del enum y garantizando que `PASAJERO` no se duplique.
- [x] 2.3 Crear schema `UserStatusUpdate` en `backend/src/schemas/user_schemas.py` para actualizar `is_active: bool`.
- [x] 2.4 Crear schema `UserPaginationResponse` con metadatos: `items: list[UserResponse]`, `total: int`, `page: int`, `size: int`, `pages: int`.
- [x] 2.5 Crear schema de parámetros de consulta con validadores de rango para `page >= 1` y `1 <= size <= 100`.

## 3. Repositorio y Servicios de Acceso a Datos

- [x] 3.1 Actualizar `UserRepository` en `backend/src/repositories/user_repository.py` para cargar ansiosamente (`joinedload` / `selectinload`) los roles del usuario en consultas por ID y por email.
- [x] 3.2 Añadir método `list_users` en `UserRepository` con soporte para filtros de búsqueda insensible (`ILIKE` sobre `first_name`, `last_name`, `email`), filtro `include_inactive`, paginación (`offset`, `limit`) y cálculo de `count` total.
- [x] 3.3 Añadir métodos `update_roles(user_id, roles)` y `update_status(user_id, is_active)` en `UserRepository`.
- [x] 3.4 Crear servicio `UserService` en `backend/src/services/user_service.py`:
  - Lógica de obtención y paginación de usuarios.
  - Asignación de roles forzando la inclusión del rol `PASAJERO` de forma obligatoria e inmutable.
  - Validación de auto-protección: rechazar con `HTTP 403 Forbidden` si `current_user.id == target_user_id` al cambiar roles o estado.
  - Validación de transiciones de estado: rechazar con `HTTP 400 Bad Request` si se intenta desactivar una cuenta ya inactiva o activar una ya activa.

## 4. Autorización y Endpoints API

- [x] 4.1 Actualizar `require_role(*roles)` en `backend/src/core/permissions.py` para verificar si la intersección entre los roles del usuario (`current_user.roles`) y los roles permitidos no es vacía; retornar `HTTP 403 Forbidden` en caso contrario.
- [x] 4.2 Ajustar `login_user` en `backend/src/services/auth_service.py` para retornar el mensaje exacto `"Su cuenta se encuentra inactiva. Contacte al administrador"` cuando `is_active` sea falso (cumplimiento estricto de CP-31).
- [x] 4.3 Actualizar `create_access_token` en `backend/src/core/security.py` para no requerir rol estático en el payload del JWT (roles siempre resueltos desde DB).
- [x] 4.4 Crear router `backend/src/api/v1/users_router.py` bajo el prefijo `/api/v1/usuarios`:
  - `GET /`: Listar usuarios con paginación y búsqueda (protegido con `require_role("ADMIN_GENERAL")`).
  - `PUT /{user_id}/roles`: Asignar roles a usuario (protegido con `require_role("ADMIN_GENERAL")`).
  - `PATCH /{user_id}/estado`: Cambiar estado activo/inactivo (protegido con `require_role("ADMIN_GENERAL")`).
- [x] 4.5 Registrar `users_router` en `backend/src/main.py`.

## 5. Pruebas Unitarias Backend (pytest)

- [x] 5.1 Crear `backend/tests/unit/test_user_service.py` con pruebas unitarias aisladas:
  - Búsqueda sin coincidencias retorna lista vacía sin error.
  - Consulta con página fuera de rango retorna lista vacía y metadatos correctos.
  - Asignación de lista de roles sin "PASAJERO" fuerza la inclusión de `PASAJERO`.
  - Intento de auto-desactivación de la cuenta de admin lanza excepción 403.
  - Intento de auto-modificación de roles de la cuenta de admin lanza excepción 403.
  - Desactivación de usuario ya inactivo lanza excepción 400.
  - Activación de usuario ya activo lanza excepción 400.
  - Modificación de usuario inexistente lanza excepción 404.
- [x] 5.2 Crear `backend/tests/unit/test_permissions.py` para evaluar el dependency `require_role` con combinaciones de roles múltiples y denegaciones 403.
- [x] 5.3 Actualizar tests existentes de autenticación en `backend/tests/` para verificar compatibilidad con el nuevo formato de roles.

## 6. Frontend — Modelos, Servicios y Store

- [x] 6.1 Actualizar interfaz `User` y tipos en `frontend/src/services/auth.service.ts`: cambiar `role: UserRole` por `roles: UserRole[]` y actualizar el enum a `SECRETARIA_COOPERATIVA`.
- [x] 6.2 Crear servicio `frontend/src/services/users.service.ts` con funciones tipadas: `getUsers(params)`, `updateUserRoles(id, roles)`, `updateUserStatus(id, isActive)`.
- [x] 6.3 Crear store `frontend/src/stores/users.store.ts` (Pinia) o composable de gestión:
  - Estado reactivo para listado, metadatos de paginación (`page`, `size`, `total`, `pages`), indicador `isLoading`, texto de búsqueda `searchQuery` y filtro `includeInactive`.
  - Acción de búsqueda con debounce para evitar saturación de peticiones.
  - Acciones para actualizar roles y alternar estado con refresco local y notificaciones.
- [x] 6.4 Actualizar `frontend/src/stores/auth.store.ts` para gestionar `user.roles` correctamente.

## 7. Frontend — Layout Modular y Rutas de Navegación

- [x] 7.1 Crear vista de módulo no construido `frontend/src/views/ModulePlaceholderView.vue` que renderice el nombre del módulo en un contenedor limpio con diseño Soft Pop.
- [x] 7.2 Crear vista de bienvenida `frontend/src/views/DashboardHomeView.vue` extrayendo el contenido hero y tarjetas de perfil actuales de `DashboardView.vue`.
- [x] 7.3 Crear componente de layout `frontend/src/views/DashboardLayout.vue`:
  - Barra superior con marca BoletoYa, badge de usuario (mostrando sus roles principales) y botón de cierre de sesión con diálogo de confirmación.
  - Barra lateral de navegación (Sidebar) que calcula los módulos permitidos según `authStore.user?.roles`:
    - `ADMIN_GENERAL`: Usuarios, Cooperativas, Rutas generales.
    - `ADMIN_COOPERATIVA`: Rutas de cooperativa, Buses, Turnos, Tarifas específicas.
    - `SECRETARIA_COOPERATIVA`: Reservas, Informes.
    - `PASAJERO`: Reservas, Perfil.
    - Combinados: Unión matemática de los módulos permitidos.
  - Iconos de `@lucide/vue` temáticos para cada opción de menú (sin emojis).
  - Área principal con `<RouterView>` para mostrar la vista hija activa.
- [x] 7.4 Actualizar `frontend/src/router/index.ts`:
  - Configurar `/dashboard` como ruta con layout shell y rutas hijas para `/dashboard/usuarios`, `/dashboard/cooperativas`, `/dashboard/rutas-generales`, `/dashboard/rutas-cooperativa`, `/dashboard/buses`, `/dashboard/turnos`, `/dashboard/tarifas`, `/dashboard/reservas`, `/dashboard/informes`, `/dashboard/perfil`.
  - Incorporar en el global guard la validación de `to.meta.requiresRoles`: si el usuario no cuenta con ninguno de los roles exigidos por la ruta hija, redirigir a `/dashboard`.

## 8. Frontend — Vista de Gestión de Usuarios

- [x] 8.1 Crear `frontend/src/views/UsersView.vue`:
  - Encabezado con título del módulo, descripción breve y buscador reactivo con icono `Search`.
  - Tabla de usuarios estilizada con clases de Tailwind semánticas (`bg-card`, `border-border`, `text-card-foreground`).
  - Columnas: Nombre completo, Email, Roles (Badges), Estado (Badge verde Activo / rojo Inactivo), Fecha de registro (DD/MM/AAAA) y Acciones.
  - Controles de paginación: Botones Anterior / Siguiente, indicador de página actual y total de registros.
  - Botones en fila: "Asignar rol" (icono `SlidersHorizontal` o `Shield`) y "Dar de baja" / "Habilitar" (icono `UserX` / `UserCheck`).
  - Deshabilitar ambos botones para la fila correspondiente al usuario actualmente autenticado (`user.id === authStore.user?.id`).
- [x] 8.2 Implementar diálogo modal de Asignación de Roles:
  - Lista de checkboxes para `ADMIN_GENERAL`, `ADMIN_COOPERATIVA`, `SECRETARIA_COOPERATIVA` y `PASAJERO`.
  - Checkbox de `PASAJERO` obligatoriamente marcado y deshabilitado (`disabled`).
  - Botones Cancelar y Guardar cambios con estado de carga.
- [x] 8.3 Implementar diálogo modal de Confirmación de Baja / Habilitación:
  - Mensaje explicativo sobre las consecuencias de la acción.
  - Botón de confirmación destructivo para baja o primario para habilitación.

## 9. Pruebas Unitarias Frontend (Vitest)

- [x] 9.1 Crear `frontend/src/__tests__/DashboardLayout.spec.ts`:
  - Verificar que un usuario con `roles: ["ADMIN_GENERAL"]` renderiza exactamente los 3 módulos correspondientes.
  - Verificar que un usuario con `roles: ["ADMIN_COOPERATIVA"]` renderiza los 4 módulos correspondientes.
  - Verificar que un usuario con `roles: ["SECRETARIA_COOPERATIVA"]` renderiza los 2 módulos correspondientes.
  - Verificar que un usuario con `roles: ["PASAJERO"]` renderiza los 2 módulos correspondientes.
  - Verificar que un usuario con roles combinados (`["ADMIN_COOPERATIVA", "PASAJERO"]`) renderiza la unión de 6 módulos exactos.
- [x] 9.2 Crear `frontend/src/__tests__/UsersView.spec.ts`:
  - Verificar que los botones de acción se deshabilitan en la fila del propio usuario logueado.
  - Verificar que el checkbox de "Pasajero" en el modal de asignación permanece inmutable y marcado.
  - Verificar que la búsqueda dispara la petición con debounce y resetea la página a 1.
- [x] 9.3 Actualizar `frontend/src/__tests__/router.spec.ts` para verificar la protección de rutas por roles específicos.

## 10. Verificación Integral y Criterios de Aceptación (CPs)

- [x] 10.1 Ejecutar suite completa de tests de backend con `pytest` y confirmar que pasan todas las pruebas (0 fallos).
- [x] 10.2 Ejecutar suite completa de tests de frontend con `npm run test:unit` y verificar aprobación del 100%.
- [x] 10.3 Ejecutar verificación de linter y tipos con `npm run lint`.
- [x] 10.4 Validar cumplimiento de escenarios manuales CP-23 a CP-32 de `submodule02.md`.

## 11. Ajustes de Navegación, Módulos y Sidebar Responsive

- [x] 11.1 Actualizar configuración de rutas en `frontend/src/router/index.ts`: añadir ruta `/dashboard/precios-generales` con rol `ADMIN_GENERAL` y retirar `/dashboard/informes`.
- [x] 11.2 Actualizar lista de módulos en `frontend/src/views/DashboardLayout.vue`: añadir "Precios generales" para `ADMIN_GENERAL` y retirar "Informes" de `SECRETARIA_COOPERATIVA`.
- [x] 11.3 Implementar funcionalidad de contracción y expansión (toggle) del sidebar de escritorio en `DashboardLayout.vue`, alternando entre ancho estándar con etiquetas y vista compacta de iconos.
- [x] 11.4 Implementar soporte responsive para pantallas móviles (< md) en `DashboardLayout.vue`: botón de menú hamburguesa en el header superior y drawer desplegable con backdrop para acceder a los módulos autorizados en dispositivos móviles.
- [x] 11.5 Actualizar pruebas unitarias en `frontend/src/__tests__/DashboardLayout.spec.ts` para verificar la presencia de "Precios generales" en ADMIN_GENERAL y que SECRETARIA_COOPERATIVA tenga únicamente "Reservas".

