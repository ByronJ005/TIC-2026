# PROJECT.md

Contexto de dominio del proyecto. No cambia tarea a tarea, describe *qué es* el sistema y sus reglas de negocio.
Para instrucciones operativas (comandos, arquitectura de capas, convenciones de código) ver `AGENTS.md`.

## 1. Descripción

Aplicación web para la reserva y gestión de boletos de transporte terrestre, orientada a cooperativas que operan desde un terminal terrestre. No se contempla pagos ni facturación.

Módulos principales:
1. Seguridad
2. Cooperativas
3. Reservas

Cada módulo puede incluir sus propias funcionalidades de reportes.

## 2. Roles y permisos

### ADMIN_GENERAL
- Crear y administrar cooperativas.
- Gestionar rutas generales.
- Gestionar usuarios y permisos.
- Gestionar los precios generales aplicables a todas las cooperativas.

### ADMIN_COOPERATIVA
- Gestionar su cooperativa: buses, asientos, rutas específicas, turnos, precios y tarifas específicas.
- Consultar información de su propia cooperativa.
- **Restricción clave:** solo puede administrar recursos de su propia cooperativa. Verificar siempre la pertenencia del recurso antes de permitir actualizar, eliminar, modificar o consultar información restringida. Nunca confiar solo en IDs enviados por el frontend.

### SECRETARIA_COOPERATIVA
-Generar nuevas reservas o actualizar el estado de las existentes a CONFIRMADO una vez recibido el pago en ventanilla.

### PASAJERO
- Consultar rutas y horarios.
- Seleccionar asientos, reservar.
- Consultar sus propias reservas y actualizar su perfil.
- **Restricción clave:** El rol "Pasajero" es el rol por defecto del sistema; en la interfaz debe mostrarse bloqueado/deshabilitado (disabled) y seleccionado por defecto, y a nivel de backend nunca debe eliminarse del array o conjunto de roles. Un usuario puede tener asignados simultáneamente varios roles adicionales (ej. Pasajero + Secretaria de Cooperativa).

RBAC: los endpoints deben validar el rol requerido antes de ejecutar operaciones protegidas. Respuesta de autorización incorrecta → HTTP 403.

## 3. Reservas y concurrencia

Regla crítica: el sistema **nunca** debe permitir que dos pasajeros reserven el mismo asiento simultáneamente.

Alcance del prototipo: el sistema gestiona **únicamente reservas**. No existe compra ni pago en línea.

Flujo transaccional (PostgreSQL/SQLAlchemy):
1. Verificar disponibilidad del asiento.
2. Bloquear el asiento (`SELECT ... FOR UPDATE`) dentro de la transacción.
3. Crear la reserva con su fecha de expiración (`expires_at`).
4. Confirmar transacción (`COMMIT`) o revertir (`ROLLBACK`) ante error.

La disponibilidad definitiva se valida siempre en backend + base de datos, nunca solo en el frontend. Como respaldo, la base de datos debe garantizar la unicidad con un índice único parcial sobre (viaje, asiento) para reservas activas.

Cada reserva tiene un tiempo límite para ser retirada y pagada en ventanilla. Al vencer, pasa a `EXPIRADO` y el asiento vuelve a estar disponible (mediante tarea programada y/o validación al consultar disponibilidad).

## 4. Estados de asiento

```
DISPONIBLE → RESERVADO
RESERVADO → EXPIRADO    (venció el plazo sin retiro en ventanilla)
RESERVADO → CANCELADO   (el pasajero cancela manualmente su reserva)
RESERVADO → CONFIRMADO (el pasajero se ha acercado a boletería a realizar el pago)
```

- `RESERVADO` es el estado final activo dentro del sistema; la compra en ventanilla queda fuera del alcance del prototipo.
- Las transiciones inválidas se rechazan. La lógica de transición vive en el Service Layer (ver `AGENTS.md`).

## 5. Seguridad

- Autenticación basada en JWT.
- Contraseñas nunca en texto plano (hash, ej. bcrypt).
- Secretos y credenciales solo por variables de entorno, nunca hardcodeados.

## 6. Integridad de datos

Usar restricciones de PostgreSQL donde protejan la integridad: Foreign Keys, Unique Constraints, Not Null, Check Constraints, índices — especialmente en todo lo relacionado a reservas y disponibilidad de asientos.
El número de cédula debe ser validado algorítmicamente bajo el estándar ecuatoriano en el backend antes de ser insertado. El pasaporte aceptará entre 6 a 20 caracteres para adaptar diferentes estándares internacionales.

## 7. Reportes y auditoría

- Reportes deben soportar filtro, orden, paginación, y consulta por fecha/estado/cooperativa/ruta, respetando siempre los permisos del usuario (un ADMIN_COOPERATIVA no ve datos de otra cooperativa).
- Auditar operaciones administrativas y críticas: crear cooperativa, modificar permisos/rutas/buses/tarifas, cancelar reservas, cambios de estado crítico. Registrar usuario, fecha/hora, acción, módulo, entidad afectada, resultado.
- Logging: nunca contraseñas, tokens, ni datos sensibles de pago.

## 8. UI/UX

- Sistema visual consistente: paleta de colores, tipografía, espaciado, estados de carga/error/éxito definidos como tokens de diseño.
- Modo claro y modo oscuro mediante variables/tokens.
- Responsive: escritorio, laptop, tablet, móvil.
- Accesibilidad: contraste adecuado, labels en formularios, navegación por teclado, mensajes de error claros, tamaños de elementos interactivos adecuados.

## 9. Testing — casos críticos de dominio

Priorizar pruebas sobre: autenticación, roles y permisos, creación de reservas, asientos ocupados/concurrencia, expiración de reservas, transiciones de estado inválidas, restricciones por cooperativa.

## 10. DevSecOps

Mantener dependencias actualizadas, evitar librerías con vulnerabilidades conocidas cuando exista alternativa estable. Proyecto preparado para análisis de dependencias, SBOM, escaneo de vulnerabilidades e integración futura con CI/CD.