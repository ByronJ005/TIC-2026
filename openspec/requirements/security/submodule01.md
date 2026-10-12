# Especificación de Requisitos - Módulo de Seguridad
**Módulo:** Seguridad
**Submódulo:** 01 - Autenticación y Registro de Usuarios

---

## RF-01: Registro de Usuarios
**Prioridad:** Alta  
**Descripción:** El sistema debe permitir a los usuarios registrarse en la plataforma ingresando Tipo de documento, Número de documento, Nombres, Apellidos, Email, y Contraseña.

### Criterios de Aceptación (Escenarios BDD)

**CP-01: Registro de usuario con datos válidos**
* **Dado** que el usuario no tiene cuenta y se encuentra en el formulario de registro.
* **Cuando** llena todos los campos obligatorios con datos válidos y hace clic en el botón "Crear cuenta".
* **Entonces** el sistema crea la cuenta correctamente, lo registra en la base de datos y muestra el mensaje de éxito "Cuenta creada satisfactoriamente".

**CP-02: Validación de formato de Cédula**
* **Dado** que el usuario se encuentra en el formulario de registro.
* **Cuando** ingresa un número de cédula con un formato inválido (no cumple el algoritmo de cédula ecuatoriana) y hace clic en "Crear cuenta".
* **Entonces** el sistema impide el registro y muestra un mensaje de error indicando "El número de documento proporcionado es inválido".

**CP-03: Validación de formato de Pasaporte**
* **Dado** que el usuario se encuentra en el formulario de registro.
* **Cuando** ingresa un número de pasaporte con un formato inválido (no es alfanumérico) y hace clic en "Crear cuenta".
* **Entonces** el sistema impide el registro y muestra un mensaje de error indicando "El número de documento proporcionado es inválido".

**CP-04: Validación de caracteres en Nombres/Apellidos**
* **Dado** que el usuario está completando el formulario de registro.
* **Cuando** ingresa caracteres fuera de los permitidos (espacios, guiones medios y apostrofes) en los campos de Nombres/Apellidos, o ingresa un texto de más de 50 caracteres y hace clic en "Crear cuenta".
* **Entonces** el sistema impide el registro y muestra el mensaje de error "Los nombres/apellidos proporcionados contienen caracteres inválidos".

**CP-05: Validación de formato de correo electrónico**
* **Dado** que el usuario se encuentra en el formulario de registro.
* **Cuando** ingresa un correo electrónico sin el símbolo '@' o sin un dominio de nivel superior válido y hace clic en "Crear cuenta".
* **Entonces** el sistema impide el registro y muestra el mensaje de error "Correo electrónico inválido".

**CP-06: Validación de formato de contraseña**
* **Dado** que el usuario está en el formulario de registro.
* **Cuando** ingresa una contraseña que no contenga una mayúscula, minúscula, número y un carácter especial opcional.
* **Entonces** el sistema impide el registro y muestra el mensaje de error "La contraseña debe incluir al menos una mayúscula, minúscula, número y carácter especial opcional".

**CP-07: Validación de campos obligatorios vacíos y espacios en blanco**
* **Dado** que el usuario se encuentra en la pantalla de registro.
* **Cuando** deja los campos obligatorios vacíos o los rellena únicamente con espacios en blanco y hace clic en "Crear cuenta".
* **Entonces** el sistema no procesa el registro y marca los campos faltantes con un mensaje indicando que son requeridos.

---

## RF-02: Inicio de Sesión
**Prioridad:** Alta  
**Descripción:** El sistema debe permitir a todos los usuarios iniciar sesión mediante su Email y Contraseña.

### Criterios de Aceptación (Escenarios BDD)

**CP-08: Inicio de sesión exitoso**
* **Dado** que un usuario previamente registrado se encuentra en la pantalla de inicio de sesión.
* **Cuando** ingresa su correo electrónico y contraseña correctos, y hace clic en "Ingresar".
* **Entonces** el sistema lo autentica correctamente y lo redirige a su respectivo Dashboard.

**CP-09: Inicio de sesión con credenciales incorrectas**
* **Dado** que el usuario se encuentra en la pantalla de inicio de sesión.
* **Cuando** ingresa su correo electrónico válido pero introduce una contraseña incorrecta y hace clic en "Ingresar".
* **Entonces** el sistema deniega el acceso y muestra un mensaje de alerta genérico ("Credenciales incorrectas").

**CP-10: Inicio de sesión con campos vacíos**
* **Dado** que el usuario se encuentra en la pantalla de inicio de sesión.
* **Cuando** intenta iniciar sesión dejando los campos de correo o contraseña vacíos, o llenos con espacios en blanco.
* **Entonces** el sistema impide el envío del formulario y requiere que los campos sean completados.

**CP-11: Email insensible a mayúsculas y con espacios laterales**
* **Dado** que existe la cuenta j.perez@email.com.
* **Cuando** el usuario ingresa " J.Perez@Email.com " con la contraseña correcta.
* **Entonces** el sistema normaliza el email y permite el acceso.

**CP-12: Acceso a ruta protegida sin sesión**
* **Dado** que no hay sesión activa.
* **Cuando** se abre directamente la URL /dashboard.
* **Entonces** el sistema redirige a Login y no muestra información protegida.

**CP-13: Visitar /login con sesión activa**
* **Dado** que el usuario ya tiene sesión activa.
* **Cuando** navega manualmente a /login.
* **Entonces** el sistema lo redirige a su Dashboard.

---

## RF-04: Cierre de Sesión
**Prioridad:** Alta  
**Descripción:** El sistema debe permitir a todos los usuarios cerrar su sesión activa.

### Criterios de Aceptación (Escenarios BDD)

**CP-14: Cierre de sesión manual exitoso**
* **Dado** que el usuario (independientemente de su rol) tiene una sesión activa y se encuentra navegando dentro del dashboard del sistema.
* **Cuando** hace clic en la opción "Cerrar sesión" desde su menú de perfil.
* **Entonces** el sistema finaliza la sesión activa de forma segura y redirige al usuario inmediatamente a la pantalla principal de inicio de sesión.

**CP-15: Restricción de acceso mediante botón "Atrás" post-cierre**
* **Dado** que el usuario ha cerrado su sesión correctamente y se encuentra visualizando la pantalla de inicio de sesión.
* **Cuando** intenta utilizar el botón "Atrás" de su navegador web para volver a las páginas protegidas que estaba viendo anteriormente.
* **Entonces** el sistema deniega el acceso a la información, invalida cualquier vista guardada en caché y mantiene al usuario en la pantalla de inicio de sesión.

**CP-16: Comportamiento del cierre de sesión en múltiples pestañas**
* **Dado** que el usuario tiene el sistema abierto con su sesión activa simultáneamente en dos pestañas diferentes del navegador.
* **Cuando** el usuario cierra la sesión desde la primera pestaña y luego intenta ejecutar una acción (como guardar un dato o recargar) en la segunda pestaña.
* **Entonces** el sistema detecta que el token de autenticación ya no es válido y redirige al usuario a la pantalla de inicio de sesión mostrando un mensaje de "Sesión expirada".

**CP-17: Logout con sesión ya expirada o invalidada**
* **Dado** que la sesión ya no es válida (expirada o cerrada en otra pestaña).
* **Cuando** el usuario hace clic en "Cerrar sesión".
* **Entonces** el sistema no muestra error técnico y lo lleva a Login.