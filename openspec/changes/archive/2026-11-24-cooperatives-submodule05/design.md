# Design

## Context

Ver `proposal.md` (Why / What Changes) y las specs `locality-catalog`, `general-routes`, `cooperative-routes` y `notifications`. Estado actual: capas `api/v1` → `services` → `repositories`; `core/permissions.py` con `require_role` y `require_active_cooperativa`; `users.cooperativa_id`; `AuditService`; `EmailSender` (SMTP) en `services/email_service.py`; validadores en `schemas/validators.py`. En el frontend, `router/index.ts` ya declara `rutas-generales` (ADMIN_GENERAL) y `rutas-cooperativa` (ADMIN_COOPERATIVA) con `ModulePlaceholderView`, y `module-access-by-role` ya incluye ambos menús. El modal de administradores (`CooperativaAdministratorsModal`) sirve de referencia para el modal de adopción. No existen turnos, viajes ni reservas.

## Goals / Non-Goals

**Goals:**
- Entregar RF-12, RF-13 y RF-14 respetando Router → Service → Repository y Component → Store/Composable → API Service.
- Garantizar en backend y base de datos las invariantes: unicidad de ruta, unicidad de adopción, coherencia de paradas y aislamiento por cooperativa.
- Dejar un punto de enlace claro para turnos y reservas sin construirlos.

**Non-Goals:**
- Precios y tarifas, turnos, buses y reservas.
- Notificaciones en tiempo real (WebSocket/SSE) y colas de correo asíncronas externas.
- Administración (editar o eliminar) del catálogo de localidades.

## Decisions

1. **Tabla unificada `routes` con `cooperativa_id` nullable.** `NULL` = general, `NOT NULL` = específica (decisión acordada en exploración). Alternativa: tablas separadas; descartada porque buses, turnos y tarifas futuros referenciarán una sola entidad Ruta. Constraints: `CHECK (origin_id <> destination_id)`, `CHECK (distance_km > 0)`, `CHECK (estimated_time_minutes BETWEEN 1 AND 1439)`. Unicidad con dos índices únicos parciales: `(origin_id, destination_id, distance_km) WHERE cooperativa_id IS NULL` y `(cooperativa_id, origin_id, destination_id, distance_km) WHERE cooperativa_id IS NOT NULL`. `distance_km` es `Numeric(8,2)` para evitar errores de comparación de flotantes. El servicio verifica antes y traduce la violación de índice a error de dominio (respaldo ante carreras).

2. **Nombre persistido como `name` + `name_suffix`.** `name_suffix` (máx. 30, opcional, recortado) es lo que escribe el usuario; `name` se calcula siempre en el servicio como `"{origen} - {destino}"` o `"{origen} - {destino} {suffix}"`. Así el prefijo se regenera al cambiar Origen/Destino sin parsear texto. El cliente nunca envía `name`.

3. **Tiempo en minutos en la API.** El frontend convierte Horas/Minutos a `estimated_time_minutes` (1 a 1439) y viceversa al editar. Los minutos 0-59 se validan en el formulario; el backend valida el total. Distancia y tiempo se capturan con campos `inputmode="decimal"/"numeric"` que filtran caracteres no numéricos en el evento de entrada.

4. **Paradas en `route_stops` con `UNIQUE(route_id, stop_order)` y `UNIQUE(route_id, locality_id)`.** El cuerpo de la ruta recibe `stops: [{locality_id, stop_order}]` (vacío = "Solo las de origen y destino"). El servicio valida orden consecutivo desde 1, sin repetidos y distintos de Origen y Destino; la edición reemplaza el conjunto completo. La opción por defecto es estado de interfaz; el backend solo recibe la lista (una lista vacía es válida únicamente si el cliente marcó la opción; el formulario bloquea "desmarcada sin paradas", CP-72).

5. **Catálogo `localities` con `POST` idempotente.** Normalización en servicio: recorte y colapso de espacios; unicidad por índice único `lower(name)`. `POST /localidades` devuelve 201 al crear y 200 con la existente si ya existe (sin error), lo que cubre el caso de carreras y el envío directo por la API. `GET /localidades?search=` hace `ILIKE` ordenado por nombre y limitado. El combobox resalta la coincidencia exacta (comparación en minúsculas en cliente) y oculta "Crear y usar la nueva localidad" cuando existe. Accesible con `require_role("ADMIN_GENERAL", "ADMIN_COOPERATIVA")`.

6. **Adopción en `cooperativa_general_routes`.** `UNIQUE(cooperativa_id, route_id)`, `is_active`. Solo se adoptan rutas generales activas (`cooperativa_id IS NULL AND is_active`). El modal consume `GET /rutas-cooperativa/generales/disponibles`. El interruptor es `PATCH /rutas-cooperativa/generales/{adoption_id}/estado`; reactivar exige `route.is_active`, si no devuelve 409 con el mensaje de CP-91. No hay `DELETE`.

7. **Edición restringida: "tiene asociaciones".** Una ruta general las tiene si existe al menos una fila de adopción (activa o inactiva) o, a futuro, turnos. Se centraliza en `RouteService._has_associations(route)`, que consulta adopciones y el guard de viajes. Si las tiene, el servicio rechaza cambios de `origin_id`/`destination_id` (409). El mismo método aplica a rutas específicas con turnos (RN-13.7). El detalle de la ruta devuelve `has_associations` para que el formulario deshabilite Origen y Destino.

8. **Enlace con turnos y reservas: `TripReservationGuard`.** Interfaz mínima `check_active_trips_or_reservations(route_id) -> ActiveTripsReport` (cantidad de viajes y reservas, ids de usuarios afectados). La implementación actual, `NoopTripReservationGuard`, devuelve cero. `RouteService` lo recibe por inyección (`Depends`), de modo que al construir turnos y reservas solo se reemplaza la implementación. Cuando el reporte tenga elementos, el desactivar exige `confirm=true` en el cuerpo (el modal del frontend, CP-89) y se notifica a los usuarios afectados.

9. **Desactivación en cascada transaccional.** `RouteService.update_estado` bloquea la fila de la ruta (`SELECT ... FOR UPDATE`), desactiva la ruta y todas sus filas de adopción en la misma transacción, y recoge los administradores activos (`users.cooperativa_id` de las cooperativas afectadas, rol `ADMIN_COOPERATIVA`, `is_active`). Tras el `COMMIT` invoca a `NotificationService`. La reactivación solo cambia la ruta; las adopciones permanecen inactivas.

10. **Notificaciones: tabla + servicio, correo tolerante a fallos.** `notifications(id, user_id FK, title, message, is_read, created_at)` con índice `(user_id, created_at DESC)`. `NotificationService.notify_users(user_ids, title, message)` crea las filas en una transacción propia y luego intenta el correo por usuario con `EmailSender`; `EmailDeliveryError` se captura, se registra solo el tipo de excepción (patrón de `email_service.py`) y nunca revierte la operación ni la notificación in-app (CP-104). Alternativa: tarea en segundo plano con cola; descartada por sobredimensionada para el prototipo (se usará `BackgroundTasks` de FastAPI solo si el envío bloquea la respuesta de forma perceptible). Endpoints: `GET /notificaciones?page=&size=5` (respuesta con `items`, `unread_count`, `has_more`; `size` máximo 5 en la interfaz) y `PATCH /notificaciones/leidas`. El `user_id` siempre sale del token, nunca de la solicitud, lo que impide acceder a notificaciones ajenas.

11. **Permisos y pertenencia (`permissions.py`).** Los endpoints de `ADMIN_COOPERATIVA` usan `Depends(require_role("ADMIN_COOPERATIVA"))` más `require_active_cooperativa`; la cooperativa se toma de `current_user.cooperativa_id`, nunca de la solicitud. Se añade `require_own_cooperativa` (centralizado) y el servicio carga cada recurso con `WHERE cooperativa_id = :user_coop`; si el recurso existe pero es de otra cooperativa devuelve 403 (no 404) según RN-13.1. `require_active_cooperativa` para cooperativas inactivas pasa a incluir `code: "COOPERATIVA_ASIGNADA_INACTIVA"` en el detalle del 403; el cliente HTTP lo intercepta, redirige a `/dashboard` y muestra "Por el momento, su cooperativa se encuentra desactivada" (CP-98). La redirección por acceso a una ruta ajena mediante URL (CP-97) se resuelve en la vista: ante 403 al cargar el detalle, redirige a `/dashboard`.

12. **Supervisión del Administrador General.** `GET /rutas-generales` (solo generales, filtros `origin_id`, `destination_id`, `is_active`, paginado) y `GET /rutas-generales/especificas` (rutas específicas agrupadas por cooperativa, solo lectura, sin endpoints de escritura para `ADMIN_GENERAL` sobre ellas). `GET /rutas/{id}` devuelve el detalle (paradas ordenadas) tanto para generales como específicas, con autorización: `ADMIN_GENERAL` cualquiera; `ADMIN_COOPERATIVA` solo generales adoptadas o específicas propias.

13. **Auditoría desde servicios.** `AuditService.record(...)` con acciones `CREATE_ROUTE`, `UPDATE_ROUTE`, `ACTIVATE_ROUTE`, `DEACTIVATE_ROUTE`, `ADOPT_ROUTE`, `TOGGLE_ADOPTION`, módulo `RUTAS`, entidad `ROUTE`/`COOPERATIVA_GENERAL_ROUTE`; éxito y fallo; sin datos sensibles.

14. **Frontend.** `RutasGeneralesView.vue` (listado con filtros, tabla, `RouteFormDialog`, `RouteDetailDialog`, sección de rutas específicas por cooperativa en acordeón/secciones) y `RutasCooperativaView.vue` (secciones "Rutas generales" con interruptor y "Mis rutas"; `GeneralRoutesPickerModal` basado en el patrón de `CooperativaAdministratorsModal`). Componentes compartidos: `LocalityCombobox.vue`, `RouteStopsEditor.vue`, `RouteTimeInput.vue`. Lógica en composables `useRouteForm`, `useLocalities` y `useRoutes`; HTTP solo en `rutas.service.ts`, `localidades.service.ts` y `notificaciones.service.ts`; stores `rutas.store.ts` y `notificaciones.store.ts`. `NotificationBell.vue` en `DashboardLayout.vue` carga el contador al montar y la lista al abrir el popover (sin polling). Se usan shadcn-vue (Dialog, Popover, Select/Command, Switch, Badge, Table, Checkbox), iconos `@lucide/vue` (Bell, Settings, Eye, Plus) y tokens Soft Pop, sin emojis ni colores fijos, compatible con modo claro y oscuro.

## Risks / Trade-offs

- [Unicidad con `distance_km` decimal] → `Numeric(8,2)` y normalización a dos decimales en el esquema antes de comparar.
- [Cascada de desactivación con muchas cooperativas] → Operación administrativa de baja frecuencia; un solo `UPDATE` por conjunto y envío de correos después del `COMMIT`.
- [El envío de correo puede ser lento y bloquear la respuesta] → Timeout SMTP existente de 15 s; se captura cada fallo; se pasa a `BackgroundTasks` si resulta perceptible.
- [Carrera al crear la misma localidad] → Índice único `lower(name)` y reintento que devuelve la existente.
- [Reglas dependientes de turnos y reservas sin tablas] → `TripReservationGuard` con implementación nula y pruebas con un guard simulado que devuelve elementos, para validar el modal de confirmación y la notificación (CP-79, CP-81 y CP-89 quedan completos al integrar turnos).
- [Catálogo de localidades con duplicados semánticos (tildes, abreviaturas)] → Fuera de alcance; se mitiga con búsqueda y resaltado antes de crear.
- [Notificaciones sin tiempo real] → Aceptable para el prototipo; el contador se actualiza al montar y al abrir el popover.

## Migration Plan

1. Migración Alembic: crear `localities`, `routes`, `route_stops`, `cooperativa_general_routes`, `notifications` con FKs, checks e índices (incluidos los únicos parciales). Reversible (`downgrade` en orden inverso).
2. Sin variables de entorno nuevas; se reutiliza la configuración SMTP existente.
3. Rollback: `alembic downgrade -1` y retirar los routers; no afecta datos de submódulos anteriores.
