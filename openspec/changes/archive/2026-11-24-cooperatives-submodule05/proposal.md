# Proposal

## Why

El Submódulo 04 dejó registradas las cooperativas y sus administradores, pero en el dashboard las opciones "Rutas generales" y "Rutas de cooperativa" siguen siendo placeholders (`ModulePlaceholderView`). Sin rutas no se pueden construir buses, turnos, tarifas ni reservas, que dependen de una entidad Ruta común. Además, desactivar una ruta afecta a las cooperativas que la usan, por lo que el sistema necesita un canal de notificaciones (correo e in-app) que hoy no existe. El Submódulo 05 (`submodule05.md`) cubre:

1. **RF-12**: gestión de rutas generales por el `ADMIN_GENERAL`, con supervisión de solo lectura de las rutas específicas de cada cooperativa.
2. **RF-13**: gestión de rutas de cooperativa por el `ADMIN_COOPERATIVA` (adopción de rutas generales y rutas propias).
3. **RF-14**: notificaciones de la aplicación (icono en el encabezado y correo).

## What Changes

- **Base de datos (migración Alembic)**
  - `localities(id, name, created_at)` con índice único sobre `lower(name)`: catálogo vivo de localidades.
  - `routes(id, cooperativa_id NULL, origin_id, destination_id, name, distance_km, estimated_time_minutes, description, is_active, created_at, updated_at)`: modelo unificado. `cooperativa_id NULL` = ruta general; `NOT NULL` = ruta específica de esa cooperativa. `CHECK` de origen distinto de destino, distancia mayor a 0 y tiempo entre 1 y 1439 minutos. Índices únicos parciales sobre `(origin_id, destination_id, distance_km)` para generales y sobre `(cooperativa_id, origin_id, destination_id, distance_km)` para específicas.
  - `route_stops(id, route_id, locality_id, stop_order)` con `UNIQUE(route_id, stop_order)` y `UNIQUE(route_id, locality_id)`.
  - `cooperativa_general_routes(id, cooperativa_id, route_id, is_active)` con `UNIQUE(cooperativa_id, route_id)`: adopción de rutas generales y su interruptor Activa/Inactiva.
  - `notifications(id, user_id, title, message, is_read, created_at)` con índice `(user_id, created_at)`.
- **Localidades (catálogo vivo)**: búsqueda con autocompletado y creación inmediata desde el formulario de rutas, accesible para `ADMIN_GENERAL` y `ADMIN_COOPERATIVA`. Nombre sin espacios sobrantes (recorte automático) y único sin distinguir mayúsculas; si la búsqueda coincide con una existente se resalta y no se ofrece crear.
- **Rutas generales (RF-12)**
  - Endpoints bajo `/api/v1/rutas-generales` exclusivos de `ADMIN_GENERAL`: listado con filtros (origen, destino, estado), detalle, crear, editar y cambiar estado. Además, un listado de solo lectura de rutas específicas agrupadas por cooperativa.
  - Nombre = prefijo no editable `Origen - Destino` + texto adicional opcional (máx. 30). Descripción opcional (máx. 100). Distancia en km con decimales (> 0). Tiempo en horas y minutos en la interfaz, almacenado en minutos (> 0 y < 24 h). Paradas intermedias secuenciales (opción por defecto "Solo las de origen y destino"; si se desmarca, al menos una).
  - Origen distinto de destino; ninguna parada igual a origen/destino ni repetida. Unicidad por (origen, destino, distancia).
  - Con cooperativas o turnos asociados, Origen y Destino quedan bloqueados (frontend y backend).
  - Desactivación lógica con cascada sobre las adopciones de las cooperativas, notificación (in-app y correo) a los administradores activos de las cooperativas afectadas y auditoría. La reactivación no reactiva las adopciones.
  - Método documentado `check_active_trips_or_reservations()` como punto de enlace para los futuros módulos de turnos y reservas (hoy no encuentra elementos y no bloquea).
- **Rutas de cooperativa (RF-13)**
  - Endpoints bajo `/api/v1/cooperativas/mi-cooperativa/...` para `ADMIN_COOPERATIVA` (pertenencia y cooperativa activa validadas en backend): rutas generales adoptadas (listar, agregar desde el modal, interruptor Activa/Inactiva, solo reactivable si la ruta general sigue activa) y "Mis rutas" (crear, editar, activar/desactivar) con las mismas validaciones que las generales y unicidad limitada a la cooperativa.
  - Desactivar con turnos o reservas activas exige confirmación y notifica a los afectados (mediante el método documentado).
  - Cooperativa desactivada: se bloquea la gestión y se redirige al Inicio con "Por el momento, su cooperativa se encuentra desactivada"; la información se conserva.
- **Notificaciones (RF-14)**
  - `GET /api/v1/notificaciones` (paginado de 5 en 5, más recientes primero, con total de no leídas) y `PATCH /api/v1/notificaciones/leidas` (marcar todas). Cada usuario solo accede a las suyas.
  - Envío por correo con el `EmailSender` existente; un fallo de correo no revierte la operación ni la notificación in-app.
  - Campana en el encabezado del dashboard, visible para cualquier usuario autenticado: indicador de no leídas, popover con las 5 más recientes, "Marcar todas como leídas", "Cargar más" y estado vacío "No tienes notificaciones".
- **Auditoría**: se reutiliza `AuditService` para crear, editar, activar/desactivar rutas y adoptar rutas generales.
- **Frontend**
  - Vistas `RutasGeneralesView.vue` (reemplaza el placeholder `rutas-generales`) y `RutasCooperativaView.vue` (reemplaza el placeholder `rutas-cooperativa`); formulario de ruta reutilizable con combobox de localidades, paradas ordenadas y campos numéricos que bloquean caracteres no numéricos; modal de detalle de solo lectura; modal de adopción similar al de administradores. Componentes shadcn-vue, iconos `@lucide/vue`, tokens del tema Soft Pop, sin emojis.
  - Servicios `rutas.service.ts`, `localidades.service.ts` y `notificaciones.service.ts`, stores Pinia y composables; campana en `DashboardLayout.vue`.
- **Pruebas**: pytest (validadores, servicios, repositorios, routers, 403 por rol, aislamiento por cooperativa y por usuario, rechazo backend de Origen/Destino con asociaciones, adopción duplicada, unicidad de localidades) y vitest (validadores, stores, composables, componentes). Los escenarios marcados PENDIENTE en `submodule05.md` (CP-79, CP-81, CP-89) dependen de turnos y reservas; se implementa su lógica de rutas y notificaciones, y la parte de viajes y reservas queda en el método documentado.

## Capabilities

### New Capabilities
- `locality-catalog`: Catálogo vivo de localidades con búsqueda, creación inmediata y unicidad sin distinguir mayúsculas (RN-12.3, CP-77).
- `general-routes`: Registro, consulta, edición, baja lógica y reactivación de rutas generales con paradas secuenciales, unicidad, edición restringida y supervisión de solo lectura de rutas específicas (RF-12, CP-65 a CP-84).
- `cooperative-routes`: Adopción de rutas generales con interruptor Activa/Inactiva y gestión de rutas específicas por cooperativa, con aislamiento y bloqueo por cooperativa inactiva (RF-13, CP-85 a CP-98).
- `notifications`: Notificaciones in-app y por correo con campana en el encabezado, paginación de 5 en 5, marcado como leídas y estado vacío (RF-14, CP-99 a CP-104).

### Modified Capabilities
<!-- Ninguna: los menús "Rutas generales" y "Rutas de cooperativa" ya constan en module-access-by-role (CP-23, CP-24) y no cambian. -->

## Impact

- **Backend**
  - Nueva migración Alembic. Nuevos modelos: `Locality`, `Route`, `RouteStop`, `CooperativaGeneralRoute`, `Notification`.
  - Nuevos: repositorios, servicios (`locality_service`, `route_service`, `cooperativa_route_service`, `notification_service`), esquemas, validadores de ruta (distancia, tiempo, paradas, texto adicional), routers `localidades_router`, `rutas_generales_router`, `rutas_cooperativa_router` y `notificaciones_router`.
  - Modificados: `core/permissions.py` (`require_own_cooperativa` y reutilización de `require_active_cooperativa`), `services/email_service.py` (plantillas de aviso de ruta), `main.py` (routers) y `models/__init__.py`.
  - Sin dependencias nuevas previstas.
- **Frontend**: nuevas vistas, componentes, servicios y stores; cambios en `router/index.ts` (reemplazo de placeholders), `DashboardLayout.vue` (campana) y `useFormValidation.ts`.
- **Seguridad**: RBAC por rol y pertenencia a cooperativa verificada en backend; notificaciones aisladas por usuario; sin datos sensibles en logs ni correos.
- **Alcance excluido**: precios y tarifas de rutas (submódulo siguiente), turnos, buses y reservas (solo se deja el método de enlace y las notificaciones a pasajeros se activarán cuando existan).
