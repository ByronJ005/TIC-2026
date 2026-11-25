# Locality Catalog Specification

## Purpose

Mantiene un catálogo compartido de localidades que alimenta el origen, el destino y las paradas de las rutas, permitiendo registrar una localidad nueva sin salir del formulario y evitando duplicados.

## Requirements

### Requirement: Catálogo accesible por ambos administradores
El sistema DEBE permitir a los usuarios con rol `ADMIN_GENERAL` o `ADMIN_COOPERATIVA` buscar y registrar localidades. Los demás roles NO DEBEN poder consultar ni crear localidades.

#### Scenario: Acceso por rol
- **GIVEN** un usuario autenticado sin rol `ADMIN_GENERAL` ni `ADMIN_COOPERATIVA`
- **WHEN** intenta buscar o crear una localidad
- **THEN** el sistema deniega la operación con HTTP 403

### Requirement: Búsqueda y creación inmediata de localidades
El selector de localidades DEBE ofrecer búsqueda con autocompletado. Si el texto no coincide con ninguna localidad, DEBE ofrecer la opción "Crear y usar la nueva localidad", que la registra y la deja seleccionada sin salir del formulario.

#### Scenario: CP-77 Registrar una nueva localidad desde el selector del catálogo
- **GIVEN** que el Administrador está en el formulario de una ruta y escribe en el selector un nombre que no existe en el catálogo
- **WHEN** selecciona la opción "Crear y usar la nueva localidad"
- **THEN** el sistema registra la localidad en el catálogo, la deja seleccionada en el campo correspondiente y la hace disponible para futuras rutas

### Requirement: Unicidad y normalización de localidades
El nombre de la localidad DEBE ser único sin distinguir mayúsculas de minúsculas, no puede quedar vacío ni compuesto solo por espacios, y el campo DEBE eliminar automáticamente los espacios sobrantes. Si el texto buscado coincide con una localidad existente, la interfaz DEBE resaltar la existente y NO DEBE ofrecer crear una nueva. El backend DEBE rechazar duplicados.

#### Scenario: Búsqueda de una localidad existente en mayúsculas
- **GIVEN** que existe la localidad "Loja" en el catálogo
- **WHEN** el Administrador escribe "LOJA" en el selector
- **THEN** el sistema resalta la localidad existente y no muestra el botón para registrar una nueva

#### Scenario: Duplicado enviado directamente a la API
- **GIVEN** que existe la localidad "Loja"
- **WHEN** se envía a la API la creación de " loja " con espacios y distinta capitalización
- **THEN** el backend rechaza la creación o devuelve la localidad existente sin crear un duplicado
