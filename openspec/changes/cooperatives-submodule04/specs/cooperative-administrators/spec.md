# Spec Delta

## Purpose

Permite al Administrador General vincular y desvincular hasta tres administradores de cooperativa a cada cooperativa, garantizando que cada administrador pertenezca a una sola cooperativa.

## ADDED Requirements

### Requirement: Sección Personal de cooperativa
El formulario de registro y la pantalla de edición de una cooperativa DEBEN incluir una sección "Personal de cooperativa" con los administradores asignados o seleccionados y un botón "Gestionar administradores" que abre un modal de selección. La asignación en el registro es opcional.

#### Scenario: Visualizar personal asignado
- **GIVEN** que el Administrador está en la pantalla "Cooperativas" en la edición de una cooperativa con administradores
- **WHEN** visualiza la sección "Personal de cooperativa"
- **THEN** el sistema muestra los nombres de los administradores asignados y el botón "Gestionar administradores"

### Requirement: Usuarios elegibles
El modal DEBE listar únicamente usuarios con rol `ADMIN_COOPERATIVA`, en estado Activo y sin cooperativa asignada, además de los ya asignados a la cooperativa actual. El backend DEBE rechazar la asignación de usuarios que no cumplan estas condiciones.

#### Scenario: Filtro de elegibles
- **GIVEN** usuarios activos sin cooperativa, usuarios asignados a otra cooperativa, usuarios inactivos y usuarios sin rol `ADMIN_COOPERATIVA`
- **WHEN** el Administrador abre el modal "Gestionar administradores"
- **THEN** solo aparecen los usuarios activos con rol `ADMIN_COOPERATIVA` libres o ya asignados a esta cooperativa

#### Scenario: Asignación inválida por la API
- **GIVEN** una solicitud que incluye un usuario inactivo, sin el rol o asignado a otra cooperativa
- **WHEN** el backend la procesa
- **THEN** rechaza la operación con un error y no modifica ninguna asignación

### Requirement: Asignación de administradores
El sistema DEBE permitir asignar de uno a tres administradores a una cooperativa activa desde el modal, y mostrar sus nombres en la sección "Personal de cooperativa" tras guardar. Un usuario DEBE pertenecer a una sola cooperativa.

#### Scenario: CP-61 Asignar administradores
- **GIVEN** que el Administrador está en la pantalla "Cooperativas" en la edición de una cooperativa activa y pulsa "Gestionar administradores"
- **WHEN** selecciona uno o más usuarios elegibles (máximo 3) y hace clic en "Guardar"
- **THEN** el sistema vincula a los usuarios, muestra "Administradores asignados exitosamente" y refleja sus nombres en "Personal de cooperativa"

### Requirement: Límite de tres administradores
El sistema DEBE permitir como máximo 3 administradores por cooperativa. El modal DEBE deshabilitar el resto de opciones al llegar a 3 selecciones y el backend DEBE rechazar cualquier solicitud que supere el límite, incluso ante solicitudes concurrentes.

#### Scenario: CP-62 Bloqueo al alcanzar 3
- **GIVEN** que el Administrador está en la pantalla "Cooperativas" dentro del modal "Gestionar administradores"
- **WHEN** selecciona 3 usuarios
- **THEN** el sistema deshabilita la selección de los demás usuarios

#### Scenario: Solicitud con más de 3 administradores
- **GIVEN** una solicitud de asignación con 4 usuarios
- **WHEN** el backend la procesa
- **THEN** la rechaza y no modifica las asignaciones

### Requirement: Desvinculación de administradores
El sistema DEBE permitir desvincular administradores de una cooperativa. Al desvincular, el usuario DEBE conservar el rol `ADMIN_COOPERATIVA` y quedar sin cooperativa asignada, disponible para una nueva asignación.

#### Scenario: CP-63 Desvincular administrador
- **GIVEN** que el Administrador está en la pantalla "Cooperativas" en "Personal de cooperativa" de una cooperativa con administradores
- **WHEN** retira a uno de la lista y confirma los cambios
- **THEN** el sistema retira la vinculación, mantiene su rol `ADMIN_COOPERATIVA` y muestra "Administrador desvinculado exitosamente"

### Requirement: Búsqueda de usuarios en el modal
El modal DEBE incluir una barra de búsqueda que filtre los usuarios elegibles por nombre, apellido o correo.

#### Scenario: CP-64 Buscar usuarios elegibles
- **GIVEN** que el Administrador está en la pantalla "Cooperativas" con el modal "Gestionar administradores" abierto
- **WHEN** escribe un término en la barra de búsqueda
- **THEN** el sistema muestra solo los usuarios elegibles que coinciden con el término

### Requirement: Cooperativa desactivada
El sistema DEBE rechazar cambios de administradores sobre una cooperativa desactivada.

#### Scenario: Asignar administradores a cooperativa desactivada
- **GIVEN** una cooperativa desactivada
- **WHEN** se intenta modificar sus administradores
- **THEN** el sistema rechaza la operación y el cliente redirige al Inicio con "La cooperativa ha sido desactivada"

### Requirement: Auditoría de asignaciones
El sistema DEBE registrar los cambios de administradores de una cooperativa con usuario, fecha y hora, acción, entidad y resultado.

#### Scenario: Registro de cambio de administradores
- **GIVEN** un cambio de administradores
- **WHEN** se completa
- **THEN** queda un registro de auditoría de la operación
