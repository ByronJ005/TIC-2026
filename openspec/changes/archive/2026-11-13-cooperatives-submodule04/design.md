# Design

## Context

Ver `proposal.md` (Why / What Changes) y las specs `cooperative-management` y `cooperative-administrators`. Estado actual del backend: capas `api/v1` → `services` → `repositories`, `core/permissions.py` con `require_role`, validadores reutilizables en `schemas/validators.py` (`validate_phone_format`, `validate_address_length`, `validate_email_format`, `is_blank`), usuarios con roles múltiples en `user_roles`. `python-multipart` ya está instalado. No existe infraestructura de auditoría ni entidad Cooperativa. El frontend usa Vue 3 + Pinia, `services/*.service.ts`, composables de formulario y un placeholder en `/dashboard/cooperativas`.

## Goals / Non-Goals

**Goals:**
- Entregar RF-09 y RF-10 respetando Router → Service → Repository y Component → Store/Composable → API Service.
- Garantizar en backend y base de datos las invariantes: RUC y nombre únicos, tope de 3 administradores, un usuario en una sola cooperativa.
- Dejar `users.cooperativa_id` y `require_active_cooperativa` listos para módulos futuros.

**Non-Goals:**
- Rutas, buses, turnos y tarifas de cooperativa.
- Almacenamiento externo de imágenes (S3, CDN), edición/recorte de imágenes.
- Consulta o reportes de auditoría (solo se escribe el registro).

## Decisions

1. **Vínculo usuario-cooperativa como columna `users.cooperativa_id`** (FK nullable, `ON DELETE SET NULL`, índice). Alternativa: tabla puente `cooperativa_admins`. Se elige la columna porque la regla es "una cooperativa por usuario" y `AGENTS.md` ya asume `current_user.cooperativa_id`; la exclusividad queda garantizada por el modelo sin constraint adicional.

2. **Asignación por reemplazo del conjunto** (`PUT /cooperativas/{id}/administradores` con `user_ids`, 0 a 3). Cubre CP-61 y CP-63 con un solo endpoint idempotente: el servicio calcula altas y bajas contra el conjunto actual. Alternativa: endpoints POST/DELETE por usuario; descartada porque el modal guarda el conjunto completo y evitaría estados intermedios inconsistentes.

3. **Concurrencia del tope de 3**: dentro de una transacción el servicio bloquea la fila de la cooperativa (`SELECT ... FOR UPDATE`), revalida cooperativa activa, elegibilidad de cada usuario (rol, activo, libre o ya asignado aquí) y `len(user_ids) <= 3`, y luego aplica altas y bajas. Dos asignaciones simultáneas a la misma cooperativa se serializan; una asignación del mismo usuario a dos cooperativas distintas se resuelve bloqueando también las filas de usuario involucradas (orden por id para evitar deadlocks).

4. **Elegibilidad calculada en repositorio** (`list_eligible_admins(cooperativa_id, search)`): usuarios con rol `ADMIN_COOPERATIVA`, `is_active`, y `cooperativa_id IS NULL OR = :id`; búsqueda por nombre, apellido y correo (`ILIKE`). Los asignados a la cooperativa actual aparecen preseleccionados.

5. **RUC ecuatoriano**: nuevo `validate_ruc` en `validators.py`. Estructura: 13 dígitos; provincia 01-24 o 30; tercer dígito 0-5 (persona natural, módulo 10 sobre cédula), 6 (público, módulo 11, sufijo ≥ 0001) o 9 (jurídica, módulo 11); los últimos 3 dígitos deben ser ≥ 001 (público ≥ 0001). Se separa el error de formato (longitud, no numérico) del error de algoritmo para mostrar los mensajes de CP-48 y CP-47. Es único y no se actualiza en `PUT`: `CooperativaUpdate` no contiene `ruc`, y los campos extra se ignoran.

6. **Nombre**: patrón `^[\p{L}\p{N} '\-]+$` (equivalente con `[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9 '-]`), recortado y con espacios internos colapsados. Unicidad con índice único sobre `lower(name)` y verificación previa en el servicio (el índice es el respaldo ante carreras). Los errores de validación siguen el formato de mensajes de las specs.

7. **Logo**: columna `logo_url` única. URL externa: se valida esquema `http/https` y longitud (≤ 500). Subida: `POST /cooperativas/{id}/logo` (multipart); un `LogoStorageService` valida el tipo real por firma de bytes (PNG, JPEG, WEBP), tamaño ≤ 2 MB, genera nombre `uuid4.ext`, guarda en `LOGO_UPLOAD_DIR` (variable de entorno) y guarda la ruta pública `/static/logos/<archivo>` en `logo_url`; el archivo anterior se elimina si era local. `main.py` monta `StaticFiles` en `/static/logos`. Alternativa descartada: guardar el binario en PostgreSQL, por peso y complejidad.

8. **Cooperativa inactiva**: el servicio lanza `CooperativaInactivaError` mapeada a HTTP 409 con `code: "COOPERATIVA_INACTIVA"` en edición, subida de logo y cambio de administradores. `PATCH /estado` es la única operación permitida sobre inactivas. El cliente Axios/fetch del frontend intercepta ese código, redirige a `/dashboard` y muestra "La cooperativa ha sido desactivada" (CP-60). Para administradores de cooperativa, `core/permissions.py` añade `require_active_cooperativa` (valida que `current_user.cooperativa_id` apunte a una cooperativa activa, 403 en caso contrario) para usarse en módulos futuros. Los módulos de Pasajero no lo usan, por lo que siguen accesibles.

9. **Auditoría**: tabla `audit_logs` y `AuditService.record(user_id, action, module, entity, entity_id, result)` invocado desde los servicios (nunca desde routers). Se registra éxito y fallo de crear, editar, cambiar estado y modificar administradores. No se guardan contraseñas, tokens ni cuerpos de solicitud.

10. **Capas y permisos**: `cooperativas_router.py` solo recibe, delega al servicio y devuelve DTOs (`CooperativaCreate`, `CooperativaUpdate`, `CooperativaEstadoUpdate`, `CooperativaResponse`, `CooperativaAdministradoresUpdate`, `AdministradorResponse`); nunca se devuelve el modelo ORM. Todos los endpoints usan `Depends(require_role("ADMIN_GENERAL"))` desde `permissions.py`; el 403 se cubre con pruebas unitarias.

11. **Frontend**: `CooperativasView.vue` con selector tabla/tarjetas persistido en el store; componentes `CooperativaCard`, `CooperativaTable`, `CooperativaFormDialog` (registro y edición, con RUC deshabilitado al editar), `CooperativaAdministratorsModal` (búsqueda con debounce, casillas con límite de 3). Lógica en `useCooperativaForm` y `useCooperativaAdministrators`; HTTP solo en `cooperativas.service.ts`. shadcn-vue (Dialog, Card, Table, Input, Checkbox, Badge, Button), iconos `@lucide/vue` (Settings, LayoutGrid, Table), tokens del tema; las tarjetas muestran un icono Lucide cuando no hay logo. Las validaciones de dirección, teléfono y correo reutilizan `useFormValidation.ts`.

## Risks / Trade-offs

- [Algoritmo de RUC incompleto para casos especiales] → Cubrir con pruebas de casos reales (natural, privada, pública) y documentar las reglas implementadas.
- [Archivos de logo huérfanos en disco al fallar una transacción] → Guardar el archivo después de validar y eliminarlo si el commit falla; limpiar el anterior solo tras éxito.
- [Almacenamiento local no escala ni persiste en despliegues efímeros] → Aceptable para el prototipo; el servicio aísla el almacenamiento para cambiarlo luego.
- [Bloqueos de filas pueden aumentar la espera en asignaciones simultáneas] → Operación administrativa de baja frecuencia; ordenar bloqueos por id.
- [`ON DELETE SET NULL` deja administradores libres si se borra una cooperativa] → No hay borrado físico; solo baja lógica.
- [Un `ADMIN_COOPERATIVA` sin cooperativa queda sin funciones operativas] → Comportamiento esperado (RN-10.4); se manejará en los módulos que usen `require_active_cooperativa`.

## Migration Plan

1. Migración Alembic: crear `cooperatives`, `audit_logs` y la columna `users.cooperativa_id` con FK e índices. Reversible (`downgrade` elimina en orden inverso).
2. Configurar `LOGO_UPLOAD_DIR` y `LOGO_MAX_SIZE_BYTES` en `.env` y `.env.example`.
3. Rollback: `alembic downgrade -1` y retirar el router; los usuarios existentes no se ven afectados.

