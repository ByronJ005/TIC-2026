## ADDED Requirements

### Requirement: Consulta del perfil propio
El sistema DEBE permitir a todo usuario autenticado consultar su perfil (Nombres, Apellidos, Email, Documento, Celular, Dirección y Fecha de nacimiento). Email y documento son de solo lectura. El módulo "Perfil" DEBE estar accesible para cualquier usuario autenticado.

#### Scenario: Usuario autenticado consulta su perfil
- **GIVEN** que el usuario está logueado
- **WHEN** abre el módulo "Perfil"
- **THEN** el sistema muestra sus datos actuales y los campos Email y Documento deshabilitados

#### Scenario: Acceso sin sesión
- **GIVEN** que no hay sesión activa
- **WHEN** se solicita el perfil
- **THEN** el sistema responde HTTP 401

### Requirement: Actualización de datos personales
El sistema DEBE permitir actualizar Nombres, Apellidos, Celular, Dirección y Fecha de nacimiento. Nombres y Apellidos son obligatorios (RN-06.1) y aplican las validaciones del registro (submódulo 01). Celular, Dirección y Fecha de nacimiento son opcionales y pueden vaciarse. La validación DEBE realizarse en el backend.

#### Scenario: CP-37(a) Actualizar perfil con datos válidos sin cambiar contraseña
- **GIVEN** que el usuario está logueado y se encuentra en el módulo "Perfil"
- **WHEN** modifica uno o más datos personales con valores válidos, deja vacíos los campos de contraseña y hace clic en "Actualizar perfil"
- **THEN** el sistema actualiza la información en la base de datos, conserva la contraseña actual y muestra "Perfil actualizado exitosamente"

#### Scenario: CP-42 Intentar actualizar perfil con campos obligatorios vacíos
- **GIVEN** que el usuario está logueado y se encuentra en el módulo "Perfil"
- **WHEN** elimina el contenido de Nombres o Apellidos, o los rellena solo con espacios, y hace clic en "Actualizar perfil"
- **THEN** el sistema impide la actualización, muestra "Los campos obligatorios no pueden quedar vacíos" y restaura en la interfaz los datos anteriores

#### Scenario: Nombres o Apellidos con caracteres inválidos o más de 50 caracteres
- **GIVEN** que el usuario está en el módulo "Perfil"
- **WHEN** ingresa en Nombres o Apellidos números, símbolos especiales o más de 50 caracteres
- **THEN** el sistema impide la actualización y muestra "Los nombres/apellidos proporcionados contienen caracteres inválidos"

#### Scenario: Actualización sin cambios
- **GIVEN** que el usuario no modificó ningún dato
- **WHEN** hace clic en "Actualizar perfil"
- **THEN** el sistema responde con éxito sin alterar los datos

#### Scenario: Intento de modificar Email o Documento
- **GIVEN** un request de actualización que incluye `email` o `document_number`
- **WHEN** el backend lo procesa
- **THEN** esos campos se ignoran y no se modifican

#### Scenario: Vaciar campos opcionales
- **GIVEN** un usuario con Celular, Dirección y Fecha de nacimiento guardados
- **WHEN** deja esos campos vacíos o con solo espacios y actualiza
- **THEN** el sistema los guarda como vacíos (nulos) sin error

### Requirement: Validación del celular (RN-06.2)
El Celular, cuando se informa, DEBE contener exactamente 10 dígitos numéricos, sin letras, espacios, guiones ni caracteres especiales. Si contiene caracteres no numéricos, el error DEBE ser el de caracteres no numéricos; si solo es numérico pero su longitud es distinta de 10, el de longitud.

#### Scenario: CP-38 Validar longitud del campo celular
- **GIVEN** que el usuario está en el módulo "Perfil"
- **WHEN** ingresa solo dígitos con una longitud distinta de 10 (por ejemplo 9 u 11) y hace clic en "Actualizar perfil"
- **THEN** el sistema impide la actualización y muestra "El número de celular debe tener exactamente 10 dígitos"

#### Scenario: CP-39 Validar restricción de caracteres no numéricos en el campo Celular
- **GIVEN** que el usuario está en el módulo "Perfil"
- **WHEN** ingresa letras, guiones, espacios o caracteres especiales y hace clic en "Actualizar perfil"
- **THEN** el sistema impide la actualización y muestra "El celular solo debe contener números"

#### Scenario: Celular con 10 dígitos
- **GIVEN** que el usuario está en el módulo "Perfil"
- **WHEN** ingresa exactamente 10 dígitos
- **THEN** el sistema acepta el valor

### Requirement: Validación de la dirección (RN-06.3)
La Dirección DEBE tener como máximo 150 caracteres (contados luego de eliminar espacios en los extremos).

#### Scenario: CP-40 Validar longitud del campo Dirección
- **GIVEN** que el usuario está en el módulo "Perfil"
- **WHEN** ingresa una dirección de más de 150 caracteres y hace clic en "Actualizar perfil"
- **THEN** el sistema impide la actualización y muestra "La dirección no puede exceder los 150 caracteres"

#### Scenario: Dirección de exactamente 150 caracteres
- **GIVEN** que el usuario está en el módulo "Perfil"
- **WHEN** ingresa una dirección de exactamente 150 caracteres
- **THEN** el sistema acepta el valor

### Requirement: Validación de la fecha de nacimiento (RN-06.4)
La Fecha de nacimiento, cuando se informa, DEBE estar entre el 1 de enero de 1900 y la fecha de hoy, ambos inclusive. El límite superior DEBE calcularse con la fecha actual al momento de validar y no estar fijado en un año concreto. No se permiten fechas futuras, aunque pertenezcan al año actual.

#### Scenario: CP-41 Validar rango permitido del campo Fecha de nacimiento
- **GIVEN** que el usuario está en el módulo "Perfil"
- **WHEN** ingresa una fecha anterior a 1900 o posterior a hoy y hace clic en "Actualizar perfil"
- **THEN** el sistema impide la actualización y muestra "La fecha de nacimiento debe estar entre 1900 y la fecha actual"

#### Scenario: Límites de la fecha
- **GIVEN** que el usuario está en el módulo "Perfil"
- **WHEN** ingresa 1/ene/1900 o la fecha de hoy
- **THEN** el sistema acepta el valor
- **AND** 31/dic/1899 o la fecha de mañana son rechazados

#### Scenario: Fecha futura dentro del año actual
- **GIVEN** que la fecha de hoy es anterior al 31 de diciembre del año actual
- **WHEN** el usuario ingresa el 31 de diciembre del año actual
- **THEN** el sistema impide la actualización con el mensaje del CP-41

#### Scenario: Fecha con formato inválido
- **GIVEN** un request con una fecha que no es válida (por ejemplo, 30 de febrero o texto)
- **WHEN** el backend la procesa
- **THEN** el sistema impide la actualización con el mensaje del CP-41

### Requirement: Cambio de contraseña desde el perfil
El sistema DEBE permitir cambiar la contraseña desde el perfil. La contraseña actual, la nueva contraseña y su confirmación son "todo o nada": si se completa cualquiera de los tres, los tres son obligatorios. La contraseña actual DEBE ser correcta, la nueva DEBE cumplir el formato del registro y DEBE ser distinta de la actual.

#### Scenario: CP-37(b) Cambiar contraseña con contraseña actual correcta
- **GIVEN** que el usuario está en el módulo "Perfil"
- **WHEN** ingresa su contraseña actual correcta, una nueva contraseña válida y distinta, la confirma y hace clic en "Actualizar perfil"
- **THEN** el sistema guarda la nueva contraseña y muestra "Contraseña actualizada exitosamente"

#### Scenario: Contraseña actual vacía al cambiarla
- **GIVEN** que el usuario completó la nueva contraseña o la confirmación
- **WHEN** deja la contraseña actual vacía o con solo espacios
- **THEN** el sistema impide la actualización, muestra "Debe ingresar su contraseña actual para cambiarla" y no modifica ningún dato

#### Scenario: Nueva contraseña o confirmación vacía
- **GIVEN** que el usuario completó la contraseña actual
- **WHEN** deja vacía la nueva contraseña o la confirmación
- **THEN** el sistema impide la actualización y marca el campo faltante como requerido

#### Scenario: Contraseña actual incorrecta
- **GIVEN** que el usuario completó los tres campos de contraseña
- **WHEN** la contraseña actual no coincide con la guardada
- **THEN** el sistema impide la actualización completa y muestra "La contraseña actual es incorrecta"

#### Scenario: Nueva contraseña igual a la actual
- **GIVEN** que la contraseña actual ingresada es correcta
- **WHEN** la nueva contraseña es igual a la actual
- **THEN** el sistema impide la actualización y muestra "La nueva contraseña debe ser diferente de la actual"

#### Scenario: Nueva contraseña con formato inválido
- **GIVEN** que la contraseña actual es correcta
- **WHEN** la nueva contraseña no cumple el formato del registro
- **THEN** el sistema impide la actualización y muestra el mensaje de contraseña inválida del registro

#### Scenario: Confirmación distinta de la nueva contraseña
- **GIVEN** que el usuario completó los tres campos
- **WHEN** la confirmación no coincide con la nueva contraseña
- **THEN** el sistema impide la actualización

#### Scenario: Error de contraseña no aplica cambios parciales
- **GIVEN** que el usuario modificó también otros datos personales
- **WHEN** el cambio de contraseña falla por cualquier motivo
- **THEN** ninguno de los cambios del request se persiste

#### Scenario: Sesiones tras cambiar la contraseña
- **GIVEN** un usuario con dos sesiones activas
- **WHEN** cambia la contraseña desde una de ellas
- **THEN** la sesión actual continúa con un token nuevo devuelto por el sistema y la otra sesión recibe HTTP 401 en su siguiente request

