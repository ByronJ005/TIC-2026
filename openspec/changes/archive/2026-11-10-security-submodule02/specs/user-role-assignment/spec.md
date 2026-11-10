# User Role Assignment Specification

## Purpose
Permitir al Administrador General asignar y actualizar los roles de los usuarios registrados, soportando múltiples roles por usuario y manteniendo el rol "Pasajero" como rol base permanente e inmutable (RF-07).

## Requirements

### Requirement: Rol Pasajero permanente e inmutable
El sistema DEBE garantizar que el rol "Pasajero" (`PASAJERO`) permanezca siempre asignado a cualquier usuario. En el frontend, el control de selección correspondiente a "Pasajero" debe permanecer marcado y bloqueado (`disabled`) contra edición. En el backend, cualquier payload de actualización de roles debe incluir forzosamente el rol `PASAJERO`, rechazando o corrigiendo intentos de eliminación.

#### Scenario: CP-28 Asignación de rol adicional a un usuario (Admin Coop)
- **GIVEN** que el Administrador General se encuentra en el módulo "Usuarios" editando los roles de un usuario existente que solo posee el rol "Pasajero"
- **WHEN** marca la casilla del nuevo rol "Administrador de Cooperativa" y hace clic en "Guardar cambios"
- **THEN** el sistema mantiene el rol "Pasajero" seleccionado (bloqueado contra edición), guarda la actualización en la base de datos persistiendo ambos roles, y asigna el nuevo rol secundario al usuario

#### Scenario: CP-29 Revocación de rol secundario a un usuario (Secretaria)
- **GIVEN** que un usuario posee roles activos múltiples ("Pasajero" y "Secretaria de Cooperativa")
- **WHEN** el Administrador General desde la vista de edición desmarca la casilla "Secretaria de Cooperativa" y hace clic en "Guardar cambios"
- **THEN** el sistema actualiza los registros retirando el rol "Secretaria de Cooperativa", mantiene activo el rol "Pasajero" y revoca el acceso a los módulos correspondientes en la siguiente sesión del usuario

### Requirement: Control de auto-modificación del Administrador General
El sistema DEBE impedir que un usuario con rol `ADMIN_GENERAL` modifique o revoque sus propios roles a través de los endpoints o interfaz de gestión de usuarios.

#### Scenario: Intento de auto-modificación de roles por el Administrador General
- **GIVEN** que un usuario autenticado con rol `ADMIN_GENERAL` intenta modificar sus propios roles enviando una petición a `PUT /api/v1/usuarios/{current_user_id}/roles`
- **WHEN** el backend recibe y procesa la petición
- **THEN** el sistema rechaza la solicitud retornando HTTP 403 Forbidden con un mensaje claro que indica que no es posible modificar los roles de la propia cuenta administrativa

