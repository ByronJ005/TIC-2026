# Notifications Specification

## Purpose

Informa a los usuarios de eventos relevantes, como la desactivación de una ruta, mediante un centro de notificaciones dentro de la aplicación y correo electrónico, respetando la privacidad de cada usuario.

## Requirements

### Requirement: Icono de notificaciones visible
El encabezado DEBE mostrar, junto al nombre de usuario, un icono de notificaciones visible para cualquier usuario autenticado, con un indicador de la cantidad de notificaciones no leídas.

#### Scenario: CP-99 Mensaje cuando no existen notificaciones
- **GIVEN** que un usuario autenticado no tiene notificaciones
- **WHEN** pulsa el icono de notificaciones
- **THEN** el sistema muestra el mensaje "No tienes notificaciones"

#### Scenario: CP-100 Visualizar las más recientes
- **GIVEN** que un usuario autenticado tiene notificaciones
- **WHEN** pulsa el icono de notificaciones
- **THEN** el sistema muestra las 5 más recientes con mensaje y fecha, distingue visualmente las no leídas y muestra el total de no leídas en el icono

### Requirement: Listado paginado de notificaciones
El listado DEBE mostrar las notificaciones de la más reciente a la más antigua, 5 por vez. El botón "Cargar más" DEBE agregar otras 5 y ocultarse cuando no queden más.

#### Scenario: CP-101 Cargar más notificaciones
- **GIVEN** que el usuario tiene más de 5 notificaciones y abrió el listado
- **WHEN** pulsa "Cargar más"
- **THEN** el sistema agrega otras 5 más antiguas y oculta el botón cuando ya no hay más

### Requirement: Marcar notificaciones como leídas
El botón "Marcar todas como leídas" DEBE actualizar todas las notificaciones del usuario a leídas.

#### Scenario: CP-102 Marcar todas como leídas
- **GIVEN** que el usuario tiene notificaciones no leídas
- **WHEN** pulsa "Marcar todas como leídas"
- **THEN** el sistema actualiza todas a leídas y el indicador de no leídas desaparece del icono

### Requirement: Privacidad de las notificaciones
Un usuario SOLO DEBE poder consultar y marcar como leídas sus propias notificaciones. El backend NO DEBE devolver ni modificar notificaciones de otro usuario.

#### Scenario: Acceso a notificaciones ajenas
- **GIVEN** dos usuarios con notificaciones distintas
- **WHEN** el primero consulta o marca como leídas sus notificaciones por la API
- **THEN** el sistema solo devuelve y modifica las del usuario autenticado

### Requirement: Notificación por desactivación de ruta general
Al desactivar una ruta general adoptada, el sistema DEBE crear una notificación in-app y enviar un correo a cada administrador activo de las cooperativas afectadas. Cuando existan turnos y reservas, DEBE notificar también a los pasajeros afectados.

#### Scenario: CP-103 Generar notificaciones al desactivar una ruta adoptada
- **GIVEN** que el Administrador General desactiva una ruta adoptada por una cooperativa con administradores activos
- **WHEN** el sistema completa la desactivación
- **THEN** cada administrador activo de la cooperativa afectada recibe una notificación in-app y un correo indicando que la ruta fue desactivada por la administración del terminal

### Requirement: Resiliencia del envío de correo
Un fallo en el envío del correo NO DEBE revertir la operación principal ni la notificación in-app. El error DEBE registrarse sin datos sensibles ni detalles técnicos para el usuario.

#### Scenario: CP-104 Conservar la notificación ante un fallo de correo
- **GIVEN** que el servicio de correo no está disponible al desactivar una ruta adoptada
- **WHEN** el sistema intenta enviar el correo
- **THEN** completa la desactivación, conserva la notificación in-app y registra el error sin mostrar detalles técnicos al usuario
