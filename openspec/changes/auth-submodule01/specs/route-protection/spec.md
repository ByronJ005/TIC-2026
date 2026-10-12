## ADDED Requirements

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
