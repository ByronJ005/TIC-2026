# Especificación de Requisitos - Módulo de Cooperativas

**Módulo:** Cooperativas  
**Submódulo:** 04 - Gestión de Cooperativas y Asignación de Administradores de cooperativa   

---

## RF-09: Gestión de Cooperativas

**Prioridad:** Alta  
**Descripción:** El sistema debe permitir al Administrador General registrar, consultar, editar y cambiar el estado (baja lógica y reactivación) de las cooperativas que operan en el terminal terrestre. La vista principal permite alternar entre un formato de tabla y una cuadrícula de tarjetas informativas.

### Reglas de Negocio Específicas
* **RN-09.1 (Restricción de Acceso Administrativo):** Solo los usuarios con rol `ADMIN_GENERAL` tienen autorización para gestionar cooperativas en el terminal.
* **RN-09.2 (Campos Obligatorios y Opcionales):**
  * **Obligatorios:** Nombre de la cooperativa y RUC.
  * **Opcionales:** Dirección de oficina en el terminal, Teléfono de contacto, Correo institucional y Logo (vía URL o subida de archivo; en actualización se admiten URLs completas o rutas relativas generadas por la subida `/static/logos/...`).
  * *Nota de reutilización:* Para Dirección (máx. 150 caracteres), Teléfono (10 dígitos numéricos) y Correo institucional (formato email estándar), se reutilizan estrictamente las mismas validaciones aplicadas en los submódulos de Registro y Perfil.
* **RN-09.3 (Formato y Algoritmo de RUC Ecuatoriano):** El RUC es obligatorio, único en el sistema y debe constar de 13 dígitos numéricos válidos evaluados mediante el algoritmo oficial de RUC ecuatoriano (módulo 10 para personas naturales o módulo 11 para sociedades privadas/públicas, con sufijo de establecimiento comercial).
* **RN-09.4 (Formato y Restricciones del Nombre):** El nombre de la cooperativa es obligatorio, único (insensible a mayúsculas/minúsculas), tiene una longitud máxima de 100 caracteres y únicamente admite caracteres alfanuméricos (letras y números), espacios, guiones medios (`-`) y apóstrofes (`'`). No puede quedar vacío ni completarse únicamente con espacios en blanco.
* **RN-09.5 (Inmutabilidad del RUC):** Una vez registrada la cooperativa, su RUC queda bloqueado contra edición para asegurar la trazabilidad y la integridad tributaria e histórica.
* **RN-09.6 (Modos de Visualización):** La interfaz de cooperativas dispone de un selector para alternar la presentación entre:
  1. **Vista de Tabla:** Presentación tabular detallada de las cooperativas.
  2. **Vista de Tarjetas (Cards):** Cuadrícula proporcional donde cada tarjeta muestra el logo, nombre, estado (Activa / Desactivada) y un botón de engranaje para acceder a la edición y gestión.
* **RN-09.7 (Ciclo de Vida y Restricciones de Desactivación):**
  * La desactivación de una cooperativa se realiza mediante borrado lógico (`is_active = false`).
  * Una cooperativa desactivada no puede tener asignadas nuevas rutas ni turnos.
  * Los Administradores de una cooperativa desactivada pierden el acceso a las funciones operativas de dicha cooperativa, aunque conservan su acceso habitual a los módulos de Pasajero.
  * **Concurrencia en desactivación:** Si una cooperativa fue desactivada y desde otra sesión concurrente un usuario intenta realizar una acción sobre ella (por ejemplo, editarla), el sistema bloquea la acción, redirige al usuario a la pantalla de Inicio/Dashboard y muestra un mensaje informando que la cooperativa ha sido desactivada.

### Criterios de Aceptación (Escenarios BDD)

**CP-48: Registrar cooperativa con datos válidos**
* **Dado** que el Administrador se encuentra en la pantalla del módulo "Cooperativas".
* **Cuando** hace clic en "Nueva Cooperativa", ingresa un Nombre válido, un RUC ecuatoriano válido, llena los campos opcionales y confirma el registro.
* **Entonces** el sistema registra la cooperativa en estado "Activa", muestra el mensaje "Cooperativa registrada exitosamente" y la añade a la lista de cooperativas.

**CP-49: Validar algoritmo de RUC ecuatoriano**
* **Dado** que el Administrador se encuentra en la pantalla del módulo "Cooperativas" en el formulario de registro.
* **Cuando** ingresa un número de RUC de 13 dígitos que no cumple con el algoritmo de validación de RUC de Ecuador y hace clic en "Guardar".
* **Entonces** el sistema impide el registro y muestra el mensaje de error: "El RUC ingresado no es válido según el estándar ecuatoriano".

**CP-50: Validar longitud y caracteres no numéricos del RUC**
* **Dado** que el Administrador se encuentra en la pantalla del módulo "Cooperativas" en el formulario de registro.
* **Cuando** ingresa un RUC con una longitud diferente a 13 dígitos o que contiene letras o caracteres especiales.
* **Entonces** el sistema impide el envío y muestra el mensaje de error: "El RUC debe tener exactamente 13 dígitos numéricos".

**CP-51: Validar unicidad del RUC en el registro**
* **Dado** que el Administrador se encuentra en la pantalla del módulo "Cooperativas" en el formulario de registro y ya existe una cooperativa registrada con dicho RUC.
* **Cuando** intenta registrar una nueva cooperativa utilizando el mismo RUC existente.
* **Entonces** el sistema impide el registro y muestra el mensaje de error: "Ya existe una cooperativa registrada con este RUC".

**CP-52: Validar unicidad del Nombre de la cooperativa**
* **Dado** que el Administrador se encuentra en la pantalla del módulo "Cooperativas" en el formulario de registro y ya existe una cooperativa registrada con el nombre "Cooperativa Loja".
* **Cuando** intenta registrar una nueva cooperativa con el mismo nombre (sin distinguir mayúsculas de minúsculas).
* **Entonces** el sistema impide el registro y muestra el mensaje de error: "Ya existe una cooperativa registrada con este nombre".

**CP-53: Validar caracteres permitidos en el Nombre de la cooperativa**
* **Dado** que el Administrador se encuentra en la pantalla del módulo "Cooperativas" en el formulario de registro.
* **Cuando** ingresa en el campo Nombre caracteres especiales no permitidos (distintos de letras, números, espacios, guiones medios o apóstrofes).
* **Entonces** el sistema impide el registro y muestra el mensaje de error: "El nombre solo puede contener letras, números, espacios, guiones medios y apóstrofes".

**CP-54: Validar longitud máxima en el Nombre de la cooperativa**
* **Dado** que el Administrador se encuentra en la pantalla del módulo "Cooperativas" en el formulario de registro.
* **Cuando** ingresa un nombre que supera los 100 caracteres permitidos.
* **Entonces** el sistema impide el registro y muestra el mensaje de error: "El nombre de la cooperativa no puede exceder los 100 caracteres".

**CP-55: Validar campos obligatorios vacíos o con solo espacios en blanco**
* **Dado** que el Administrador se encuentra en la pantalla del módulo "Cooperativas" en el formulario de registro.
* **Cuando** deja los campos obligatorios (Nombre o RUC) vacíos o los completa únicamente con espacios en blanco y hace clic en "Guardar".
* **Entonces** el sistema no envía el formulario y marca los campos requeridos con sus respectivos mensajes de error ("El nombre de la cooperativa no puede quedar vacío" y "El RUC es obligatorio").

**CP-56: Actualizar información de una cooperativa existente**
* **Dado** que el Administrador se encuentra en la pantalla del módulo "Cooperativas" y abre el formulario de edición mediante el botón de engranaje de una cooperativa activa.
* **Cuando** modifica los campos permitidos (Nombre, Dirección, Teléfono, Correo institucional o Logo) con datos válidos y confirma los cambios.
* **Entonces** el sistema actualiza la información en la base de datos y muestra el mensaje: "Cooperativa actualizada exitosamente".

**CP-57: Restringir campo Nombre vacío o con solo espacios en la edición**
* **Dado** que el Administrador se encuentra en la pantalla del módulo "Cooperativas" editando una cooperativa existente.
* **Cuando** borra el contenido del campo Nombre o ingresa exclusivamente espacios en blanco y hace clic en "Guardar cambios".
* **Entonces** el sistema impide la actualización y muestra el mensaje de error: "El nombre de la cooperativa no puede quedar vacío".

**CP-58: Verificar inmutabilidad del campo RUC en la edición**
* **Dado** que el Administrador se encuentra en la pantalla del módulo "Cooperativas" en la vista de edición de una cooperativa existente.
* **Cuando** visualiza el campo RUC.
* **Entonces** el sistema presenta el campo RUC en modo deshabilitado (solo lectura), impidiendo su edición.

**CP-59: Desactivar (baja lógica) a una cooperativa activa**
* **Dado** que el Administrador se encuentra en la pantalla del módulo "Cooperativas" visualizando una cooperativa en estado "Activa".
* **Cuando** selecciona la acción "Desactivar" y confirma la operación en el diálogo de confirmación.
* **Entonces** el sistema actualiza el estado a "Desactivada" mediante borrado lógico, muestra el mensaje "Cooperativa desactivada exitosamente" y actualiza su estado visual en la interfaz.

**CP-60: Reactivar una cooperativa desactivada**
* **Dado** que el Administrador se encuentra en la pantalla del módulo "Cooperativas" visualizando una cooperativa en estado "Desactivada".
* **Cuando** selecciona la acción "Activar" y confirma la operación.
* **Entonces** el sistema actualiza el estado de la cooperativa a "Activa", muestra el mensaje "Cooperativa activada exitosamente" y restablece su disponibilidad operativa.

**CP-61: Intentar editar una cooperativa desactivada desde otra sesión**
* **Dado** que el Administrador se encuentra en la pantalla del módulo "Cooperativas" e intenta acceder a la edición o guardar cambios de una cooperativa que fue desactivada previamente en otra sesión concurrente.
* **Cuando** el sistema detecta que la cooperativa ya no se encuentra activa.
* **Entonces** el sistema deniega la operación, redirige al usuario a la pantalla de Inicio y muestra el mensaje: "La cooperativa ha sido desactivada".

---

## RF-10: Asignación de Administradores de cooperativa

**Prioridad:** Alta  
**Descripción:** El sistema debe permitir al Administrador General asignar hasta 3 administradores a una cooperativa activa a través de un modal de gestión de personal, seleccionándolos a partir del listado de usuarios que ya cuentan con el rol de Administrador de cooperativa y están disponibles.

### Reglas de Negocio Específicas
* **RN-10.1 (Límite Máximo por Cooperativa):** Una cooperativa puede tener como máximo hasta 3 Administradores de cooperativa asignados de forma simultánea.
* **RN-10.2 (Exclusividad de Asignación por Usuario):** Un usuario con rol `ADMIN_COOPERATIVA` solo puede pertenecer y estar asignado a una única cooperativa a la vez.
* **RN-10.3 (Filtro de Usuarios Elegibles en la Selección):** El modal de gestión de administradores lista únicamente usuarios que cumplan concurrentemente tres condiciones:
  1. Poseer el rol `ADMIN_COOPERATIVA`.
  2. Encontrarse en estado `Activo`.
  3. No estar asignados a ninguna otra cooperativa (usuarios libres o los ya asignados a la cooperativa actual).
* **RN-10.4 (Conservación de Rol al Desvincular):** Al desvincular a un administrador de la cooperativa, el usuario mantiene intacto su rol `ADMIN_COOPERATIVA` en el sistema, quedando en estado libre (sin cooperativa asignada) hasta una futura vinculación.
* **RN-10.5 (Sección de Personal de Cooperativa):** Dentro del formulario de registro y de la pantalla de configuración/edición de la cooperativa se incluye una sección denominada "Personal de cooperativa", donde se visualiza la lista de administradores asignados o seleccionados y un botón "Gestionar administradores" para abrir el modal de selección.

### Criterios de Aceptación (Escenarios BDD)

**CP-62: Asignar administradores de cooperativa desde el modal de gestión**
* **Dado** que el Administrador se encuentra en la pantalla del módulo "Cooperativas" en la vista de edición de una cooperativa activa y pulsa "Gestionar administradores".
* **Cuando** en el modal selecciona uno o más usuarios de la lista de elegibles (hasta un máximo de 3) y hace clic en "Guardar".
* **Entonces** el sistema vincula a los usuarios seleccionados con la cooperativa, muestra el mensaje "Administradores asignados exitosamente" y refleja sus nombres en la sección "Personal de cooperativa".

**CP-63: Bloquear selección al alcanzar el límite de 3 administradores**
* **Dado** que el Administrador se encuentra en la pantalla del módulo "Cooperativas" dentro del modal "Gestionar administradores".
* **Cuando** selecciona 3 usuarios en la lista.
* **Entonces** el sistema deshabilita las casillas de selección del resto de usuarios disponibles en el modal, impidiendo seleccionar más del límite permitido.

**CP-64: Desvincular a un Administrador de la cooperativa**
* **Dado** que el Administrador se encuentra en la pantalla del módulo "Cooperativas" en la sección "Personal de cooperativa" de una cooperativa con administradores asignados.
* **Cuando** elimina a uno de los administradores de la lista y confirma los cambios.
* **Entonces** el sistema retira la vinculación del usuario con la cooperativa, mantiene el rol `ADMIN_COOPERATIVA` del usuario dejándolo disponible para futuras asignaciones, y muestra el mensaje: "Administrador desvinculado exitosamente".
