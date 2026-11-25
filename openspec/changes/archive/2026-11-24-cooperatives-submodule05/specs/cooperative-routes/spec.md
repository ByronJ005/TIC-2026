# Cooperative Routes Specification

## Purpose

Permite al Administrador de cooperativa adoptar rutas generales activas y gestionar rutas específicas propias, aisladas por cooperativa, con control de estado y bloqueo cuando la cooperativa está desactivada.

## Requirements

### Requirement: Acceso y pertenencia por cooperativa
Solo los usuarios con rol `ADMIN_COOPERATIVA` DEBEN gestionar rutas de cooperativa y únicamente sobre su propia cooperativa. El backend DEBE validar la pertenencia con la cooperativa del usuario autenticado y NO DEBE confiar en IDs enviados por el frontend.

#### Scenario: CP-97 Impedir el acceso a rutas de otra cooperativa
- **GIVEN** que un Administrador de cooperativa intenta consultar por la URL una ruta específica de otra cooperativa
- **WHEN** el sistema valida la pertenencia del recurso
- **THEN** el sistema deniega el acceso y redirige al Administrador a la pantalla de Inicio

#### Scenario: Acceso a recurso ajeno por la API
- **GIVEN** un Administrador de cooperativa
- **WHEN** consulta, edita o desactiva por la API una ruta o adopción de otra cooperativa
- **THEN** el backend responde HTTP 403 sin exponer ni modificar información

### Requirement: Estructura de la pantalla de rutas
La pantalla DEBE dividirse en "Rutas generales" (rutas adoptadas) y "Mis rutas" (rutas específicas), cada una con su listado o un mensaje informativo si está vacía.

#### Scenario: CP-85 Visualizar las secciones
- **GIVEN** que el Administrador de cooperativa ingresa al submódulo "Rutas" de su cooperativa activa
- **WHEN** el sistema carga la pantalla
- **THEN** muestra las secciones "Rutas generales" y "Mis rutas", cada una con su listado o un mensaje informativo

### Requirement: Adopción de rutas generales
El botón "Agregar" DEBE abrir un modal que liste únicamente las rutas generales activas aún no adoptadas por la cooperativa. Una cooperativa NO DEBE adoptar la misma ruta general más de una vez; la interfaz bloquea las ya adoptadas y el backend rechaza duplicados.

#### Scenario: CP-86 Listar solo rutas generales activas no adoptadas
- **GIVEN** que el Administrador está en "Rutas generales" y pulsa "Agregar"
- **WHEN** se abre el modal
- **THEN** el sistema lista únicamente las rutas generales activas que la cooperativa aún no adoptó

#### Scenario: CP-87 Adoptar rutas generales
- **GIVEN** que el Administrador está en el modal de selección
- **WHEN** selecciona una o más rutas y hace clic en "Guardar"
- **THEN** el sistema las asocia en estado "Activa", muestra "Rutas agregadas exitosamente" y las refleja en "Rutas generales"

#### Scenario: Adopción duplicada rechazada por la API
- **GIVEN** una ruta general ya adoptada por la cooperativa
- **WHEN** se intenta adoptarla nuevamente por la API
- **THEN** el backend rechaza la operación con un error de conflicto

### Requirement: Rutas generales adoptadas no editables
El administrador de cooperativa NO DEBE poder editar los datos de una ruta general adoptada; solo consultar su detalle y alternar el interruptor Activa/Inactiva. No existe la acción de desvincular o eliminar.

#### Scenario: Modificación de datos de ruta general rechazada
- **GIVEN** un Administrador de cooperativa con una ruta general adoptada
- **WHEN** intenta modificar los datos de esa ruta general por la API
- **THEN** el backend responde HTTP 403

### Requirement: Interruptor Activa/Inactiva de rutas generales adoptadas
El administrador DEBE poder activar o desactivar una ruta general adoptada. Solo PUEDE reactivarla si la ruta general sigue activa. Si tiene turnos o reservas activas, DEBE mostrarse un modal de confirmación y notificar a los usuarios afectados.

#### Scenario: CP-88 Deshabilitar una ruta general adoptada
- **GIVEN** una ruta general adoptada "Activa" sin turnos ni reservas activas
- **WHEN** el Administrador cambia el interruptor a "Inactiva"
- **THEN** el sistema actualiza el estado para la cooperativa, muestra "Ruta desactivada exitosamente" y conserva la asociación

#### Scenario: CP-89 Deshabilitar con turnos o reservas activas (PENDIENTE)
- **GIVEN** una ruta con turnos activos o pasajes reservados
- **WHEN** el Administrador cambia el interruptor a "Inactiva"
- **THEN** el sistema muestra un modal de confirmación y, al confirmar, desactiva la ruta y notifica a los usuarios afectados por correo y dentro de la aplicación

#### Scenario: CP-90 Reactivar una ruta general adoptada
- **GIVEN** una ruta general adoptada "Inactiva" cuya ruta general sigue activa
- **WHEN** el Administrador cambia el interruptor a "Activa"
- **THEN** el sistema actualiza el estado a "Activa" y muestra "Ruta activada exitosamente"

#### Scenario: CP-91 Impedir reactivar si la ruta general está inactiva
- **GIVEN** una ruta general adoptada desactivada porque el Administrador General desactivó la ruta general
- **WHEN** el Administrador intenta cambiar el interruptor a "Activa"
- **THEN** el sistema impide la operación y muestra "La ruta general se encuentra desactivada por la administración del terminal"

### Requirement: Registro de rutas específicas
El administrador DEBE poder registrar rutas específicas con los mismos campos, formatos y validaciones de las rutas generales (nombre con prefijo, distancia, tiempo, paradas secuenciales, origen distinto del destino, descripción y texto adicional con sus límites). Las rutas NO incluyen precio y usan el catálogo de localidades.

#### Scenario: CP-92 Registrar una ruta específica con datos válidos
- **GIVEN** que el Administrador está en "Mis rutas" y pulsa "Nueva ruta"
- **WHEN** selecciona Origen y Destino distintos, ingresa distancia mayor a 0 y tiempo estimado válido, define sus localidades y confirma
- **THEN** el sistema registra la ruta "Activa" asociada a su cooperativa, muestra "Ruta registrada exitosamente" y la añade a "Mis rutas"

### Requirement: Unicidad de rutas específicas por cooperativa
No DEBEN existir dos rutas específicas de la misma cooperativa con el mismo Origen, Destino y Distancia. Otra cooperativa PUEDE registrar esa misma combinación.

#### Scenario: CP-93 Rutas similares entre cooperativas distintas
- **GIVEN** que otra cooperativa ya registró una ruta específica
- **WHEN** el Administrador registra una con el mismo Origen, Destino y Distancia en su cooperativa
- **THEN** el sistema registra la ruta exitosamente sin conflicto

#### Scenario: Duplicado dentro de la misma cooperativa
- **GIVEN** que la cooperativa ya tiene una ruta específica con cierto Origen, Destino y Distancia
- **WHEN** intenta registrar otra con la misma combinación
- **THEN** el sistema impide el registro con un mensaje de error de duplicado

### Requirement: Edición de rutas específicas
El administrador DEBE poder editar sus rutas específicas. Si tienen turnos asociados, Origen y Destino DEBEN quedar bloqueados.

#### Scenario: CP-94 Editar una ruta específica
- **GIVEN** que el Administrador abre la edición de una ruta de "Mis rutas"
- **WHEN** modifica campos permitidos con datos válidos y confirma
- **THEN** el sistema actualiza la ruta y muestra "Ruta actualizada exitosamente"

### Requirement: Activación y desactivación de rutas específicas
El administrador DEBE poder desactivar y reactivar sus rutas específicas. Con turnos o reservas activas DEBE exigirse confirmación y notificar a los afectados.

#### Scenario: CP-95 Desactivar una ruta específica
- **GIVEN** una ruta de "Mis rutas" "Activa" sin turnos ni reservas activas
- **WHEN** el Administrador selecciona "Desactivar" y confirma
- **THEN** el sistema actualiza el estado a "Inactiva", muestra "Ruta desactivada exitosamente" y conserva su información

#### Scenario: CP-96 Reactivar una ruta específica
- **GIVEN** una ruta de "Mis rutas" "Inactiva"
- **WHEN** el Administrador selecciona "Activar" y confirma
- **THEN** el sistema actualiza el estado a "Activa" y muestra "Ruta activada exitosamente"

### Requirement: Cooperativa desactivada
Si la cooperativa está desactivada, el sistema DEBE bloquear el acceso y las acciones sobre sus rutas, y DEBE conservar su información.

#### Scenario: CP-98 Bloquear la gestión de rutas
- **GIVEN** que la cooperativa del Administrador está "Desactivada"
- **WHEN** intenta acceder al submódulo "Rutas" o actuar sobre sus rutas
- **THEN** el sistema bloquea la acción, oculta las secciones de rutas y muestra "Cooperativa desactivada", conservando la información de las rutas

### Requirement: Auditoría de rutas de cooperativa
El sistema DEBE registrar en auditoría la adopción de rutas generales, la creación y edición de rutas específicas y los cambios de estado, sin datos sensibles.

#### Scenario: Registro de auditoría
- **GIVEN** que el Administrador adopta una ruta general o cambia el estado de una ruta
- **WHEN** la operación finaliza
- **THEN** el sistema guarda un registro de auditoría con usuario, acción, entidad y resultado
