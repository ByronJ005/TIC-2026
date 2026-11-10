## ADDED Requirements

### Requirement: Successful login with valid credentials
The system SHALL authenticate users by email and password. Upon successful authentication, the system SHALL return a JWT access token (30-minute TTL) containing user_id, role, and a unique jti, and redirect the user to their dashboard.

#### Scenario: Login with correct credentials
- **WHEN** a registered user submits their correct email and password
- **THEN** the system authenticates the user, returns a JWT access token, and redirects to `/dashboard`

#### Scenario: Login returns token with correct payload
- **WHEN** a user successfully authenticates
- **THEN** the returned JWT contains `sub` (user_id), `role`, `jti` (UUID), and `exp` (30 minutes from now)

### Requirement: Login with invalid credentials
The system SHALL reject authentication when email or password is incorrect and display a generic error message that does not reveal whether the email exists.

#### Scenario: Wrong password
- **WHEN** a user submits a valid email but an incorrect password
- **THEN** the system denies access and displays "Credenciales incorrectas"

#### Scenario: Non-existent email
- **WHEN** a user submits an email that does not exist in the system
- **THEN** the system denies access and displays "Credenciales incorrectas" (same message as wrong password)

### Requirement: Login field validation
The system SHALL prevent login submission when email or password fields are empty or contain only whitespace.

#### Scenario: Empty fields prevent submission
- **WHEN** a user attempts to login with empty email or password fields, or fields containing only whitespace
- **THEN** the system prevents form submission and requires the fields to be completed

### Requirement: Email normalization on login
The system SHALL normalize the email input by trimming leading/trailing whitespace and converting to lowercase before authentication.

#### Scenario: Case-insensitive email with surrounding spaces
- **WHEN** a user enters " J.Perez@Email.com " with the correct password
- **THEN** the system normalizes to "j.perez@email.com" and grants access

### Requirement: Password hashing
The system SHALL store passwords as bcrypt hashes (work factor 12) and SHALL never store or log passwords in plain text.

#### Scenario: Password stored as hash
- **WHEN** a user registers or the system processes a password
- **THEN** the password is stored as a bcrypt hash, never in plain text
