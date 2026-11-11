## ADDED Requirements

### Requirement: Invalidación de sesiones tras cambio de contraseña
El sistema DEBE rechazar con HTTP 401 cualquier token cuyo instante de emisión (`iat`) sea anterior al último cambio de contraseña del usuario (`password_changed_at`), tanto si el cambio fue por restablecimiento como por actualización de perfil. Los usuarios que nunca cambiaron su contraseña (`password_changed_at` nulo) no se ven afectados.

#### Scenario: Token emitido antes del cambio de contraseña
- **GIVEN** un token emitido antes de `password_changed_at`
- **WHEN** se usa en cualquier endpoint protegido
- **THEN** el sistema responde HTTP 401 Unauthorized

#### Scenario: Token emitido después del cambio de contraseña
- **GIVEN** un token emitido en o después de `password_changed_at`
- **WHEN** se usa en un endpoint protegido
- **THEN** el sistema lo acepta

#### Scenario: Usuario que nunca cambió su contraseña
- **GIVEN** un usuario con `password_changed_at` nulo
- **WHEN** usa un token válido
- **THEN** el sistema lo acepta sin cambios respecto al comportamiento actual

#### Scenario: Rutas públicas de recuperación
- **GIVEN** que no hay sesión activa
- **WHEN** el usuario abre `/forgot-password` o `/reset-password`
- **THEN** el sistema muestra la pantalla sin redirigir a `/login`; con sesión activa, redirige al dashboard

