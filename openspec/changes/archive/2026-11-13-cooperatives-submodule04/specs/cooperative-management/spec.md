# Spec Delta

## Purpose

Permite al Administrador General registrar, consultar, editar y dar de baja o reactivar las cooperativas del terminal, garantizando la integridad de sus datos (nombre, RUC ecuatoriano y logo) y el efecto de su desactivación.

## ADDED Requirements

### Requirement: Acceso exclusivo del Administrador General
El sistema DEBE permitir gestionar cooperativas únicamente a usuarios con rol `ADMIN_GENERAL`. Cualquier otro rol o falta de sesión DEBE ser rechazado en backend con código de error HTTP 403 o 401.

#### Scenario: Rol no autorizado
- **GIVEN** un usuario autenticado sin rol `ADMIN_GENERAL`
- **WHEN** invoca cualquier operación de gestión de cooperativas
- **THEN** el sistema responde HTTP 403 sin ejecutar la operación

### Requirement: Registro de cooperativa
El sistema DEBE permitir registrar una cooperativa con Nombre y RUC obligatorios, y Dirección, Teléfono, Correo institucional y Logo opcionales. La cooperativa nace en estado Activa. Dirección, Teléfono y Correo DEBEN reutilizar las validaciones del Registro y Perfil.

#### Scenario: CP-46 Registrar cooperativa con datos válidos
- **GIVEN** que el Administrador se encuentra en la pantalla del módulo "Cooperativas"
- **WHEN** hace clic en "Nueva Cooperativa", ingresa un Nombre y un RUC ecuatoriano válidos, llena los campos opcionales y confirma
- **THEN** el sistema registra la cooperativa en estado "Activa", muestra "Cooperativa registrada exitosamente" y la añade a la lista

#### Scenario: CP-53 Campos obligatorios vacíos o con solo espacios
- **GIVEN** que el Administrador está en la pantalla "Cooperativas" en el formulario de registro
- **WHEN** deja Nombre o RUC vacíos o con solo espacios y hace clic en "Guardar"
- **THEN** el sistema no envía el formulario y marca los campos requeridos con su mensaje de error ("El nombre de la cooperativa no puede quedar vacío" y "El RUC es obligatorio")

### Requirement: Validación del RUC
El RUC DEBE ser obligatorio, único, de exactamente 13 dígitos numéricos y válido según el algoritmo de RUC ecuatoriano. La validación DEBE realizarse en backend. Si se omite o contiene solo espacios, el sistema DEBE indicar que "El RUC es obligatorio".

#### Scenario: CP-47 RUC que no cumple el algoritmo
- **GIVEN** que el Administrador está en la pantalla "Cooperativas" en el formulario de registro
- **WHEN** ingresa un RUC de 13 dígitos que no cumple el algoritmo ecuatoriano y hace clic en "Guardar"
- **THEN** el sistema impide el registro y muestra "El RUC ingresado no es válido según el estándar ecuatoriano"

#### Scenario: CP-48 RUC con longitud incorrecta o caracteres no numéricos
- **GIVEN** que el Administrador está en la pantalla "Cooperativas" en el formulario de registro
- **WHEN** ingresa un RUC con longitud distinta a 13 o con letras o caracteres especiales
- **THEN** el sistema impide el envío y muestra "El RUC debe tener exactamente 13 dígitos numéricos"

#### Scenario: CP-49 RUC duplicado
- **GIVEN** que el Administrador está en la pantalla "Cooperativas" en el formulario de registro y ya existe una cooperativa con ese RUC
- **WHEN** intenta registrar otra cooperativa con el mismo RUC
- **THEN** el sistema impide el registro y muestra "Ya existe una cooperativa registrada con este RUC"

### Requirement: Validación del Nombre
El Nombre DEBE ser obligatorio, único sin distinguir mayúsculas de minúsculas, de máximo 100 caracteres y contener solo letras, números, espacios, guiones medios y apóstrofes. NO DEBE aceptarse un nombre vacío o solo con espacios, ni al registrar ni al editar.

#### Scenario: CP-50 Nombre duplicado
- **GIVEN** que el Administrador está en la pantalla "Cooperativas" en el formulario de registro y existe la cooperativa "Cooperativa Loja"
- **WHEN** intenta registrar otra con el mismo nombre sin distinguir mayúsculas
- **THEN** el sistema impide el registro y muestra "Ya existe una cooperativa registrada con este nombre"

#### Scenario: CP-51 Caracteres no permitidos en el Nombre
- **GIVEN** que el Administrador está en la pantalla "Cooperativas" en el formulario de registro
- **WHEN** ingresa en Nombre caracteres distintos de letras, números, espacios, guiones medios o apóstrofes
- **THEN** el sistema impide el registro y muestra "El nombre solo puede contener letras, números, espacios, guiones medios y apóstrofes"

#### Scenario: CP-52 Nombre con más de 100 caracteres
- **GIVEN** que el Administrador está en la pantalla "Cooperativas" en el formulario de registro
- **WHEN** ingresa un nombre de más de 100 caracteres
- **THEN** el sistema impide el registro y muestra "El nombre de la cooperativa no puede exceder los 100 caracteres"

### Requirement: Logo de la cooperativa
El Logo DEBE ser opcional y poder indicarse mediante un enlace `http` o `https`, o subiendo una imagen PNG, JPG o WEBP de hasta 2 MB. En la edición se DEBEN admitir además enlaces relativos generados por el sistema (`/static/logos/...`). El sistema DEBE rechazar archivos de otro tipo o tamaño superior.

#### Scenario: Logo por enlace válido
- **GIVEN** que el Administrador está en el formulario de una cooperativa
- **WHEN** ingresa una URL `https` de imagen y guarda
- **THEN** el sistema guarda el logo y lo muestra en la tarjeta y la tabla

#### Scenario: Archivo de logo inválido
- **GIVEN** que el Administrador está en el formulario de una cooperativa
- **WHEN** sube un archivo que no es PNG, JPG o WEBP, o supera 2 MB
- **THEN** el sistema rechaza la subida con un mensaje de error y no altera el logo actual

### Requirement: Visualización en tabla y tarjetas
El sistema DEBE listar las cooperativas con búsqueda y paginación, y DEBE permitir alternar entre vista de tabla y vista de tarjetas. Cada tarjeta DEBE mostrar logo, nombre, estado (Activa o Desactivada) y un botón de engranaje que abre la edición.

#### Scenario: CP-54 Alternar modo de visualización
- **GIVEN** que el Administrador se encuentra en la pantalla del módulo "Cooperativas"
- **WHEN** hace clic en el botón de alternar visualización
- **THEN** el sistema cambia entre tabla y cuadrícula de tarjetas, mostrando en cada tarjeta logo, nombre, estado y botón de engranaje

### Requirement: Edición de cooperativa
El sistema DEBE permitir editar Nombre, Dirección, Teléfono, Correo y Logo de una cooperativa activa. El RUC DEBE ser inmutable: se muestra deshabilitado y el backend DEBE ignorar o rechazar cualquier intento de modificarlo.

#### Scenario: CP-55 Actualizar información
- **GIVEN** que el Administrador está en la pantalla "Cooperativas" y abre la edición de una cooperativa activa con el engranaje
- **WHEN** modifica campos permitidos con datos válidos y confirma
- **THEN** el sistema actualiza la información y muestra "Cooperativa actualizada exitosamente"

#### Scenario: CP-56 Nombre vacío o con solo espacios al editar
- **GIVEN** que el Administrador está en la pantalla "Cooperativas" editando una cooperativa
- **WHEN** borra el Nombre o lo reemplaza por espacios y hace clic en "Guardar cambios"
- **THEN** el sistema impide la actualización y muestra "El nombre de la cooperativa no puede quedar vacío"

#### Scenario: CP-57 RUC de solo lectura en edición
- **GIVEN** que el Administrador está en la pantalla "Cooperativas" en la edición de una cooperativa existente
- **WHEN** visualiza el campo RUC
- **THEN** el campo aparece deshabilitado y no puede modificarse

#### Scenario: Intento de modificar el RUC por la API
- **GIVEN** una solicitud de edición que incluye un RUC distinto
- **WHEN** el backend la procesa
- **THEN** el RUC almacenado no cambia

### Requirement: Baja lógica y reactivación
El sistema DEBE desactivar y reactivar cooperativas mediante borrado lógico, previa confirmación, sin eliminar sus datos. Una cooperativa desactivada NO DEBE admitir nuevas rutas ni turnos, y sus administradores DEBEN perder el acceso a las funciones operativas de la cooperativa conservando los módulos de Pasajero.

#### Scenario: CP-58 Desactivar cooperativa activa
- **GIVEN** que el Administrador está en la pantalla "Cooperativas" y visualiza una cooperativa "Activa"
- **WHEN** selecciona "Desactivar" y confirma
- **THEN** el sistema cambia el estado a "Desactivada", muestra "Cooperativa desactivada exitosamente" y actualiza su estado visual

#### Scenario: CP-59 Reactivar cooperativa desactivada
- **GIVEN** que el Administrador está en la pantalla "Cooperativas" y visualiza una cooperativa "Desactivada"
- **WHEN** selecciona "Activar" y confirma
- **THEN** el sistema cambia el estado a "Activa" y muestra "Cooperativa activada exitosamente"

#### Scenario: Administrador de cooperativa desactivada
- **GIVEN** un usuario `ADMIN_COOPERATIVA` asignado a una cooperativa desactivada
- **WHEN** intenta usar una función operativa de la cooperativa
- **THEN** el sistema la rechaza y el usuario conserva el acceso a los módulos de Pasajero

### Requirement: Acción sobre cooperativa desactivada desde otra sesión
El sistema DEBE rechazar cualquier edición o cambio de administradores sobre una cooperativa desactivada, indicándolo al cliente para que lo redirija al Inicio.

#### Scenario: CP-60 Editar cooperativa desactivada en otra sesión
- **GIVEN** que el Administrador está en la pantalla "Cooperativas" con una cooperativa que fue desactivada en otra sesión
- **WHEN** intenta abrir su edición o guardar cambios
- **THEN** el sistema deniega la operación, redirige al Inicio y muestra "La cooperativa ha sido desactivada"

### Requirement: Auditoría de operaciones
El sistema DEBE registrar la creación, edición y cambio de estado de cooperativas con usuario, fecha y hora, acción, entidad y resultado, sin datos sensibles.

#### Scenario: Registro de auditoría
- **GIVEN** una operación administrativa sobre una cooperativa
- **WHEN** se completa con éxito o falla
- **THEN** queda un registro con usuario, fecha y hora, acción, entidad afectada y resultado
