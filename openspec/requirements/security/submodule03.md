# Especificación de Requisitos - Módulo de Seguridad

**Módulo:** Seguridad
**Submódulo:** 03 - Gestión de Perfil y Recuperación de Cuenta
**Metodología:** Specification-Driven Development (SDD)

## RF-03: Restablecer Contraseña

**Prioridad:** Alta

**Descripción:** El sistema debe permitir a todos los usuarios restablecer su contraseña en caso de olvido, mediante el envío de un enlace de recuperación al correo electrónico registrado.

### Reglas de Negocio Específicas
* **RN-03.1 (Vigencia y Unicidad del Enlace):** El enlace de restablecimiento contiene un token seguro de un solo uso con vigencia de 30 minutos. La generación de un nuevo enlace invalida cualquier enlace anterior no utilizado.
* **RN-03.2 (Cuentas Inactivas):** Las solicitudes para cuentas registradas pero inactivas no envían correo ni generan tokens, pero devuelven la misma respuesta genérica que una cuenta activa para no revelar su estado.
* **RN-03.3 (Invalidación de Sesiones):** Tras restablecer la contraseña exitosamente, todas las sesiones activas previas del usuario quedan automáticamente revocadas.

### Criterios de Aceptación (Escenarios BDD)

**CP-33: Enviar correo electrónico de reestablecimiento de contraseña**

* **Dado** que el usuario ha olvidado su contraseña y se encuentra en la pantalla de Inicio de sesión.
* **Cuando** hace click en "¿Olvidaste tu contraseña?" e ingresa su correo electrónico válido de una cuenta activa.
* **Entonces** el sistema valida el correo ingresado, envía el mensaje de restablecimiento y muestra el mensaje: "Hemos procesado tu solicitud. Si el correo corresponde a una cuenta activa, recibirás un enlace en los próximos minutos."

**CP-34: Actualizar contraseña a partir del enlace de restablecimiento**

* **Dado** que el usuario ha recibido el correo de restablecimiento de contraseña dentro de los 30 minutos de vigencia.
* **Cuando** hace clic en el enlace recibido e ingresa una nueva contraseña que cumple el formato de seguridad.
* **Entonces** el sistema guarda la nueva contraseña, revoca sesiones previas, marca el enlace como utilizado y permite al usuario iniciar sesión con sus nuevas credenciales.

**CP-35: Intentar restablecimiento de contraseña con email no registrado**

* **Dado** que el usuario ha olvidado su contraseña y se encuentra en la pantalla de Inicio de sesión.
* **Cuando** hace clic en "¿Olvidaste tu contraseña?" e ingresa un correo electrónico no registrado en el sistema.
* **Entonces** el sistema no envía ningún correo y muestra el mensaje de error: "El correo ingresado no corresponde a una cuenta registrada en el sistema".

**CP-36: Intentar restablecimiento de contraseña sin colocar el email**

* **Dado** que el usuario ha olvidado su contraseña y se encuentra en la pantalla de Inicio de sesión.
* **Cuando** deja el campo de correo electrónico vacío o solo con espacios y hace clic en "Enviar enlace".
* **Entonces** el sistema no envía ningún correo y muestra el mensaje de error: "Se requiere el correo electrónico".

**CP-36.1: Intentar restablecimiento con cuenta inactiva**

* **Dado** que un usuario posee una cuenta registrada pero en estado "Inactivo".
* **Cuando** solicita el restablecimiento ingresando su correo electrónico.
* **Entonces** el sistema muestra el mensaje oficial del CP-33 y no envía ningún correo electrónico ni genera tokens en la base de datos.

**CP-36.2: Intentar restablecimiento con enlace vencido o reutilizado**

* **Dado** que el usuario intenta usar un enlace de restablecimiento cuya vigencia de 30 minutos expiró o que ya fue utilizado previamente.
* **Cuando** accede al enlace o intenta guardar la nueva contraseña.
* **Entonces** el sistema rechaza la operación mostrando el mensaje: "El enlace de restablecimiento es inválido o ha expirado" y ofrece solicitar uno nuevo.

---

## RF-06: Actualización de Información de Perfil

**Prioridad:** Media

**Descripción:** El sistema debe permitir a todos los usuarios autenticados consultar y actualizar su información de perfil (Nombres, Apellidos, Contraseña, Celular, Dirección y Fecha de nacimiento). Los campos Correo electrónico y Número de documento son de solo lectura.

### Reglas de Negocio Específicas
* **RN-06.1 (Campos Obligatorios de Datos Personales):** Los campos Nombres y Apellidos son obligatorios y no pueden quedar vacíos o con solo espacios. Celular, Dirección y Fecha de nacimiento son opcionales y pueden vaciarse.
* **RN-06.2 (Formato de Celular):** El campo celular, si se ingresa, debe contener exactamente 10 dígitos numéricos. No se admiten letras, espacios ni caracteres especiales.
* **RN-06.3 (Longitud de Dirección):** El campo dirección está limitado a un máximo de 150 caracteres.
* **RN-06.4 (Restricción de Fecha):** La fecha de nacimiento, si se ingresa, debe estar comprendida entre el 1 de enero de 1900 y la fecha actual del día de validación (no se admiten fechas futuras).
* **RN-06.5 (Regla Todo o Nada en Contraseña):** La actualización de contraseña es opcional. Si el usuario ingresa información en cualquiera de los campos de contraseña (actual, nueva o confirmación), es obligatorio completar los tres campos. Se requiere ingresar la contraseña actual correcta, y la nueva contraseña debe ser distinta a la actual y cumplir las validaciones de seguridad de registro.

### Criterios de Aceptación (Escenarios BDD)

**CP-37: Actualizar perfil con datos válidos (sin cambiar contraseña)**

* **Dado** que el usuario está logueado y se encuentra en el módulo "Perfil".
* **Cuando** modifica cualquiera de sus datos personales permitidos (Nombres, Apellidos, Celular, Dirección o Fecha de nacimiento) con datos válidos, dejando vacíos los campos de contraseña, y hace clic en "Actualizar perfil".
* **Entonces** el sistema actualiza la información en la base de datos, conserva la contraseña actual y muestra la notificación de éxito: "Perfil actualizado exitosamente".

**CP-37b: Cambiar contraseña desde el perfil con confirmación y contraseña actual**

* **Dado** que el usuario está logueado y se encuentra en el módulo "Perfil".
* **Cuando** ingresa su contraseña actual correcta, una nueva contraseña válida que no sea igual a la actual, confirma la nueva contraseña y hace clic en "Actualizar perfil".
* **Entonces**  

**CP-38: Validar longitud del campo celular**

* **Dado** que el usuario está logueado y se encuentra en el módulo "Perfil".
* **Cuando** ingresa un número de celular compuesto únicamente por números pero con una longitud distinta a 10 dígitos y hace clic en "Actualizar perfil".
* **Entonces** el sistema impide la actualización y muestra el mensaje de error: "El número de celular debe tener exactamente 10 dígitos".

**CP-39: Validar restricción de caracteres no numéricos en el campo Celular**

* **Dado** que el usuario está logueado y se encuentra en el módulo "Perfil".
* **Cuando** intenta ingresar letras, guiones, espacios o caracteres especiales en el campo celular y hace clic en "Actualizar perfil".
* **Entonces** el sistema impide la actualización y muestra el mensaje de error: "El celular solo debe contener números".

**CP-40: Validar longitud del campo Dirección**

* **Dado** que el usuario está logueado y se encuentra en el módulo "Perfil".
* **Cuando** ingresa una dirección extensa que supera el límite permitido de 150 caracteres y hace clic en "Actualizar perfil".
* **Entonces** el sistema impide la actualización y muestra el mensaje de error: "La dirección no puede exceder los 150 caracteres".

**CP-41: Validar rango permitido del campo Fecha de nacimiento**

* **Dado** que el usuario está logueado y se encuentra en el módulo "Perfil".
* **Cuando** intenta seleccionar una fecha de nacimiento fuera del rango permitido (anterior a 1900 o posterior a la fecha actual).
* **Entonces** el sistema impide la actualización y muestra el mensaje de error: "La fecha de nacimiento debe estar entre 1900 y la fecha actual".

**CP-42: Intentar actualizar perfil con campos obligatorios vacíos**

* **Dado** que el usuario está logueado y se encuentra en el módulo "Perfil".
* **Cuando** elimina el contenido de los campos obligatorios (Nombres o Apellidos) o los rellena exclusivamente con espacios en blanco y hace clic en "Actualizar perfil".
* **Entonces** el sistema impide la actualización, muestra el mensaje de error "Los campos obligatorios no pueden quedar vacíos", y coloca nuevamente los datos anteriores en la interfaz.

**CP-43: Intentar cambiar contraseña sin ingresar la contraseña actual**

* **Dado** que el usuario está en el módulo "Perfil" e ingresa datos en la nueva contraseña o confirmación.
* **Cuando** deja el campo de contraseña actual vacío y hace clic en "Actualizar perfil".
* **Entonces** el sistema impide la actualización y muestra el mensaje de error: "Debe ingresar su contraseña actual para cambiarla".

**CP-44: Intentar cambiar contraseña con contraseña actual incorrecta**

* **Dado** que el usuario completa los tres campos de contraseña.
* **Cuando** introduce una contraseña actual incorrecta y hace clic en "Actualizar perfil".
* **Entonces** el sistema impide la actualización y muestra el mensaje de error: "La contraseña actual es incorrecta".

**CP-45: Intentar cambiar contraseña repitiendo la contraseña actual**

* **Dado** que el usuario introduce su contraseña actual correcta.
* **Cuando** introduce en la nueva contraseña el mismo valor que la contraseña actual y hace clic en "Actualizar perfil".
* **Entonces** el sistema impide la actualización y muestra el mensaje de error: "La nueva contraseña debe ser diferente de la actual".
