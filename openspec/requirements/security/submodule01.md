# Especificación de Requisitos - Módulo de Seguridad
**Módulo:** Seguridad  
**Submódulo:** 01 - Autenticación y Registro de Usuarios  
**Metodología:** Specification-Driven Development (SDD)  

---

## RF-01: Registro de Usuarios
**Prioridad:** Alta  
**Descripción:** El sistema debe permitir a los usuarios registrarse en la plataforma ingresando Tipo de documento, Número de documento, Nombres, Apellidos, Email y Contraseña.

### Criterios de Aceptación (Escenarios BDD)

**CP-01: Registrar usuario con datos válidos**
* **Dado** que el usuario no tiene cuenta y se encuentra en el formulario de registro.
* **Cuando** llena todos los campos obligatorios con datos válidos y hace clic en el botón "Crear cuenta".
* **Entonces** el sistema crea la cuenta correctamente, lo registra en la base de datos y muestra el mensaje de éxito "Cuenta creada satisfactoriamente".

**CP-02: Verificar validación de algoritmo de cédula ecuatoriana**
* **Dado** que el usuario no tiene cuenta y se encuentra en el formulario de registro.
* **Cuando** ingresa un número de cédula inválido (que no cumple con el algoritmo de módulo 10) y hace clic en "Crear cuenta".
* **Entonces** el sistema impide el registro y muestra un mensaje de error indicando "El número de documento proporcionado es inválido".

**CP-03: Verificar validación de longitud de cédula**
* **Dado** que el usuario no tiene cuenta y se encuentra en el formulario de registro.
* **Cuando** ingresa un número de cédula inválido (con una longitud distinta a 10 dígitos) y hace clic en "Crear cuenta".
* **Entonces** el sistema impide el registro y muestra un mensaje de error indicando "El número de documento proporcionado es inválido".

**CP-04: Verificar validación de cédula con caracteres no numéricos**
* **Dado** que el usuario no tiene cuenta y se encuentra en el formulario de registro.
* **Cuando** ingresa un número de cédula inválido (que contiene letras o caracteres especiales) y hace clic en "Crear cuenta".
* **Entonces** el sistema impide el registro y muestra un mensaje de error indicando "El número de documento proporcionado es inválido".

**CP-05: Verificar validación de formato numérico/alfanumérico de pasaporte**
* **Dado** que el usuario no tiene cuenta y se encuentra en el formulario de registro.
* **Cuando** ingresa un número de pasaporte con un formato inválido (solo contiene letras o caracteres no permitidos) y hace clic en "Crear cuenta".
* **Entonces** el sistema impide el registro y muestra un mensaje de error indicando "El número de documento proporcionado es inválido".

**CP-06: Verificar validación de longitud de pasaporte**
* **Dado** que el usuario no tiene cuenta y se encuentra en el formulario de registro.
* **Cuando** ingresa un número de pasaporte con una longitud incorrecta según el estándar y hace clic en "Crear cuenta".
* **Entonces** el sistema impide el registro y muestra un mensaje de error indicando "El número de documento proporcionado es inválido".

**CP-07: Verificar validación de caracteres en Nombres/Apellidos**
* **Dado** que el usuario no tiene cuenta y se encuentra en el formulario de registro.
* **Cuando** ingresa en los campos de Nombres o Apellidos un texto no válido (que contiene números o caracteres fuera de los permitidos, como símbolos especiales) y hace clic en "Crear cuenta".
* **Entonces** el sistema impide el registro y muestra el mensaje de error "Los nombres/apellidos proporcionados contienen caracteres inválidos".

**CP-08: Verificar validación de longitud de texto en Nombres/Apellidos**
* **Dado** que el usuario no tiene cuenta y se encuentra en el formulario de registro.
* **Cuando** ingresa en los campos de Nombres o Apellidos un texto que excede los 50 caracteres y hace clic en "Crear cuenta".
* **Entonces** el sistema impide el registro y muestra el mensaje de error "Los nombres/apellidos proporcionados contienen caracteres inválidos".

**CP-09: Verificar validación de símbolo '@' en el correo electrónico**
* **Dado** que el usuario no tiene cuenta y se encuentra en el formulario de registro.
* **Cuando** ingresa un correo electrónico inválido (sin el símbolo '@') y hace clic en "Crear cuenta".
* **Entonces** el sistema impide el registro y muestra el mensaje de error "Correo electrónico inválido".

**CP-10: Verificar validación de dominio de nivel superior en el correo electrónico**
* **Dado** que el usuario no tiene cuenta y se encuentra en el formulario de registro.
* **Cuando** ingresa un correo electrónico inválido (sin un dominio de nivel superior válido) y hace clic en "Crear cuenta".
* **Entonces** el sistema impide el registro y muestra el mensaje de error "Correo electrónico inválido".

**CP-11: Verificar validación de formato de contraseña**
* **Dado** que el usuario no tiene cuenta y se encuentra en el formulario de registro.
* **Cuando** ingresa una contraseña que no cumple con el formato requerido (al menos una mayúscula, minúscula, número y de mínimo 8 caracteres).
* **Entonces** el sistema impide el registro y muestra el mensaje de error "La contraseña debe incluir al menos una mayúscula, minúscula, número y carácter especial opcional".

**CP-12: Verificar validación de campos obligatorios vacíos y espacios en blanco**
* **Dado** que el usuario no tiene cuenta y se encuentra en el formulario de registro.
* **Cuando** deja los campos obligatorios vacíos o los rellena únicamente con espacios en blanco y hace clic en "Crear cuenta".
* **Entonces** el sistema no procesa el registro y marca los campos faltantes con un mensaje indicando que son requeridos.

---

## RF-02: Inicio de Sesión
**Prioridad:** Alta  
**Descripción:** El sistema debe permitir a todos los usuarios iniciar sesión mediante su Email y Contraseña.

### Criterios de Aceptación (Escenarios BDD)

**CP-13: Iniciar sesión con credenciales correctas**
* **Dado** que un usuario previamente registrado se encuentra en la pantalla de inicio de sesión.
* **Cuando** ingresa su correo electrónico y contraseña correctos, y hace clic en "Ingresar".
* **Entonces** el sistema lo autentica correctamente y lo redirige a su respectivo Dashboard.

**CP-14: Iniciar sesión con credenciales incorrectas**
* **Dado** que el usuario se encuentra en la pantalla de inicio de sesión.
* **Cuando** ingresa su correo electrónico válido pero introduce una contraseña incorrecta y hace clic en "Ingresar".
* **Entonces** el sistema deniega el acceso y muestra un mensaje de alerta genérico ("Credenciales incorrectas").

**CP-15: Iniciar sesión con campos vacíos**
* **Dado** que el usuario se encuentra en la pantalla de inicio de sesión.
* **Cuando** intenta iniciar sesión dejando los campos de correo o contraseña vacíos, o llenos con espacios en blanco.
* **Entonces** el sistema impide el envío del formulario y requiere que los campos sean completados.

**CP-16: Verificar que el campo "Correo electrónico" sea insensible a mayúsculas**
* **Dado** que el usuario se encuentra en la pantalla de inicio de sesión.
* **Cuando** ingresa su correo electrónico utilizando letras mayúsculas junto con la contraseña correcta.
* **Entonces** el sistema normaliza el email y permite el acceso.

**CP-17: Verificar el acceso a ruta protegida sin sesión**
* **Dado** que no hay sesión activa.
* **Cuando** el usuario abre directamente la URL /dashboard.
* **Entonces** el sistema redirige a Login y no muestra información protegida.

**CP-18: Visitar /login con sesión activa**
* **Dado** que el usuario ya tiene sesión activa.
* **Cuando** navega manualmente a /login.
* **Entonces** el sistema lo redirige a su Dashboard.

---

## RF-04: Cierre de Sesión
**Prioridad:** Alta  
**Descripción:** El sistema debe permitir a todos los usuarios cerrar su sesión activa.

### Criterios de Aceptación (Escenarios BDD)

**CP-19: Cerrar sesión de forma manual**
* **Dado** que el usuario (independientemente de su rol) tiene una sesión activa y se encuentra en el dashboard.
* **Cuando** hace clic en el botón "Cerrar sesión".
* **Entonces** el sistema finaliza la sesión activa de forma segura y redirige al usuario inmediatamente a la pantalla principal de inicio de sesión.

**CP-20: Verificar restricción de acceso mediante botón "Atrás" post-cierre**
* **Dado** que el usuario ha cerrado su sesión correctamente y se encuentra visualizando la pantalla de inicio de sesión.
* **Cuando** intenta utilizar el botón "Atrás" de su navegador web para volver a las páginas protegidas que estaba viendo anteriormente.
* **Entonces** el sistema deniega el acceso y mantiene al usuario en la pantalla de inicio de sesión.

**CP-21: Verificar comportamiento del cierre de sesión en múltiples pestañas**
* **Dado** que el usuario tiene el sistema abierto con su sesión activa simultáneamente en dos pestañas diferentes del navegador.
* **Cuando** el usuario cierra la sesión desde la primera pestaña y luego intenta ejecutar alguna acción (acceder a su perfil o recargar la página) en la segunda pestaña.
* **Entonces** el sistema detecta que el token de autenticación ya no es válido y redirige al usuario a la pantalla de inicio de sesión mostrando un mensaje de "Sesión expirada".

**CP-22: Verificar cierre de sesión cuando la misma ya ha expirado**
* **Dado** que la sesión del usuario ya no es válida (expirada o cerrada en otra pestaña).
* **Cuando** el usuario hace clic en "Cerrar sesión".
* **Entonces** el sistema no muestra error y lo lleva a Login.
