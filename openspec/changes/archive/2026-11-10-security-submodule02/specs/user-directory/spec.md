# User Directory Specification

## Purpose
Proveer al Administrador General una interfaz de consulta y administración del directorio de usuarios, con paginación en backend, búsqueda insensible a mayúsculas/minúsculas por nombres y correo electrónico, e indicadores claros de estado y rol.

## Requirements

### Requirement: Consulta paginada y búsqueda de usuarios
El sistema DEBE permitir listar usuarios con soporte para paginación (`page`, `size`) y filtro de búsqueda por texto (`search`) que busque de forma insensible a mayúsculas/minúsculas sobre `first_name`, `last_name` y `email`.

#### Scenario: Búsqueda de usuarios por coincidencia parcial de texto
- **GIVEN** que el Administrador General ingresa un término de búsqueda en la barra de consulta del módulo Usuarios
- **WHEN** el backend procesa el parámetro `search`
- **THEN** retorna únicamente los usuarios cuyos nombres, apellidos o correo contengan la cadena especificada, ordenados cronológicamente

#### Scenario: Paginación de usuarios
- **GIVEN** un volumen de usuarios registrados superior al tamaño de página configurado
- **WHEN** el Administrador navega entre páginas
- **THEN** el sistema entrega el subconjunto correspondiente de registros junto con los metadatos de paginación (`total`, `page`, `size`, `pages`)

### Requirement: Presentación de información en la tabla de usuarios
La tabla de usuarios DEBE presentar las siguientes columnas: Nombre completo, Correo electrónico, Rol(es) (mediante badges visuales), Estado (badge semántico de Activo o Inactivo), Fecha de registro (formateada) y Acciones disponibles.

#### Scenario: Visualización de fila de usuario activo
- **GIVEN** que el Administrador General visualiza la tabla de usuarios
- **WHEN** se renderiza un usuario con estado activo
- **THEN** la fila muestra el badge de "Activo", el botón "Asignar rol" y el botón "Dar de baja"

#### Scenario: Visualización de fila de usuario inactivo
- **GIVEN** que el Administrador General visualiza la tabla de usuarios
- **WHEN** se renderiza un usuario con estado inactivo
- **THEN** la fila muestra el badge de "Inactivo", el botón "Asignar rol" y el botón "Habilitar usuario"

### Requirement: Deshabilitación de acciones en la propia cuenta
En la fila de la tabla correspondiente al usuario actualmente autenticado, los botones de acción ("Dar de baja" y "Asignar rol") DEBEN presentarse deshabilitados (`disabled`) con una indicación visual de auto-protección.

#### Scenario: Visualización de la propia cuenta en la tabla
- **GIVEN** que el Administrador General visualiza su propio registro en la tabla de usuarios
- **WHEN** se examinan los controles de acción
- **THEN** los botones de "Dar de baja" y "Asignar rol" se encuentran inhabilitados para prevenir modificaciones accidentales

