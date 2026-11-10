# Module Access by Role Specification

## Purpose
Permitir a los usuarios autenticados visualizar en su dashboard y barra de navegación lateral únicamente los módulos autorizados según su(s) rol(es) asignado(s), con soporte para roles individuales y roles combinados (RF-05).

## Requirements

### Requirement: Acceso a módulos del Administrador General
El sistema DEBE mostrar en el menú de navegación del Administrador General únicamente los accesos a los módulos: "Usuarios", "Cooperativas", "Rutas generales" y "Precios generales".

#### Scenario: CP-23 Acceso a módulos del Administrador
- **GIVEN** que un usuario con el rol de "Administrador General" (`ADMIN_GENERAL`) ha iniciado sesión exitosamente
- **WHEN** visualiza el dashboard principal o el menú de navegación lateral
- **THEN** el sistema le muestra únicamente el acceso a los módulos: Usuarios, Cooperativas, Rutas generales y Precios generales

### Requirement: Acceso a módulos del Administrador de Cooperativa
El sistema DEBE mostrar en el menú de navegación del Administrador de Cooperativa únicamente los accesos a los módulos: "Rutas de cooperativa", "Buses", "Turnos" y "Tarifas específicas".

#### Scenario: CP-24 Acceso a módulos de Admin de Cooperativa
- **GIVEN** que un usuario con el rol de "Administrador de Cooperativa" (`ADMIN_COOPERATIVA`) ha iniciado sesión exitosamente
- **WHEN** visualiza el dashboard principal o el menú de navegación lateral
- **THEN** el sistema le muestra únicamente el acceso a los módulos: Rutas de cooperativa, Buses, Turnos y Tarifas específicas

### Requirement: Acceso a módulos de Secretaria de Cooperativa
El sistema DEBE mostrar en el menú de navegación de la Secretaria de Cooperativa únicamente el acceso al módulo: "Reservas".

#### Scenario: CP-25 Acceso a módulos de Secretaria de Cooperativa
- **GIVEN** que un usuario con el rol de "Secretaria de Cooperativa" (`SECRETARIA_COOPERATIVA`) ha iniciado sesión exitosamente
- **WHEN** visualiza el dashboard principal o el menú de navegación lateral
- **THEN** el sistema le muestra únicamente el acceso al módulo: Reservas

### Requirement: Acceso a módulos de Pasajero
El sistema DEBE mostrar en el menú de navegación del usuario con rol exclusivo de Pasajero únicamente los accesos a los módulos: "Reservas" y "Perfil".

#### Scenario: CP-26 Acceso a módulos de Pasajero
- **GIVEN** que un usuario con el rol exclusivo de "Pasajero" (`PASAJERO`) ha iniciado sesión exitosamente
- **WHEN** visualiza el dashboard principal o el menú de navegación lateral
- **THEN** el sistema le muestra únicamente el acceso a los módulos: Reservas y Perfil

### Requirement: Acceso a módulos por roles combinados
El sistema DEBE computar la unión matemática de los módulos permitidos cuando un usuario posee múltiples roles activos simultáneos.

#### Scenario: CP-27 Acceso a módulos por roles combinados (Admin Coop y Pasajero)
- **GIVEN** que un usuario que posee múltiples roles activos ("Administrador de Cooperativa" y "Pasajero") ha iniciado sesión exitosamente
- **WHEN** visualiza el dashboard principal o el menú de navegación lateral
- **THEN** el sistema le muestra el conjunto exacto de módulos permitidos por ambos roles: Rutas de cooperativa, Buses, Turnos, Tarifas específicas, Reservas y Perfil

### Requirement: Barra lateral colapsable y navegación móvil responsive
El sistema DEBE permitir contraer y expandir la barra lateral mediante un botón de alternancia en pantallas medianas y grandes, optimizando el espacio visual de trabajo. Asimismo, en pantallas móviles y reducidas, el sistema DEBE disponer de un botón de menú que despliegue la navegación mediante un panel lateral / drawer para garantizar la accesibilidad responsive en cualquier dispositivo.

#### Scenario: Contracción y expansión del sidebar en escritorio
- **GIVEN** que el usuario visualiza la barra lateral en escritorio
- **WHEN** hace clic en el botón de alternancia (toggle) del sidebar
- **THEN** la barra lateral alterna entre su estado expandido (mostrando icono y texto) y contraído (mostrando únicamente iconos con tooltips informativos)

#### Scenario: Visualización y apertura del menú en dispositivos móviles
- **GIVEN** que el usuario accede desde una pantalla pequeña o dispositivo móvil
- **WHEN** pulsa el botón de menú hamburguesa en el encabezado
- **THEN** se despliega el menú lateral como un drawer/overlay sobre la interfaz, permitiendo seleccionar cualquier módulo y cerrándose al navegar o pulsar el botón de cierre

### Requirement: Manejo de módulos no construidos
Para aquellos módulos del menú que aún no han sido implementados, al hacer clic en el enlace, el sistema DEBE presentar una vista en blanco con el nombre del módulo respectivo.

#### Scenario: Navegación hacia un módulo placeholder
- **GIVEN** que un usuario hace clic en un módulo que aún no cuenta con interfaz de negocio construida (ej. "Cooperativas", "Buses", etc.)
- **WHEN** la aplicación procesa la navegación
- **THEN** el sistema renderiza una vista con el título del módulo correspondiente y un mensaje de módulo en construcción

