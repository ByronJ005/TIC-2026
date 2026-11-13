# Tasks

## 1. Base de datos y modelos

- [x] 1.1 Crear modelos `Cooperativa` y `AuditLog`, y añadir `cooperativa_id` a `User`; exportarlos en `models/__init__.py`. Verificar con `python -c "import src.models"`.
- [x] 1.2 Crear migración Alembic (`cooperatives` con `UNIQUE(ruc)`, índice único `lower(name)` y checks; `audit_logs`; `users.cooperativa_id` FK `SET NULL` indexada). Verificar con `alembic upgrade head` y `alembic downgrade -1` sin errores.
- [x] 1.3 Añadir `LOGO_UPLOAD_DIR` y `LOGO_MAX_SIZE_BYTES` a `core/config.py` y `.env.example`. Verificar que `settings` los carga con valores por defecto.

## 2. Validadores

- [x] 2.1 Implementar `validate_ruc` (formato y algoritmo módulos 10 y 11) y `validate_cooperativa_name` en `schemas/validators.py`. Verificar con pruebas pytest de RUC natural, privado, público, longitud, no numérico, dígito verificador y provincia inválidos; nombre con números, guion, apóstrofe, símbolo inválido, vacío y 100/101 caracteres.

## 3. Repositorios y auditoría

- [x] 3.1 Implementar `CooperativaRepository` (crear, obtener, listar paginado con búsqueda, existe por RUC y por nombre `lower`, actualizar, bloqueo `FOR UPDATE`). Verificar con pruebas de repositorio.
- [x] 3.2 Ampliar `UserRepository`/crear métodos para administradores: listar elegibles con búsqueda, obtener asignados, bloquear usuarios por id y asignar/desvincular. Verificar con pruebas: solo activos, con rol, libres o de la propia cooperativa.
- [x] 3.3 Implementar `AuditService` y su repositorio. Verificar con prueba que guarda usuario, acción, módulo, entidad y resultado sin datos sensibles.

## 4. Servicios y esquemas (RF-09)

- [x] 4.1 Crear `schemas/cooperativa_schemas.py` (DTOs de creación, actualización sin RUC, estado, respuesta, lista paginada) reutilizando los validadores de dirección, teléfono y correo. Verificar con pruebas de esquemas, incluyendo nombre vacío al editar y RUC ignorado en actualización.
- [x] 4.2 Implementar `CooperativaService` (crear, listar, obtener, editar, cambiar estado, unicidad de RUC y nombre, error de cooperativa inactiva, auditoría). Verificar con pruebas de CP-46 a CP-53, CP-55 a CP-60 y la inmutabilidad del RUC.
- [x] 4.3 Implementar `LogoStorageService` (URL http/https, firma PNG/JPEG/WEBP, 2 MB, nombre generado, eliminación del anterior). Verificar con pruebas de archivo válido, tipo falso, exceso de tamaño y URL inválida.

## 5. Servicios (RF-10) y permisos

- [x] 5.1 Implementar `CooperativaAdministratorsService` (elegibles, reemplazo del conjunto en transacción con bloqueo, máximo 3, validación de elegibilidad, cooperativa activa, auditoría). Verificar con pruebas de CP-61 a CP-64, 4 usuarios rechazados, usuario de otra cooperativa o inactivo rechazado, rol conservado al desvincular.
- [x] 5.2 Añadir `require_active_cooperativa` a `core/permissions.py`. Verificar con pruebas: admin con cooperativa activa pasa, inactiva o sin cooperativa recibe 403.
- [x] 5.3 Probar la concurrencia del tope de 3 con dos asignaciones simultáneas. Verificar que nunca se superan 3 administradores.

## 6. API

- [x] 6.1 Crear `api/v1/cooperativas_router.py` con los endpoints de cooperativas, logo y administradores bajo `/api/v1/cooperativas`, protegidos con `require_role("ADMIN_GENERAL")`; registrar el router y montar `StaticFiles` en `main.py`. Verificar con pruebas de router: respuestas de éxito, 401 sin sesión, 403 para `ADMIN_COOPERATIVA`, `SECRETARIA_COOPERATIVA` y `PASAJERO`, 409 `COOPERATIVA_INACTIVA`, 422 de validación.
- [x] 6.2 Ejecutar `pytest` completo. Verificar que pasan las pruebas nuevas y existentes.

## 7. Frontend: base

- [x] 7.1 Crear `cooperativas.service.ts` con tipos TypeScript estrictos (lista, detalle, crear, editar, estado, logo, administradores, elegibles). Verificar con pruebas vitest del servicio con cliente simulado.
- [x] 7.2 Interceptar `COOPERATIVA_INACTIVA` en el cliente HTTP para redirigir a `/dashboard` con "La cooperativa ha sido desactivada". Verificar con prueba unitaria del interceptor.
- [x] 7.3 Añadir validadores de nombre y RUC (con algoritmo) a `useFormValidation.ts`, reutilizando los de dirección, teléfono y correo. Verificar con pruebas vitest equivalentes a las del backend.
- [x] 7.4 Crear el store Pinia de cooperativas (lista, búsqueda, paginación, modo de vista) y composables `useCooperativaForm` y `useCooperativaAdministrators` (límite de 3, búsqueda con debounce). Verificar con pruebas de store y composables.

## 8. Frontend: interfaz

- [x] 8.1 Instalar los componentes shadcn-vue necesarios que falten (Dialog, Card, Badge, Checkbox, Table) verificando que no se agreguen librerías ajenas.
- [x] 8.2 Implementar `CooperativasView.vue` con selector tabla/tarjetas, `CooperativaTable` y `CooperativaCard` (logo o icono Lucide, nombre, estado, engranaje); reemplazar el placeholder en `router/index.ts`. Verificar con pruebas de componente de CP-54 y estados activa/desactivada.
- [x] 8.3 Implementar `CooperativaFormDialog` para registro y edición (RUC deshabilitado al editar, logo por URL o subida, mensajes de error de las specs) y acciones Desactivar/Activar con confirmación. Verificar con pruebas de componente de CP-46 a CP-53 y CP-55 a CP-59.
- [x] 8.4 Implementar la sección "Personal de cooperativa" y `CooperativaAdministratorsModal` (búsqueda, selección múltiple, bloqueo al llegar a 3, guardado y desvinculación). Verificar con pruebas de componente de CP-61 a CP-64.
- [x] 8.5 Revisar tokens del tema, modo claro/oscuro, ausencia de emojis y colores fijos, y responsive. Verificar con `npm run lint` y revisión visual de tabla y tarjetas en ambos modos.

## 9. Integración

- [x] 9.1 Ejecutar `npm run test:unit` y `npm run lint`. Verificar que no hay fallas ni errores de tipos.
- [x] 9.2 Recorrer manualmente el flujo completo: registrar, editar, asignar 3 administradores, desvincular, desactivar y editar desde otra sesión. Verificar cada resultado contra los CP-46 a CP-64.

## 10. Mejoras y correcciones

- [x] 10.1 Corregir reactividad de `isEditMode` en `CooperativaFormDialog.vue` y `useCooperativaForm.ts` para que actualice textos a "Editar Cooperativa", botón a "Guardar cambios", deshabilite el RUC y envíe la petición de actualización (PUT) en lugar de creación (POST).
- [x] 10.2 Permitir la asignación opcional de administradores de cooperativa tanto en el formulario de registro como en el de edición (soporte para `cooperativa_id=0` al listar usuarios elegibles y vinculación al crear).
- [x] 10.3 Permitir en la actualización enlaces de logo relativos generados por el sistema (`/static/logos/...`) y resolver la URL absoluta con `resolveLogoUrl` para que las imágenes se visualicen correctamente en tarjetas, tabla y vista previa.
- [x] 10.4 Configurar el cierre automático del modal tanto al finalizar con éxito como en caso de error para visualizar claramente el mensaje de alerta en la vista.
- [x] 10.5 Mejorar el mensaje de validación cuando el campo RUC se omite o contiene solo espacios a "El RUC es obligatorio" en frontend y backend.
- [x] 10.6 Actualizar las especificaciones y requisitos correspondientes en `openspec/requirements/cooperatives/submodule04.md` y `openspec/changes/cooperatives-submodule04/`.
- [x] 10.7 Ejecutar la suite completa de pruebas de backend y frontend para garantizar 0 regresiones.

## Workflow follow-up

- Archivar el cambio tras la revisión (`/opsx:archive`).

