# Especificación de Requisitos - Módulo de Seguridad
**Módulo:** Seguridad
**Submódulo:** 02 - Gestión de Usuarios, Roles y Permisos

---

## RF-05: Visualización de Módulos según Rol
**Prioridad:** Alta  
**Descripción:** El sistema debe permitir a los usuarios logueados visualizar un dashboard únicamente con los módulos a los que tienen acceso según su rol asignado.

### Criterios de Aceptación (Escenarios BDD)

**CP-23: Acceso a módulos del Administrador**
* **Dado** que un usuario con el rol de "Administrador" ha iniciado sesión exitosamente.
* **Cuando** visualiza el dashboard principal o el menú de navegación.
* **Entonces** el sistema le muestra únicamente el acceso a los módulos: Usuarios, Cooperativas, Rutas generales y Precios generales.

**CP-24: Acceso a módulos de Admin de Cooperativa**
* **Dado** que un usuario con el rol de "Administrador de Cooperativa" ha iniciado sesión exitosamente.
* **Cuando** visualiza el dashboard principal o el menú de navegación.
* **Entonces** el sistema le muestra únicamente el acceso a los módulos: Rutas de cooperativa, Buses, Turnos y Tarifas específicas.

**CP-25: Acceso a módulos de Secretaria de Cooperativa**
* **Dado** que un usuario con el rol de "Secretaria de Cooperativa" ha iniciado sesión exitosamente.
* **Cuando** visualiza el dashboard principal o el menú de navegación.
* **Entonces** el sistema le muestra únicamente el acceso al módulo: Reservas.

**CP-26: Acceso a módulos de Pasajero**
* **Dado** que un usuario con el rol de "Pasajero" ha iniciado sesión exitosamente.
* **Cuando** visualiza el dashboard principal o el menú de navegación.
* **Entonces** el sistema le muestra únicamente el acceso a los módulos: Reservas y Perfil.

**CP-27: Acceso a módulos por roles combinados (Administrador de Cooperativa y Pasajero)**
* **Dado** que un usuario que posee múltiples roles activos ("Administrador de Cooperativa" y "Pasajero") ha iniciado sesión exitosamente.
* **Cuando** visualiza el dashboard principal o el menú de navegación.
* **Entonces** el sistema le muestra el conjunto exacto de módulos permitidos por ambos roles: Rutas de cooperativa, Buses, Turnos, Tarifas específicas, Reservas y Perfil.

---

## RF-07: Asignación y Actualización de Roles
**Prioridad:** Alta  
**Descripción:** El sistema debe permitir al administrador asignar y actualizar los roles de los usuarios registrados. El sistema soporta múltiples roles por usuario, manteniendo el rol "Pasajero" como rol base permanente.

### Criterios de Aceptación (Escenarios BDD)

**CP-28: Asignación de rol adicional a un usuario (Admin Coop)**
* **Dado** que el Administrador se encuentra en el módulo "Usuarios" editando los roles de un usuario existente que solo es "Pasajero".
* **Cuando** marca la casilla del nuevo rol "Administrador de Cooperativa" y hace clic en "Guardar cambios".
* **Entonces** el sistema mantiene el rol "Pasajero" seleccionado (bloqueado contra edición), guarda la actualización en la base de datos y asigna el nuevo rol secundario al usuario.

**CP-29: Revocación de rol secundario a un usuario (Secretaria)**
* **Dado** que un usuario posee roles activos múltiples ("Pasajero" y "Secretaria de Cooperativa").
* **Cuando** el Administrador desde la vista de edición desmarca la casilla "Secretaria de Cooperativa" y hace clic en "Guardar cambios".
* **Entonces** el sistema actualiza los registros retirando el rol "Secretaria de Cooperativa", mantiene activo el rol "Pasajero" y revoca el acceso a los módulos correspondientes en la siguiente sesión del usuario.

---

## RF-08: Baja y Rehabilitación de Usuarios
**Prioridad:** Alta  
**Descripción:** El sistema debe permitir al administrador cambiar el estado de acceso de los usuarios (dar de baja o reactivar/habilitar), aplicando un borrado lógico y bloqueando el acceso.

### Criterios de Aceptación (Escenarios BDD)

**CP-30: Dar de baja a un usuario activo**
* **Dado** que el Administrador tiene sesión iniciada y localiza a un usuario en estado "Activo" dentro del módulo "Usuarios".
* **Cuando** selecciona la acción "Dar de baja" y confirma la operación.
* **Entonces** el sistema actualiza el estado del usuario a "Inactivo" mediante borrado lógico y muestra un mensaje confirmando que la baja fue exitosa.

**CP-31: Intento de inicio de sesión de un usuario dado de baja**
* **Dado** que una cuenta de usuario se encuentra en estado "Inactivo" (dado de baja).
* **Cuando** el usuario ingresa sus credenciales válidas en la pantalla de Login y hace clic en "Ingresar".
* **Entonces** el sistema rechaza la autenticación, no genera token de sesión y muestra el mensaje de alerta "Su cuenta se encuentra inactiva. Contacte al administrador".

**CP-32: Habilitar / Reactivar a un usuario inactivo**
* **Dado** que el Administrador localiza en el módulo "Usuarios" a un usuario en estado "Inactivo".
* **Cuando** ejecuta la acción "Habilitar usuario" y confirma la operación.
* **Entonces** el sistema actualiza el estado de la cuenta a "Activo", muestra un mensaje de éxito y permite que el usuario recupere su capacidad de iniciar sesión.