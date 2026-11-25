# Especificación de Requisitos - Módulo de Cooperativas

**Módulo:** Cooperativas  
**Submódulo:** 05 - Gestión de Rutas (Rutas Generales, Rutas de Cooperativa) y Notificaciones   

---

## RF-12: Gestión de Rutas Generales

**Prioridad:** Alta  
**Descripción:** El sistema debe permitir al Administrador General registrar, consultar, editar y cambiar el estado (baja lógica y reactivación) de las rutas generales del terminal, apoyándose en un catálogo de localidades. Además, desde la misma pantalla puede supervisar, en modo solo lectura, las rutas específicas creadas por cada cooperativa.

### Reglas de Negocio Específicas
* **RN-12.1 (Restricción de Acceso Administrativo):** Solo los usuarios con rol `ADMIN_GENERAL` pueden crear, editar, activar y desactivar rutas generales. Cualquier otro rol recibe una respuesta HTTP 403.
* **RN-12.2 (Campos Obligatorios y Opcionales):**
  * **Obligatorios:** Origen, Destino, Nombre, Distancia (km), Tiempo estimado, Localidades por las que pasa y Estado.
  * **Opcionales:** Descripción (máximo 100 caracteres).
  * *Nota:* El precio no forma parte de este submódulo; se gestiona en un submódulo posterior.
* **RN-12.3 (Catálogo Vivo de Localidades):**
  * Origen, Destino y paradas intermedias se seleccionan desde un catálogo de localidades mediante un campo de selección con búsqueda (combobox).
  * Si la localidad buscada no existe, el usuario (`ADMIN_GENERAL` o `ADMIN_COOPERATIVA`) puede registrarla en ese momento sin salir del formulario.
  * El nombre de la localidad es único en el catálogo (insensible a mayúsculas/minúsculas) y no puede quedar vacío ni compuesto solo por espacios. El campo elimina automáticamente los espacios sobrantes.
  * Si el texto buscado coincide con una localidad existente (sin distinguir mayúsculas de minúsculas), el sistema resalta la localidad existente y no ofrece la opción de registrar una nueva.
* **RN-12.4 (Nombre de la Ruta):** El nombre se compone de un prefijo no editable con el formato `Origen - Destino`, más un texto adicional opcional ingresado por el usuario (máximo 30 caracteres). Si no se agrega texto adicional, el nombre es únicamente `Origen - Destino`. El prefijo se actualiza automáticamente al cambiar Origen o Destino mientras estos sean editables.
* **RN-12.5 (Distancia):** Se expresa en kilómetros, admite decimales y debe ser estrictamente mayor a 0. Al ser un campo numérico, la interfaz no permite ingresar caracteres que no sean dígitos o separador decimal.
* **RN-12.6 (Tiempo Estimado):** En la interfaz se ingresa en campos numéricos separados de Horas y Minutos (minutos entre 0 y 59); en la base de datos se almacena como minutos enteros totales. El tiempo total debe ser mayor a 0 y menor a 24 horas, que es el tiempo de viaje más largo en Ecuador.
* **RN-12.7 (Localidades por las que Pasa):**
  * Por defecto la opción "Solo las de origen y destino" se encuentra marcada. Al desmarcarla se habilita la búsqueda y selección de paradas intermedias.
  * Cada parada intermedia consiste únicamente en una Localidad y un Número de Orden. El orden es secuencial y lo define manualmente el administrador.
  * Si se desmarca la opción, debe seleccionarse al menos una parada intermedia.
* **RN-12.8 (Coherencia de Origen, Destino y Paradas):** El Origen y el Destino deben ser distintos. Ninguna parada intermedia puede ser igual al Origen ni al Destino, ni repetirse dentro de la misma ruta.
* **RN-12.9 (Unicidad de Rutas Generales):** No pueden existir dos rutas generales con la misma combinación de Origen, Destino y Distancia.
* **RN-12.10 (Edición Restringida):** Si la ruta general tiene cooperativas asociadas o turnos asociados, el Origen y el Destino quedan bloqueados contra edición (y, por consiguiente, el prefijo del nombre). Los demás campos siguen siendo editables. El backend rechaza cualquier intento de modificar Origen o Destino en esa condición.
* **RN-12.11 (Ciclo de Vida y Estado):**
  * Al crearse, la ruta queda en estado `Activa` por defecto.
  * La desactivación es un borrado lógico (`is_active = false`).
  * Al desactivar una ruta general se desactivan en cascada las asociaciones de las cooperativas que la habían adoptado, sin eliminar su información.
  * Se notifica (correo electrónico y notificación dentro de la aplicación) a todos los administradores activos de las cooperativas afectadas y se registra la operación en la auditoría.
  * Se deja documentado un método de verificación/desactivación de viajes y reservas futuros (`check_active_trips_or_reservations()`), que mientras no existan los módulos de turnos y reservas no encuentra elementos y no bloquea la operación. Cuando se implementen, deshabilitará los viajes y reservas afectados y notificará a los pasajeros.
  * La reactivación de una ruta general no reactiva automáticamente las asociaciones de las cooperativas; cada cooperativa decide si vuelve a habilitarla.
* **RN-12.12 (Vistas del Administrador General):**
  1. **Rutas generales:** listado con filtros (origen, destino, estado), creación, edición y activación/desactivación.
  2. **Rutas específicas de cooperativas:** se muestran debajo de las generales, agrupadas en secciones por cooperativa, en modo solo lectura. Cada ruta dispone de un botón para ver su detalle completo (paradas, tiempo y distancia) en un modal de solo lectura.
* **RN-12.13 (Auditoría):** La creación, edición, activación y desactivación de rutas se registra en la auditoría (usuario, fecha/hora, acción, módulo, entidad afectada, resultado).

### Criterios de Aceptación (Escenarios BDD)

**CA-65: Registrar ruta general con datos válidos**
* **Dado** que el Administrador se encuentra en el submódulo "Rutas" y pulsa "Nueva ruta general".
* **Cuando** selecciona un Origen y un Destino distintos, deja vacío el campo de texto adicional del nombre, ingresa una distancia mayor a 0, un tiempo estimado mayor a 0, mantiene marcada la opción "Solo las de origen y destino", agrega una descripción y confirma el registro.
* **Entonces** el sistema registra la ruta en estado "Activa", muestra el mensaje "Ruta registrada exitosamente" y la añade al listado de rutas generales.

**CA-66: Generar el nombre de la ruta con prefijo no editable y texto adicional**
* **Dado** que el Administrador se encuentra en el formulario de registro de una ruta general.
* **Cuando** selecciona un Origen y un Destino distintos, escribe texto en el campo de texto adicional del nombre y confirma el registro.
* **Entonces** el sistema guarda el nombre completo combinando el prefijo y el texto adicional.

**CA-67: Validar campos obligatorios vacíos en la ruta general**
* **Dado** que el Administrador se encuentra en el formulario de registro de una ruta general.
* **Cuando** deja vacíos uno o más campos obligatorios (Origen, Destino, Distancia o Tiempo estimado) y hace clic en "Guardar".
* **Entonces** el sistema impide el registro y marca cada campo requerido con su mensaje de error correspondiente (por ejemplo, "El origen es obligatorio" o "La distancia es obligatoria").

**CA-68: Validar que Origen y Destino sean distintos**
* **Dado** que el Administrador se encuentra en el formulario de registro o edición de una ruta general.
* **Cuando** selecciona alguna localidad como Origen e intenta seleccionar la misma como Destino.
* **Entonces** el sistema excluye automáticamente la localidad seleccionada como Origen del catálogo de localidades disponibles para Destino, evitando así que una misma localidad sea asignada en ambos campos.

**CA-69: Validar que una parada intermedia no coincida con el Origen o el Destino**
* **Dado** que el Administrador ha desmarcado la opción "Solo las de origen y destino" en el formulario de una ruta general.
* **Cuando** agrega como parada intermedia la misma localidad del Origen o del Destino.
* **Entonces** el sistema impide agregar la parada y muestra el mensaje de error: "Una parada intermedia no puede ser igual al origen o al destino".

**CA-70: Validar paradas intermedias duplicadas**
* **Dado** que el Administrador ha desmarcado la opción "Solo las de origen y destino" y ya agregó una localidad como parada intermedia.
* **Cuando** intenta agregar nuevamente la misma localidad como otra parada de la ruta.
* **Entonces** el sistema impide la duplicidad y muestra el mensaje de error: "La localidad ya fue agregada como parada de esta ruta".

**CA-71: Registrar paradas intermedias en orden secuencial**
* **Dado** que el Administrador se encuentra registrando una nueva ruta y desmarca la opción "Solo las de origen y destino".
* **Cuando** busca y agrega varias localidades intermedias definiendo manualmente su orden y confirma el registro.
* **Entonces** el sistema guarda las paradas con su número de orden consecutivo y las muestra en ese mismo orden en el detalle de la ruta.

**CA-72: Exigir al menos una parada cuando se desmarca la opción por defecto**
* **Dado** que el Administrador se encuentra en el formulario de una ruta y desmarca la opción "Solo las de origen y destino" sin agregar ninguna parada intermedia.
* **Cuando** hace clic en "Guardar".
* **Entonces** el sistema impide el registro y muestra el mensaje de error: "Debe agregar al menos una parada intermedia o marcar la opción 'Solo las de origen y destino'".

**CA-73: Validar distancia inválida (menor o igual a cero)**
* **Dado** que el Administrador se encuentra en el formulario de una ruta general.
* **Cuando** ingresa una distancia igual a 0 o negativa y hace clic en "Guardar".
* **Entonces** el sistema impide el registro y muestra el mensaje de error: "La distancia debe ser un número mayor a 0".

**CA-74: Validar tiempo estimado inválido**
* **Dado** que el Administrador se encuentra en el formulario de una ruta general.
* **Cuando** ingresa un tiempo estimado que contiene valores fuera de los rangos permitidos: "horas" mayor a 0, "minutos" entre 0 y 59, o establece ambos campos en 0, y hace clic en el botón "Guardar".
* **Entonces** el sistema impide el registro y muestra el mensaje de error: "Ingrese un tiempo estimado válido. El tiempo total debe ser mayor a cero y los minutos deben estar entre 0 y 59".

**CA-75: Validar unicidad de la ruta general (Origen, Destino y Distancia)**
* **Dado** que el Administrador se encuentra en el formulario de registro y ya existe una ruta general con el mismo Origen, Destino y Distancia.
* **Cuando** intenta registrar una nueva ruta con esa misma combinación.
* **Entonces** el sistema impide el registro y muestra el mensaje de error: "Ya existe una ruta general con el mismo origen, destino y distancia".

**CA-76: Permitir la misma pareja Origen-Destino con distancia distinta**
* **Dado** que existe una ruta general registrada con una determinada combinación de origen y destino.
* **Cuando** el Administrador registra una nueva ruta con la misma combinación de origen y destino, pero con una distancia diferente.
* **Entonces** el sistema registra la nueva ruta exitosamente, dado que la combinación de Origen, Destino y Distancia es distinta.

**CA-77: Registrar una nueva localidad desde el selector del catálogo**
* **Dado** que el Administrador se encuentra en el formulario de una ruta general y escribe en el selector de localidades un nombre que no existe en el catálogo.
* **Cuando** selecciona la opción de "Crear y usar la nueva localidad".
* **Entonces** el sistema registra la localidad en el catálogo, la deja seleccionada en el campo correspondiente y la hace disponible para futuras rutas.

**CA-78: Editar todos los campos de una ruta general sin asociaciones**
* **Dado** que el Administrador abre el formulario de edición de una ruta general que no tiene cooperativas ni turnos asociados.
* **Cuando** modifica cualquier campo (incluyendo Origen y Destino) con datos válidos y confirma los cambios.
* **Entonces** el sistema actualiza la ruta, regenera el prefijo del nombre si cambió el Origen o el Destino y muestra el mensaje "Ruta actualizada exitosamente".

**CA-79: Restringir la edición de Origen y Destino en una ruta con asociaciones (PENDIENTE)**
* **Dado** que el Administrador abre el formulario de edición de una ruta general que tiene cooperativas o turnos asociados.
* **Cuando** visualiza los campos del formulario.
* **Entonces** el sistema presenta los campos Origen y Destino en modo deshabilitado (solo lectura), permite modificar el resto de los campos informativos y, al guardar, muestra el mensaje "Ruta actualizada exitosamente".

**CA-80: Desactivar una ruta general sin cooperativas asociadas**
* **Dado** que el Administrador visualiza una ruta general en estado "Activa" sin cooperativas que la hayan adoptado.
* **Cuando** selecciona la acción "Desactivar" y confirma la operación.
* **Entonces** el sistema actualiza el estado a "Inactiva", muestra el mensaje "Ruta desactivada exitosamente" y registra la acción en la auditoría.

**CA-81: Desactivar una ruta general adoptada por cooperativas (cascada y notificaciones) (PENDIENTE)**
* **Dado** que el Administrador visualiza una ruta general activa adoptada por una o más cooperativas.
* **Cuando** selecciona la acción "Desactivar" y confirma el diálogo, el cual advierte que se desactivará en las cooperativas que la utilizan.
* **Entonces** el sistema desactiva la ruta, desactiva en cascada sus asociaciones en las cooperativas sin eliminar su información, envía un correo y una notificación dentro de la aplicación a todos los administradores activos de las cooperativas afectadas, y registra la operación en la auditoría.

**CA-82: Reactivar una ruta general inactiva**
* **Dado** que el Administrador visualiza una ruta general en estado "Inactiva".
* **Cuando** selecciona la acción "Activar" y confirma la operación.
* **Entonces** el sistema actualiza el estado a "Activa", muestra el mensaje "Ruta activada exitosamente" y mantiene inactivas las asociaciones de las cooperativas hasta que cada una las habilite nuevamente.

**CA-83: Filtrar el listado de rutas generales**
* **Dado** que el Administrador se encuentra en el listado de rutas generales.
* **Cuando** aplica filtros por origen, destino o estado.
* **Entonces** el sistema muestra únicamente las rutas que cumplen con los criterios seleccionados y un mensaje informativo: "No se encontraron rutas generales que coincidan con los criterios".

**CA-84: Visualizar las rutas específicas de cada cooperativa en modo solo lectura**
* **Dado** que el Administrador se encuentra en el submódulo "Rutas".
* **Cuando** desplaza la vista por debajo del listado de rutas generales.
* **Entonces** el sistema muestra las rutas específicas agrupadas en una sección por cooperativa, sin ofrecer acciones de edición, activación ni desactivación sobre ellas.

---

## RF-13: Gestión de rutas de cooperativa

**Prioridad:** Alta  
**Descripción:** El sistema debe permitir al administrador de cooperativa gestionar las rutas asociadas a su cooperativa: adoptar rutas generales activas del terminal, habilitarlas o deshabilitarlas en su oferta, y crear y administrar rutas específicas propias que solo son visibles para su cooperativa.

### Reglas de Negocio Específicas
* **RN-13.1 (Restricción de Acceso y Pertenencia):** Solo los usuarios con rol `ADMIN_COOPERATIVA` pueden gestionar rutas de cooperativa y únicamente sobre los recursos de la cooperativa a la que están asignados. La pertenencia se valida siempre en el backend con la cooperativa del usuario autenticado, nunca solo con IDs enviados por el frontend. El acceso a recursos de otra cooperativa genera una respuesta HTTP 403.
* **RN-13.2 (Estructura de la Pantalla):** La pantalla se divide en dos secciones:
  1. **Rutas generales:** lista las rutas generales adoptadas por la cooperativa. El administrador de cooperativa no puede editarlas ni modificar sus datos; solo puede habilitarlas o deshabilitarlas para su cooperativa mediante un interruptor Activa/Inactiva.
  2. **Mis rutas:** lista las rutas específicas de la cooperativa, que pueden crearse, editarse y activarse/desactivarse.
* **RN-13.3 (Adopción de Rutas Generales):**
  * El botón "Agregar" de la sección "Rutas generales" abre un modal (con una interfaz similar a la de asignación de administradores de cooperativa) que lista únicamente las rutas generales activas que la cooperativa aún no ha adoptado.
  * Una cooperativa no puede adoptar la misma ruta general más de una vez. La interfaz bloquea la selección de rutas ya adoptadas y el backend rechaza cualquier intento de duplicarlas.
  * Al adoptarse, la ruta queda en estado `Activa` para la cooperativa.
* **RN-13.4 (Interruptor Activa/Inactiva en Rutas Generales Adoptadas):**
  * No existe la acción de eliminar o desvincular; se utiliza el interruptor Activa/Inactiva para dejar de ofrecer la ruta.
  * Una ruta general adoptada solo puede reactivarse si la ruta general sigue activa.
* **RN-13.5 (Rutas Específicas de la Cooperativa):**
  * Se registran con los mismos campos, formatos y validaciones de la ruta general definidos en RN-12.2 a RN-12.8 (nombre con prefijo no editable, distancia en km, tiempo en horas y minutos, paradas intermedias secuenciales, Origen distinto del Destino).
  * El catálogo de localidades es accesible para el administrador de cooperativa bajo las mismas reglas de RN-12.3.
  * Solo son visibles para su cooperativa y, en modo solo lectura, para el `ADMIN_GENERAL`.
  * No incluyen precio; este se define en un submódulo posterior.
* **RN-13.6 (Unicidad por Cooperativa):** No pueden existir dos rutas específicas de la misma cooperativa con la misma combinación de Origen, Destino y Distancia. Otra cooperativa sí puede registrar una ruta con esa misma combinación sin conflicto.
* **RN-13.7 (Edición de Rutas Específicas):** Si la ruta específica tiene turnos asociados, solo pueden editarse los campos informativos y el Origen y el Destino quedan bloqueados (misma regla de RN-12.10).
* **RN-13.8 (Desactivación con Turnos o Reservas Activas):**
  * Si la ruta (general adoptada o específica) tiene turnos activos o pasajes reservados, el sistema muestra un modal de confirmación antes de desactivarla; al confirmar, se desactiva y se notifica a los usuarios afectados por correo y dentro de la aplicación.
  * Mientras no existan los módulos de turnos y reservas, la verificación se realiza mediante el método documentado `check_active_trips_or_reservations()`, que no encuentra elementos y no bloquea la operación.
* **RN-13.9 (Cooperativa Desactivada):** Si la cooperativa está desactivada, no se puede acceder a la gestión de sus rutas ni realizar acciones sobre ellas, pero su información (rutas y asociaciones) se conserva sin eliminarse.
* **RN-13.10 (Auditoría):** La adopción de rutas generales, la creación y edición de rutas específicas y los cambios de estado se registran en la auditoría.

### Criterios de Aceptación (Escenarios BDD)

**CA-85: Visualizar las secciones de rutas de la cooperativa**
* **Dado** que el Administrador de cooperativa ingresa al submódulo "Rutas" de su cooperativa activa.
* **Cuando** el sistema carga la pantalla.
* **Entonces** el sistema muestra las secciones "Rutas generales" (rutas adoptadas) y "Mis rutas" (rutas específicas), cada una con su listado o con un mensaje informativo si está vacía.

**CA-86: Listar en el modal únicamente rutas generales activas no adoptadas**
* **Dado** que el Administrador de cooperativa se encuentra en la sección "Rutas generales" y pulsa el botón "Agregar".
* **Cuando** se abre el modal de selección.
* **Entonces** el sistema lista únicamente las rutas generales activas que la cooperativa aún no ha adoptado, excluyendo las inactivas y las ya adoptadas.

**CA-87: Adoptar rutas generales desde el modal**
* **Dado** que el Administrador de cooperativa se encuentra en el modal de selección de rutas generales.
* **Cuando** selecciona una o más rutas disponibles y hace clic en "Guardar".
* **Entonces** el sistema asocia las rutas a la cooperativa en estado "Activa", muestra el mensaje "Rutas agregadas exitosamente" y las refleja en la sección "Rutas generales".

**CA-88: Deshabilitar una ruta general adoptada mediante el interruptor**
* **Dado** que el Administrador de cooperativa visualiza una ruta general adoptada cuyo estado de Operación Propia se encuentra en "Operando", sin turnos ni reservas activas.
* **Cuando** cambia el interruptor a "Pausada".
* **Entonces** el sistema actualiza el estado de la ruta para la cooperativa, muestra el mensaje "Operación de ruta adoptada actualizada a Inactiva" y conserva la asociación y su información.

**CA-89: Deshabilitar una ruta general con turnos o reservas activas solicitando confirmación (PENDIENTE)**
* **Dado** que la ruta que el Administrador de cooperativa desea desactivar tiene turnos activos o pasajes reservados.
* **Cuando** cambia el interruptor a "Inactiva".
* **Entonces** el sistema muestra un modal de confirmación advirtiendo del impacto y, al confirmar, desactiva la ruta y notifica a los usuarios afectados por correo y dentro de la aplicación.

**CA-90: Reactivar una ruta general adoptada**
* **Dado** que el Administrador de cooperativa visualiza una ruta general adoptada adoptada cuyo estado de Operación Propia se encuentra en "Pausada" y su estado en el catálogo general de rutas sigue activa.
* **Cuando** cambia el interruptor a "Operando".
* **Entonces** el sistema actualiza el estado a "Operando" y muestra el mensaje "Operación de ruta adoptada actualizada a Activa".

**CA-91: Impedir reactivar una ruta general adoptada cuya ruta general está inactiva**
* **Dado** que el Administrador de cooperativa visualiza una ruta general adoptada cuyo estado de Operación Propia se encuentra en "Pausada" y su estado en el catálogo general de rutas ha sido cambiado a "Inactiva" por el Administrador General.
* **Cuando** intenta cambiar el interruptor a "Operando".
* **Entonces** el sistema bloquea las acciones del interruptor, impidiendo cambiar su estado.

**CA-92: Registrar una ruta específica con datos válidos**
* **Dado** que el Administrador de cooperativa se encuentra en la sección "Mis rutas" y pulsa "Nueva ruta".
* **Cuando** selecciona un Origen y un Destino distintos, ingresa distancia mayor a 0, tiempo estimado válido, define sus localidades y confirma el registro.
* **Entonces** el sistema registra la ruta en estado "Activa" asociada a su cooperativa, muestra el mensaje "Ruta registrada exitosamente" y la añade a la sección "Mis rutas".

**CA-93: Permitir rutas similares entre cooperativas distintas**
* **Dado** que otra cooperativa ya registró una ruta específica.
* **Cuando** el Administrador de cooperativa registra una ruta con el mismo Origen, Destino y Distancia en su propia cooperativa.
* **Entonces** el sistema registra la ruta exitosamente, sin conflicto con la ruta de la otra cooperativa.

**CA-94: Editar una ruta específica de la cooperativa**
* **Dado** que el Administrador de cooperativa abre el formulario de edición de una ruta de "Mis rutas".
* **Cuando** modifica campos permitidos con datos válidos y confirma los cambios.
* **Entonces** el sistema actualiza la ruta y muestra el mensaje "Ruta actualizada exitosamente".

**CA-95: Desactivar una ruta específica de la cooperativa**
* **Dado** que el Administrador de cooperativa visualiza una ruta de "Mis rutas" en estado "Activa" sin turnos ni reservas activas.
* **Cuando** selecciona la acción "Desactivar" y confirma la operación.
* **Entonces** el sistema actualiza su estado a "Inactiva", muestra el mensaje "Ruta desactivada exitosamente" y conserva su información.

**CA-96: Reactivar una ruta específica de la cooperativa**
* **Dado** que el Administrador de cooperativa visualiza una ruta de "Mis rutas" en estado "Inactiva".
* **Cuando** selecciona la acción "Activar" y confirma la operación.
* **Entonces** el sistema actualiza su estado a "Activa" y muestra el mensaje "Ruta activada exitosamente".

**CA-97: Bloquear la gestión de rutas cuando la cooperativa está desactivada**
* **Dado** que la cooperativa del Administrador de cooperativa se encuentra en estado "Desactivada".
* **Cuando** intenta acceder al submódulo "Rutas" o consultar las rutas de su cooperativa.
* **Entonces** el sistema oculta las secciones de gestión de rutas y muestra el mensaje "Cooperativa desactivada" indicando que el Administrador General ha deshabilitado su cooperativa, sin mostrar mensajes de error no entendibles.

---

## RF-14: Notificaciones de la aplicación

**Prioridad:** Media  
**Descripción:** El sistema debe informar a los usuarios sobre eventos relevantes (como la desactivación de una ruta general) mediante correo electrónico y un centro de notificaciones dentro de la aplicación, accesible mediante un icono ubicado junto al nombre de usuario en el encabezado.

### Reglas de Negocio Específicas
* **RN-14.1 (Visibilidad):** El icono de notificaciones es visible para cualquier usuario autenticado y muestra un indicador con la cantidad de notificaciones no leídas.
* **RN-14.2 (Datos de la Notificación):** Cada notificación registra al menos: usuario notificado, mensaje, fecha y hora, y estado de lectura (leída: sí/no).
* **RN-14.3 (Listado Paginado):** Al abrir el icono se muestran las 5 notificaciones más recientes del usuario, ordenadas de la más reciente a la más antigua. Un botón "Cargar más" al final carga otras 5 por cada pulsación y se oculta cuando no hay más.
* **RN-14.4 (Marcar como Leídas):** Un botón "Marcar todas como leídas" actualiza todas las notificaciones del usuario a leídas.
* **RN-14.5 (Estado Vacío):** Si el usuario no tiene notificaciones, se muestra el mensaje "No tienes notificaciones".
* **RN-14.6 (Privacidad):** Un usuario solo puede consultar y marcar como leídas sus propias notificaciones. El backend nunca devuelve ni modifica notificaciones de otro usuario.
* **RN-14.7 (Destinatarios en este Submódulo):** Al desactivarse una ruta general adoptada, se notifica (in-app y correo) a todos los administradores activos de las cooperativas afectadas. Cuando se implementen turnos y reservas, se notificará también a los pasajeros afectados.
* **RN-14.8 (Resiliencia del Correo):** Un fallo en el envío del correo no revierte la operación principal; la notificación dentro de la aplicación se conserva y el error se registra sin exponer datos sensibles.

### Criterios de Aceptación (Escenarios BDD)

**CA-98: Mostrar mensaje cuando no existen notificaciones**
* **Dado** que un usuario autenticado no tiene notificaciones.
* **Cuando** pulsa el icono de notificaciones.
* **Entonces** el sistema muestra el mensaje "No tienes notificaciones".

**CA-99: Visualizar el icono de notificaciones y las más recientes**
* **Dado** que un usuario autenticado tiene notificaciones.
* **Cuando** pulsa el icono de notificaciones junto a su nombre de usuario.
* **Entonces** el sistema muestra las 5 notificaciones más recientes con su mensaje y fecha, distinguiendo visualmente las no leídas, y un indicador con el total de no leídas en el icono.

**CA-100: Cargar más notificaciones**
* **Dado** que el usuario tiene más de 5 notificaciones y abrió el listado.
* **Cuando** pulsa el botón "Cargar más".
* **Entonces** el sistema agrega otras 5 notificaciones más antiguas al listado y oculta el botón cuando ya no existen más por mostrar.

**CA-101: Marcar todas las notificaciones como leídas**
* **Dado** que el usuario tiene notificaciones no leídas.
* **Cuando** pulsa el botón "Marcar todas como leídas".
* **Entonces** el sistema actualiza todas sus notificaciones a leídas y el indicador de no leídas desaparece del icono.

**CA-102: Generar notificaciones al desactivar una ruta general adoptada**
* **Dado** que el Administrador General desactiva una ruta general adoptada por una cooperativa con administradores activos.
* **Cuando** el sistema completa la desactivación.
* **Entonces** cada administrador activo de la cooperativa afectada recibe una notificación dentro de la aplicación y un correo electrónico indicando que la ruta fue desactivada por la administración del terminal.

**CA-103: Conservar la notificación ante un fallo en el envío del correo**
* **Dado** que el servicio de correo no está disponible al desactivar una ruta general adoptada.
* **Cuando** el sistema intenta enviar el correo a los administradores afectados.
* **Entonces** el sistema completa la desactivación, conserva la notificación dentro de la aplicación y registra el error sin mostrar detalles técnicos al usuario.

---

## Verificaciones cubiertas únicamente con pruebas unitarias (sin caso de prueba manual)

* Rechazo desde el backend de la modificación de Origen y Destino en una ruta con asociaciones (RN-12.10).
* Acceso a la gestión de rutas generales por usuarios sin rol `ADMIN_GENERAL`, con respuesta HTTP 403 (RN-12.1).
* Rechazo desde el backend de la adopción duplicada de una ruta general (RN-13.3).
* Rechazo de modificaciones sobre rutas generales adoptadas por parte de `ADMIN_COOPERATIVA` (RN-13.2).
* Unicidad de localidades en el catálogo sin distinguir mayúsculas de minúsculas ni espacios sobrantes (RN-12.3).
* Aislamiento de notificaciones: un usuario no puede consultar ni modificar las de otro (RN-14.6).
