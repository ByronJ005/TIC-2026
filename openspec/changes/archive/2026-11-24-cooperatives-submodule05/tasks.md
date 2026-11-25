# Tasks

## 1. Base de datos y modelos

- [x] 1.1 Crear modelos `Locality`, `Route`, `RouteStop`, `CooperativaGeneralRoute` y `Notification` con sus constraints (checks, únicos, índices únicos parciales) y exportarlos en `models/__init__.py`. Verificar con `python -c "import src.models"`.
- [x] 1.2 Crear migración Alembic con las cinco tablas, FKs e índices (incluidos los únicos parciales de rutas generales y específicas). Verificar con `alembic upgrade head` y `alembic downgrade -1` sin errores.

## 2. Validadores y esquemas

- [x] 2.1 Implementar validadores de ruta en `schemas/validators.py` (normalización de localidad, texto adicional ≤ 30, descripción ≤ 100, distancia > 0 con dos decimales, tiempo 1 a 1439 minutos, paradas consecutivas sin repetidos). Verificar con pruebas pytest de límites y casos inválidos (CP-67, CP-72 a CP-74).
- [x] 2.2 Crear `schemas/route_schemas.py`, `locality_schemas.py` y `notification_schemas.py` (DTOs de creación, actualización, estado, detalle, listados, adopciones, paginación de notificaciones) sin devolver modelos ORM. Verificar con pruebas de esquemas.

## 3. Localidades (locality-catalog)

- [x] 3.1 Implementar `LocalityRepository` y `LocalityService` (búsqueda `ILIKE`, creación idempotente con normalización y unicidad `lower(name)`). Verificar con pruebas: crear, duplicado con otra capitalización y espacios, vacío y solo espacios (CP-77).
- [x] 3.2 Crear `localidades_router.py` (`GET` y `POST` bajo `/api/v1/localidades`) con `require_role("ADMIN_GENERAL", "ADMIN_COOPERATIVA")` y registrarlo en `main.py`. Verificar con pruebas de router: 200/201, 401, 403 para `PASAJERO` y `SECRETARIA_COOPERATIVA`.

## 4. Notificaciones (notifications)

- [x] 4.1 Implementar `NotificationRepository` y `NotificationService` (crear en lote, listar paginado de 5 en 5 con `unread_count` y `has_more`, marcar todas como leídas del usuario). Verificar con pruebas de CP-99 a CP-102.
- [x] 4.2 Añadir el envío de correo tolerante a fallos usando `EmailSender` y plantillas de aviso de ruta desactivada. Verificar con pruebas con un `EmailSender` simulado que falla: la notificación in-app se conserva y el error no revierte la operación (CP-104).
- [x] 4.3 Crear `notificaciones_router.py` (`GET /notificaciones`, `PATCH /notificaciones/leidas`) para cualquier usuario autenticado y registrarlo en `main.py`. Verificar con pruebas de router, incluyendo que un usuario nunca accede a las notificaciones de otro.

## 5. Rutas generales (general-routes)

- [x] 5.1 Implementar `RouteRepository` y `RouteStopRepository` (crear, obtener con paradas, listar generales con filtros y paginación, listar específicas agrupadas por cooperativa, existe combinación única con ámbito, bloqueo `FOR UPDATE`). Verificar con pruebas de repositorio.
- [x] 5.2 Implementar `TripReservationGuard` (interfaz y `NoopTripReservationGuard`) con `check_active_trips_or_reservations()` documentado. Verificar con prueba de que devuelve cero y con un guard simulado que devuelve elementos.
- [x] 5.3 Implementar `RouteService` para rutas generales: crear (nombre = prefijo + texto adicional, paradas, unicidad, Origen distinto de Destino), editar con `_has_associations` (rechazar cambio de Origen/Destino con asociaciones), detalle y auditoría. Verificar con pruebas de CP-65, CP-66, CP-68 a CP-72, CP-75, CP-76, CP-78 y el rechazo backend de CP-79.
- [x] 5.4 Implementar cambio de estado con cascada transaccional sobre adopciones, notificación a administradores activos de las cooperativas afectadas tras el `COMMIT`, confirmación `confirm=true` cuando el guard reporte viajes/reservas y auditoría. Verificar con pruebas de CP-80 a CP-82, CP-103 y que la reactivación no reactiva adopciones.
- [x] 5.5 Crear `rutas_generales_router.py` (`GET`, `GET /{id}`, `POST`, `PUT /{id}`, `PATCH /{id}/estado`, `GET /especificas`) con `require_role("ADMIN_GENERAL")`, registrarlo en `main.py` y exponer el detalle `GET /rutas/{id}` con la autorización de la decisión 12. Verificar con pruebas de router: éxito, 401, 403 para los demás roles, 409 por duplicado y edición restringida, 422 de validación, filtros (CP-83) y listado de específicas (CP-84).

## 6. Rutas de cooperativa (cooperative-routes)

- [x] 6.1 Implementar `CooperativaGeneralRouteRepository` y la lógica de adopción en `CooperativaRouteService` (listar adoptadas, listar disponibles activas no adoptadas, adoptar múltiples, interruptor con regla de ruta general activa, auditoría). Verificar con pruebas de CP-85 a CP-91, adopción duplicada rechazada y modificación de datos de ruta general rechazada.
- [x] 6.2 Implementar en `CooperativaRouteService` las rutas específicas (crear, editar, activar/desactivar con confirmación y guard, unicidad por cooperativa, Origen/Destino bloqueados con turnos). Verificar con pruebas de CP-92 a CP-96.
- [x] 6.3 Añadir `require_own_cooperativa` a `core/permissions.py` y el código `COOPERATIVA_ASIGNADA_INACTIVA` al 403 de `require_active_cooperativa`. Verificar con pruebas de permisos: recurso de otra cooperativa y cooperativa inactiva reciben 403 (CP-97, CP-98).
- [x] 6.4 Crear `rutas_cooperativa_router.py` bajo `/api/v1/rutas-cooperativa` con `require_role("ADMIN_COOPERATIVA")` y `require_active_cooperativa`, registrarlo en `main.py`. Verificar con pruebas de router: éxito, 401, 403 por rol y por pertenencia, 403 con cooperativa inactiva y 409 de duplicados.
- [x] 6.5 Ejecutar `pytest` completo. Verificar que pasan las pruebas nuevas y existentes.

## 7. Frontend: base

- [x] 7.1 Crear `localidades.service.ts`, `rutas.service.ts` y `notificaciones.service.ts` con tipos TypeScript estrictos. Verificar con pruebas vitest con cliente simulado.
- [x] 7.2 Extender el cliente HTTP para interceptar `COOPERATIVA_ASIGNADA_INACTIVA` (redirigir a `/dashboard` con "Por el momento, su cooperativa se encuentra desactivada") y el 403 al abrir una ruta ajena (redirigir a `/dashboard`). Verificar con pruebas del interceptor (CP-97, CP-98).
- [x] 7.3 Añadir a `useFormValidation.ts` los validadores de ruta (obligatorios, Origen distinto de Destino, paradas, distancia, tiempo, límites de 30 y 100) con los mensajes de las specs. Verificar con pruebas vitest equivalentes a las del backend.
- [x] 7.4 Crear stores Pinia (`rutas.store.ts`, `notificaciones.store.ts`) y composables `useRouteForm`, `useLocalities` (debounce, recorte de espacios, resaltado de coincidencia exacta) y `useRoutes`. Verificar con pruebas de store y composables.

## 8. Frontend: interfaz

- [x] 8.1 Instalar los componentes shadcn-vue que falten (Popover, Command/Combobox, Switch, Tabs o Accordion) sin añadir librerías ajenas. Verificar con `npm run lint`.
- [x] 8.2 Implementar `LocalityCombobox.vue`, `RouteStopsEditor.vue` y `RouteTimeInput.vue` (campos numéricos que bloquean caracteres no numéricos; opción "Solo las de origen y destino" marcada por defecto). Verificar con pruebas de componente de CP-69 a CP-74 y CP-77 (incluido el resaltado sin botón de crear).
- [x] 8.3 Implementar `RouteFormDialog.vue` (prefijo de nombre no editable, texto adicional, descripción, Origen/Destino deshabilitados con asociaciones) y `RouteDetailDialog.vue` (solo lectura). Verificar con pruebas de componente de CP-65 a CP-67, CP-78 y CP-79.
- [x] 8.4 Implementar `RutasGeneralesView.vue` (listado con filtros, activar/desactivar con diálogo de confirmación, sección de rutas específicas por cooperativa en solo lectura) y reemplazar el placeholder `rutas-generales` en `router/index.ts`. Verificar con pruebas de componente de CP-80 a CP-84.
- [x] 8.5 Implementar `RutasCooperativaView.vue` (secciones "Rutas generales" y "Mis rutas", interruptor con confirmación, `GeneralRoutesPickerModal` con selección múltiple) y reemplazar el placeholder `rutas-cooperativa`. Verificar con pruebas de componente de CP-85 a CP-96.
- [x] 8.6 Implementar `NotificationBell.vue` en `DashboardLayout.vue` (indicador de no leídas, 5 más recientes, "Marcar todas como leídas", "Cargar más", estado vacío "No tienes notificaciones"). Verificar con pruebas de componente de CP-99 a CP-102.
- [x] 8.7 Revisar tokens del tema, modo claro/oscuro, ausencia de emojis y colores fijos, iconos solo de `@lucide/vue` y responsive. Verificar con `npm run lint` y revisión visual en ambos modos.

## 9. Integración

- [x] 9.1 Ejecutar `npm run test:unit` y `npm run lint`. Verificar que no hay fallas ni errores de tipos.
- [x] 9.2 Recorrer manualmente: registrar ruta general con y sin paradas, crear localidad, adoptar desde otra cooperativa, desactivar la ruta general y revisar notificación y correo, probar interruptor y rutas propias, y cooperativa desactivada. Verificar cada resultado contra CP-65 a CP-104.


## 10. Mejoras

- [x] 10.1 Unificar el contrato entre RouteFormDialog.vue y useRouteForm.ts.
- [x] 10.2 Unificar y tipar las claves de errores y revalidar dependencias entre paradas.
- [x] 10.3 Implementar reordenamiento de paradas y tipos de datos en envío.
- [x] 10.4 Capturar errores de envío con useRouteSubmission y mostrarlos dentro del modal.
- [x] 10.5 Mostrar advertencia en combobox de localidades para desambiguar cantones entre paréntesis.
- [x] 10.6 Añadir título de sección Recorrido sobre la casilla de solo origen y destino.
- [x] 10.7 Restringir en frontend dígitos numéricos y ampliar límite de tiempo hasta 99h 59m.
- [x] 10.8 Mostrar dinámicamente el nombre real de la cooperativa en Mis Rutas.
- [x] 10.9 Incorporar modal de confirmación previo a la reactivación de rutas generales y propias.
- [x] 10.10 Gestionar cooperativa desactivada ocultando secciones y mostrando aviso informativo sin errores confusos.
