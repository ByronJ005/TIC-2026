## ADDED Requirements

### Requirement: Solicitud de enlace de restablecimiento
El sistema DEBE permitir a cualquier usuario solicitar un enlace de restablecimiento de contraseña ingresando su correo electrónico desde la pantalla de Inicio de sesión ("¿Olvidaste tu contraseña?"). El correo DEBE normalizarse (espacios y mayúsculas) antes de buscarlo. El enlace DEBE enviarse únicamente si el correo pertenece a una cuenta registrada y activa.

#### Scenario: CP-33 Enviar correo electrónico de reestablecimiento de contraseña
- **GIVEN** que el usuario ha olvidado su contraseña y se encuentra en la pantalla de Inicio de sesión
- **WHEN** hace clic en "¿Olvidaste tu contraseña?" e ingresa su correo electrónico válido de una cuenta activa
- **THEN** el sistema valida el correo, envía el mensaje de reestablecimiento y muestra "Hemos procesado tu solicitud. Si el correo corresponde a una cuenta activa, recibirás un enlace en los próximos minutos."

#### Scenario: CP-35 Intentar restablecimiento de contraseña con email no registrado
- **GIVEN** que el usuario se encuentra en la pantalla de Inicio de sesión
- **WHEN** hace clic en "¿Olvidaste tu contraseña?" e ingresa un correo electrónico no registrado en el sistema
- **THEN** el sistema no envía ningún correo y muestra el error "El correo ingresado no corresponde a una cuenta registrada en el sistema"

#### Scenario: CP-36 Intentar restablecimiento de contraseña sin colocar el email
- **GIVEN** que el usuario se encuentra en la pantalla de Inicio de sesión
- **WHEN** deja el campo de correo vacío o solo con espacios y hace clic en "¿Olvidaste tu contraseña?"
- **THEN** el sistema muestra el error "Se requiere el correo electrónico" y no envía ningún correo

#### Scenario: Cuenta inactiva solicita restablecimiento
- **GIVEN** que existe una cuenta con el correo registrado pero en estado "Inactivo"
- **WHEN** se solicita el restablecimiento con ese correo
- **THEN** el sistema muestra el mismo mensaje de éxito del CP-33 y NO envía ningún correo ni crea un token

#### Scenario: Correo con formato inválido
- **GIVEN** que el usuario se encuentra en la pantalla de recuperación
- **WHEN** ingresa un texto que no cumple el formato de correo (por ejemplo, sin "@")
- **THEN** el sistema muestra "Correo electrónico inválido", no consulta la base de datos de cuentas y no envía correo

#### Scenario: Correo con mayúsculas y espacios
- **GIVEN** una cuenta activa registrada con `usuario@dominio.com`
- **WHEN** se solicita el restablecimiento con `"  Usuario@Dominio.COM "`
- **THEN** el sistema trata la solicitud como correo válido de esa cuenta y envía el enlace

#### Scenario: El fallo del proveedor de correo no revela información
- **GIVEN** una cuenta activa y un proveedor de correo que falla al enviar
- **WHEN** se solicita el restablecimiento
- **THEN** el sistema responde sin exponer detalles técnicos ni stack traces al usuario y registra el error sin datos sensibles

### Requirement: Token de restablecimiento de un solo uso con vigencia
El enlace de restablecimiento DEBE contener un token aleatorio de un solo uso con vigencia de 30 minutos (configurable por `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES`). El sistema DEBE almacenar únicamente el hash del token. Al generar un nuevo token para un usuario, los tokens anteriores aún vigentes DEBEN quedar invalidados.

#### Scenario: Token vigente
- **GIVEN** un token generado hace menos de 30 minutos y no usado
- **WHEN** se usa para restablecer la contraseña
- **THEN** el sistema acepta el token

#### Scenario: Token vencido
- **GIVEN** un token generado hace 30 minutos o más
- **WHEN** se usa para restablecer la contraseña
- **THEN** el sistema rechaza la operación con "El enlace de restablecimiento es inválido o ha expirado" y no modifica la contraseña

#### Scenario: Token reutilizado
- **GIVEN** un token que ya fue usado para restablecer la contraseña
- **WHEN** se intenta usar de nuevo
- **THEN** el sistema rechaza la operación con "El enlace de restablecimiento es inválido o ha expirado"

#### Scenario: Token invalidado por una nueva solicitud
- **GIVEN** un usuario que solicitó dos enlaces consecutivos
- **WHEN** intenta usar el primer enlace
- **THEN** el sistema lo rechaza y solo el segundo enlace es válido

#### Scenario: Token inexistente o manipulado
- **GIVEN** un token que no corresponde a ningún registro (alterado, truncado o vacío)
- **WHEN** se intenta restablecer la contraseña
- **THEN** el sistema responde con el mismo mensaje de enlace inválido o expirado

#### Scenario: Token de una cuenta que fue desactivada
- **GIVEN** un token vigente cuya cuenta fue dada de baja después de generarlo
- **WHEN** se intenta restablecer la contraseña
- **THEN** el sistema rechaza la operación con el mensaje de enlace inválido o expirado

#### Scenario: El token no se almacena en claro
- **GIVEN** un token recién generado
- **WHEN** se inspecciona la tabla `password_reset_tokens`
- **THEN** solo existe el hash del token y no el valor enviado por correo

### Requirement: Definir nueva contraseña desde el enlace
El sistema DEBE permitir definir una nueva contraseña a partir de un enlace válido. La nueva contraseña DEBE cumplir las mismas reglas de formato del registro (submódulo 01). Al completarse, el sistema DEBE guardar la contraseña, marcar el token como usado, actualizar `password_changed_at` e invalidar las sesiones previas del usuario.

#### Scenario: CP-34 Actualizar contraseña a partir del enlace de restablecimiento
- **GIVEN** que el usuario recibió el correo de restablecimiento
- **WHEN** hace clic en el enlace e ingresa una nueva contraseña válida
- **THEN** el sistema guarda la nueva contraseña, muestra "Contraseña restablecida exitosamente" y permite iniciar sesión con las nuevas credenciales (la contraseña anterior deja de funcionar)

#### Scenario: Nueva contraseña con formato inválido
- **GIVEN** un enlace vigente
- **WHEN** el usuario ingresa una contraseña que no cumple el formato (menos de 8 caracteres, sin mayúscula, minúscula o número)
- **THEN** el sistema muestra el mensaje de contraseña inválida del registro, no consume el token y no modifica la contraseña

#### Scenario: Nueva contraseña vacía o solo espacios
- **GIVEN** un enlace vigente
- **WHEN** el usuario deja la nueva contraseña vacía o con espacios
- **THEN** el sistema muestra "Este campo es requerido" y el token sigue vigente

#### Scenario: Confirmación de contraseña distinta
- **GIVEN** un enlace vigente
- **WHEN** la nueva contraseña y su confirmación no coinciden
- **THEN** el sistema impide el envío en la interfaz y no modifica la contraseña

#### Scenario: Sesiones previas invalidadas tras el restablecimiento
- **GIVEN** un usuario con una sesión activa emitida antes del restablecimiento
- **WHEN** completa el restablecimiento de contraseña
- **THEN** cualquier token emitido antes de ese momento recibe HTTP 401 en el siguiente request

#### Scenario: Enlace inválido en la interfaz
- **GIVEN** un usuario que abre `/reset-password` con un token inválido, vencido o sin token
- **WHEN** la pantalla carga o envía el formulario
- **THEN** muestra el mensaje de enlace inválido o expirado y ofrece volver a solicitar un enlace

### Requirement: Envío de correo desacoplado y configurable
El sistema DEBE enviar el correo mediante un puerto `EmailSender` cuya implementación SMTP se configure exclusivamente por variables de entorno. El correo NO DEBE incluir la contraseña ni registrarse el token en logs.

#### Scenario: Correo con enlace al frontend
- **GIVEN** una solicitud válida de una cuenta activa
- **WHEN** se envía el correo
- **THEN** el mensaje se envía desde `MAIL_FROM_ADDRESS` y contiene un enlace `FRONTEND_URL/reset-password?token=<token>` y la vigencia en minutos

#### Scenario: Configuración SMTP ausente
- **GIVEN** que las variables SMTP no están configuradas
- **WHEN** se solicita un restablecimiento
- **THEN** el sistema registra el error de configuración sin exponer credenciales y responde sin detalles técnicos

