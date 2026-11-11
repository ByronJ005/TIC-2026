# Route Protection Specification

## Purpose
Establecer el control de acceso a rutas tanto en el frontend como en el backend, garantizando que los recursos protegidos requieran un token JWT válido y que las rutas públicas/de invitados gestionen adecuadamente la redirección de usuarios según su estado de autenticación.

## Requirements

### Requirement: Protected route redirect for unauthenticated users
The system SHALL redirect unauthenticated users to `/login` when they attempt to access any protected route (e.g., `/dashboard`). No protected information SHALL be displayed.

#### Scenario: Direct URL access without session
- **WHEN** an unauthenticated user navigates directly to `/dashboard`
- **THEN** the system redirects to `/login` and does not display any protected content

#### Scenario: Navigation guard blocks all protected routes
- **WHEN** an unauthenticated user attempts to access any route that requires authentication
- **THEN** the Vue Router navigation guard redirects to `/login` before the component loads

### Requirement: Authenticated user redirect from login page
The system SHALL redirect authenticated users away from the login page to their dashboard.

#### Scenario: Authenticated user visits /login
- **WHEN** an authenticated user navigates manually to `/login`
- **THEN** the system redirects to `/dashboard`

#### Scenario: Authenticated user visits /register
- **WHEN** an authenticated user navigates manually to `/register`
- **THEN** the system redirects to `/dashboard`

### Requirement: Backend endpoint protection
The system SHALL protect API endpoints using a `get_current_user` dependency that validates the JWT from the Authorization header. Requests without a valid token MUST receive HTTP 401.

#### Scenario: API request without Authorization header
- **WHEN** an HTTP request targets a protected endpoint without an Authorization header
- **THEN** the system responds with HTTP 401 Unauthorized

#### Scenario: API request with expired token
- **WHEN** an HTTP request includes an expired JWT in the Authorization header
- **THEN** the system responds with HTTP 401 Unauthorized

#### Scenario: API request with valid token
- **WHEN** an HTTP request includes a valid, non-expired, non-blacklisted JWT
- **THEN** the system allows the request and injects the current user into the endpoint

### Requirement: HTTP interceptor handles 401
The frontend HTTP client SHALL intercept 401 responses from any API call, clear the auth state, and redirect to `/login` with a "Sesión expirada" message.

#### Scenario: API returns 401 during user session
- **WHEN** any API call returns HTTP 401 while the user appears to be logged in
- **THEN** the frontend clears the auth token and state, and redirects to `/login` displaying "Sesión expirada"

### Requirement: Anti-cache headers for protected pages
The system SHALL set appropriate cache-control headers to prevent the browser from caching protected page content.

#### Scenario: Protected page not served from cache after logout
- **WHEN** a user logs out and uses the back button
- **THEN** the browser does not display cached protected content due to no-store/no-cache headers


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
