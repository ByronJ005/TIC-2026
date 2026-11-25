# General Routes Specification

## Purpose

Permite al Administrador General administrar el catálogo de rutas generales del terminal y supervisar en solo lectura las rutas específicas de cada cooperativa, garantizando coherencia de datos, unicidad y trazabilidad.

## Requirements

### Requirement: Acceso exclusivo del Administrador General
Solo los usuarios con rol `ADMIN_GENERAL` DEBEN poder crear, editar, activar y desactivar rutas generales. Cualquier otro rol DEBE recibir HTTP 403.

#### Scenario: Rol no autorizado
- **GIVEN** un usuario autenticado sin rol `ADMIN_GENERAL`
- **WHEN** intenta gestionar rutas generales por la interfaz o por la API
- **THEN** el sistema deniega la operación con HTTP 403 y no modifica información

### Requirement: Registro de ruta general
El sistema DEBE registrar una ruta general con Origen, Destino, Nombre, Distancia, Tiempo estimado, localidades por las que pasa y Estado (Activa por defecto), y una Descripción opcional de hasta 100 caracteres. El precio NO forma parte de la ruta.

#### Scenario: CP-65 Registrar ruta general con datos válidos
- **GIVEN** que el Administrador está en el submódulo "Rutas" y pulsa "Nueva ruta general"
- **WHEN** selecciona un Origen y un Destino distintos, deja vacío el texto adicional del nombre, ingresa una distancia mayor a 0 y un tiempo estimado mayor a 0, mantiene marcada "Solo las de origen y destino", agrega una descripción y confirma
- **THEN** el sistema registra la ruta en estado "Activa", muestra "Ruta registrada exitosamente" y la añade al listado de rutas generales

#### Scenario: CP-67 Validar campos obligatorios vacíos
- **GIVEN** que el Administrador está en el formulario de registro de una ruta general
- **WHEN** deja vacíos uno o más campos obligatorios (Origen, Destino, Distancia o Tiempo estimado) y hace clic en "Guardar"
- **THEN** el sistema impide el registro y marca cada campo requerido con su mensaje de error (por ejemplo, "El origen es obligatorio" o "La distancia es obligatoria")

### Requirement: Nombre de la ruta
El nombre DEBE componerse de un prefijo no editable `Origen - Destino` y un texto adicional opcional de máximo 30 caracteres. Sin texto adicional, el nombre es solo `Origen - Destino`. El prefijo DEBE actualizarse al cambiar Origen o Destino mientras sean editables.

#### Scenario: CP-66 Generar el nombre con prefijo no editable y texto adicional
- **GIVEN** que el Administrador está en el formulario de registro de una ruta general
- **WHEN** selecciona un Origen y un Destino distintos, escribe texto en el campo adicional del nombre y confirma
- **THEN** el sistema guarda el nombre completo combinando el prefijo y el texto adicional

### Requirement: Coherencia de origen, destino y paradas
El Origen y el Destino DEBEN ser distintos. Ninguna parada intermedia PUEDE ser igual al Origen o al Destino ni repetirse en la misma ruta. El backend DEBE validar estas reglas.

#### Scenario: CP-68 Origen y Destino distintos
- **GIVEN** que el Administrador está en el formulario de registro o edición de una ruta general
- **WHEN** selecciona la misma localidad como Origen y Destino
- **THEN** el sistema impide el registro y muestra "El origen y el destino deben ser diferentes"

#### Scenario: CP-69 Parada igual al Origen o Destino
- **GIVEN** que el Administrador desmarcó "Solo las de origen y destino"
- **WHEN** agrega como parada intermedia la localidad del Origen o del Destino
- **THEN** el sistema impide agregar la parada y muestra "Una parada intermedia no puede ser igual al origen o al destino"

#### Scenario: CP-70 Paradas duplicadas
- **GIVEN** que el Administrador desmarcó "Solo las de origen y destino" y ya agregó una localidad como parada
- **WHEN** intenta agregar nuevamente la misma localidad
- **THEN** el sistema impide la duplicidad y muestra "La localidad ya fue agregada como parada de esta ruta"

### Requirement: Paradas intermedias secuenciales
La opción "Solo las de origen y destino" DEBE estar marcada por defecto. Al desmarcarla se DEBEN poder agregar paradas, cada una con Localidad y Número de Orden consecutivo definido manualmente, y se DEBE exigir al menos una.

#### Scenario: CP-71 Registrar paradas intermedias en orden secuencial
- **GIVEN** que el Administrador registra una ruta y desmarca "Solo las de origen y destino"
- **WHEN** agrega varias localidades intermedias definiendo su orden y confirma
- **THEN** el sistema guarda las paradas con su número de orden consecutivo y las muestra en ese orden en el detalle

#### Scenario: CP-72 Exigir al menos una parada
- **GIVEN** que el Administrador desmarca "Solo las de origen y destino" sin agregar paradas
- **WHEN** hace clic en "Guardar"
- **THEN** el sistema impide el registro y muestra "Debe agregar al menos una parada intermedia o marcar la opción 'Solo las de origen y destino'"

### Requirement: Distancia y tiempo estimado
La distancia DEBE expresarse en kilómetros con decimales y ser mayor a 0; la interfaz NO DEBE admitir caracteres no numéricos. El tiempo DEBE ingresarse en Horas y Minutos (minutos de 0 a 59), ser mayor a 0 y menor a 24 horas, y almacenarse en minutos.

#### Scenario: CP-73 Distancia inválida
- **GIVEN** que el Administrador está en el formulario de una ruta general
- **WHEN** ingresa una distancia igual a 0 o negativa y hace clic en "Guardar"
- **THEN** el sistema impide el registro y muestra "La distancia debe ser un número mayor a 0"

#### Scenario: CP-74 Tiempo estimado inválido
- **GIVEN** que el Administrador está en el formulario de una ruta general
- **WHEN** ingresa valores fuera de rango (minutos fuera de 0 a 59) o ambos campos en 0 y hace clic en "Guardar"
- **THEN** el sistema impide el registro y muestra "Ingrese un tiempo estimado válido. El tiempo total debe ser mayor a cero y los minutos deben estar entre 0 y 59"

### Requirement: Unicidad de rutas generales
No DEBEN existir dos rutas generales con la misma combinación de Origen, Destino y Distancia.

#### Scenario: CP-75 Combinación duplicada
- **GIVEN** que existe una ruta general con el mismo Origen, Destino y Distancia
- **WHEN** el Administrador intenta registrar una nueva con esa combinación
- **THEN** el sistema impide el registro y muestra "Ya existe una ruta general con el mismo origen, destino y distancia"

#### Scenario: CP-76 Misma pareja con distancia distinta
- **GIVEN** que existe una ruta general con un Origen y Destino determinados
- **WHEN** el Administrador registra otra con el mismo Origen y Destino pero distinta distancia
- **THEN** el sistema registra la nueva ruta exitosamente

### Requirement: Edición de rutas generales
El sistema DEBE permitir editar una ruta general. Si tiene cooperativas o turnos asociados, el Origen y el Destino DEBEN quedar bloqueados en la interfaz y el backend DEBE rechazar cualquier intento de modificarlos.

#### Scenario: CP-78 Editar todos los campos sin asociaciones
- **GIVEN** que el Administrador abre la edición de una ruta general sin cooperativas ni turnos asociados
- **WHEN** modifica cualquier campo, incluyendo Origen y Destino, con datos válidos y confirma
- **THEN** el sistema actualiza la ruta, regenera el prefijo del nombre si cambió Origen o Destino y muestra "Ruta actualizada exitosamente"

#### Scenario: CP-79 Restringir Origen y Destino con asociaciones (PENDIENTE)
- **GIVEN** que el Administrador abre la edición de una ruta general con cooperativas o turnos asociados
- **WHEN** visualiza el formulario
- **THEN** el sistema presenta Origen y Destino deshabilitados, permite modificar los demás campos y al guardar muestra "Ruta actualizada exitosamente"

#### Scenario: Modificación de Origen o Destino rechazada por la API
- **GIVEN** una ruta general con cooperativas asociadas
- **WHEN** se envía a la API una actualización que cambia el Origen o el Destino
- **THEN** el backend rechaza la operación indicando que no pueden modificarse porque la ruta tiene asociaciones

### Requirement: Desactivación y reactivación de rutas generales
La desactivación DEBE ser lógica. Al desactivar una ruta adoptada, el sistema DEBE desactivar en cascada las adopciones de las cooperativas sin eliminar información, notificar por correo y dentro de la aplicación a los administradores activos de las cooperativas afectadas y registrar la auditoría. La reactivación NO DEBE reactivar las adopciones.

#### Scenario: CP-80 Desactivar sin cooperativas asociadas
- **GIVEN** una ruta general "Activa" que ninguna cooperativa adoptó
- **WHEN** el Administrador selecciona "Desactivar" y confirma
- **THEN** el sistema actualiza el estado a "Inactiva", muestra "Ruta desactivada exitosamente" y registra la acción en la auditoría

#### Scenario: CP-81 Desactivar una ruta adoptada (PENDIENTE)
- **GIVEN** una ruta general activa adoptada por una o más cooperativas
- **WHEN** el Administrador selecciona "Desactivar" y confirma el diálogo que advierte el impacto
- **THEN** el sistema desactiva la ruta y sus adopciones sin eliminar información, envía correo y notificación in-app a los administradores activos de las cooperativas afectadas y registra la auditoría

#### Scenario: CP-82 Reactivar una ruta general inactiva
- **GIVEN** una ruta general "Inactiva"
- **WHEN** el Administrador selecciona "Activar" y confirma
- **THEN** el sistema actualiza el estado a "Activa", muestra "Ruta activada exitosamente" y mantiene inactivas las adopciones hasta que cada cooperativa las habilite

### Requirement: Enlace con turnos y reservas
El sistema DEBE exponer un método documentado de verificación de viajes y reservas activos que, mientras no existan los módulos de turnos y reservas, no encuentra elementos y no bloquea la operación.

#### Scenario: Verificación sin módulos de turnos y reservas
- **GIVEN** que aún no existen turnos ni reservas en el sistema
- **WHEN** se desactiva una ruta
- **THEN** la verificación no encuentra viajes ni reservas activos y la desactivación continúa

### Requirement: Listado y filtros de rutas generales
El listado DEBE permitir filtrar por origen, destino y estado, y mostrar un mensaje informativo si no hay coincidencias.

#### Scenario: CP-83 Filtrar el listado
- **GIVEN** que el Administrador está en el listado de rutas generales
- **WHEN** aplica filtros por origen, destino o estado
- **THEN** el sistema muestra solo las rutas que cumplen los criterios y un mensaje informativo si no hay coincidencias

### Requirement: Supervisión de rutas específicas de cooperativas
Debajo de las rutas generales, el sistema DEBE mostrar las rutas específicas agrupadas por cooperativa en modo solo lectura, con un botón para ver el detalle completo (paradas, tiempo y distancia) en un modal de solo lectura.

#### Scenario: CP-84 Visualizar rutas específicas en solo lectura
- **GIVEN** que el Administrador está en el submódulo "Rutas"
- **WHEN** desplaza la vista por debajo del listado de rutas generales
- **THEN** el sistema muestra las rutas específicas agrupadas por cooperativa, sin acciones de edición, activación ni desactivación

#### Scenario: Ver detalle completo de una ruta
- **GIVEN** una ruta (general o específica) en el listado
- **WHEN** el Administrador pulsa "Ver detalle"
- **THEN** el sistema abre un modal de solo lectura con nombre, origen, destino, distancia en km, tiempo en horas y minutos, paradas en orden, descripción y estado

### Requirement: Auditoría de rutas
El sistema DEBE registrar en auditoría la creación, edición, activación y desactivación de rutas con usuario, fecha y hora, acción, módulo, entidad y resultado, sin datos sensibles.

#### Scenario: Registro de auditoría
- **GIVEN** que el Administrador registra, edita o cambia el estado de una ruta
- **WHEN** la operación finaliza
- **THEN** el sistema guarda un registro de auditoría con los datos de la acción y su resultado
