## ADDED Requirements

### Requirement: Manual logout
The system SHALL allow any authenticated user to close their active session by clicking "Cerrar sesión" from their profile menu. Upon logout, the system SHALL add the token's jti to the blacklist table, remove the token from client storage, and redirect to the login page.

#### Scenario: Successful manual logout
- **WHEN** an authenticated user clicks "Cerrar sesión"
- **THEN** the system blacklists the JWT (by jti), clears the token from localStorage, and redirects to `/login`

### Requirement: Back button restriction after logout
The system SHALL prevent access to protected pages via the browser's back button after logout. Cached views of protected content MUST NOT be displayed.

#### Scenario: Back button after logout shows login page
- **WHEN** a user has logged out and presses the browser's back button
- **THEN** the system denies access to cached protected content and keeps the user on the login page

### Requirement: Multi-tab logout synchronization
The system SHALL detect when a session is invalidated in one tab and enforce it across all open tabs. When a user performs an action in another tab after the token has been invalidated, the system SHALL redirect to login with a "Sesión expirada" message.

#### Scenario: Action in second tab after logout in first tab
- **WHEN** a user logs out in tab 1 and then attempts an action (save, reload) in tab 2
- **THEN** the system detects the invalid token and redirects tab 2 to `/login` with "Sesión expirada" message

#### Scenario: Storage event listener detects token removal
- **WHEN** the auth token is removed from localStorage in any tab
- **THEN** all other tabs listening on the `storage` event clear their auth state and redirect to `/login`

### Requirement: Logout with already expired or invalidated session
The system SHALL handle gracefully the case where a user clicks "Cerrar sesión" but the session is already expired or invalidated. No technical error SHALL be shown.

#### Scenario: Logout when session already expired
- **WHEN** a user clicks "Cerrar sesión" but the token is already expired or blacklisted
- **THEN** the system does not show a technical error and redirects to `/login`

### Requirement: Blacklisted token rejection
The system SHALL check every authenticated request against the blacklist table. Requests with a blacklisted token jti MUST be rejected with HTTP 401.

#### Scenario: Request with blacklisted token
- **WHEN** an HTTP request includes a JWT whose jti exists in the blacklist table
- **THEN** the system rejects the request with HTTP 401 Unauthorized
