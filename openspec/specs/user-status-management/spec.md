# User Status Management Specification

## Purpose
Permitir al Administrador General cambiar el estado de acceso de los usuarios (dar de baja mediante borrado lógico o reactivar/habilitar), bloqueando el acceso de cuentas inactivas con mensajes claros de retroalimentación (RF-08).

## Requirements

### Requirement: Dar de baja a un usuario (borrado lógico)
El sistema DEBE permitir al Administrador General cambiar el estado de un usuario activo a inactivo (`is_active = false`), aplicando un borrado lógico en base de datos sin eliminar físicamente el registro del usuario.

#### Scenario: CP-30 Dar de baja a un usuario activo
- **GIVEN** que el Administrador General tiene sesión iniciada y localiza a un usuario en estado "Activo" dentro del módulo "Usuarios"
- **WHEN** selecciona la acción "Dar de baja" y confirma la operación en el diálogo modal
- **THEN** el sistema actualiza el estado del usuario a "Inactivo" mediante borrado lógico en la base de datos y muestra un mensaje confirmando que la baja fue exitosa

### Requirement: Restricción de acceso para usuarios inactivos
El sistema DEBE rechazar el intento de inicio de sesión de cualquier cuenta que se encuentre en estado inactivo (`is_active = false`), impidiendo la generación de tokens de autenticación y desplegando el mensaje oficial de advertencia.

#### Scenario: CP-31 Intento de inicio de sesión de un usuario dado de baja
- **GIVEN** que una cuenta de usuario se encuentra en estado "Inactivo" (dado de baja)
- **WHEN** el usuario ingresa sus credenciales válidas en la pantalla de Login y hace clic en "Ingresar"
- **THEN** el sistema rechaza la autenticación, no genera token de sesión y muestra el mensaje de alerta "Su cuenta se encuentra inactiva. Contacte al administrador"

### Requirement: Habilitar y reactivar a un usuario inactivo
El sistema DEBE permitir al Administrador General reactivar una cuenta previamente dada de baja, restaurando su capacidad de iniciar sesión y acceder al sistema.

#### Scenario: CP-32 Habilitar / Reactivar a un usuario inactivo
- **GIVEN** que el Administrador General localiza en el módulo "Usuarios" a un usuario en estado "Inactivo"
- **WHEN** ejecuta la acción "Habilitar usuario" y confirma la operación
- **THEN** el sistema actualiza el estado de la cuenta a "Activo" (`is_active = true`), muestra un mensaje de éxito y permite que el usuario recupere su capacidad de iniciar sesión

### Requirement: Protección contra auto-baja del Administrador General
El sistema DEBE impedir que un usuario con rol `ADMIN_GENERAL` se dé de baja a sí mismo.

#### Scenario: Intento de auto-desactivación del Administrador General
- **GIVEN** que el Administrador General intenta cambiar el estado de su propia cuenta a inactiva a través del endpoint o interfaz de usuarios
- **WHEN** el backend recibe la solicitud
- **THEN** el sistema rechaza la operación retornando HTTP 403 Forbidden con un mensaje que prohíbe desactivar la propia cuenta de administrador

