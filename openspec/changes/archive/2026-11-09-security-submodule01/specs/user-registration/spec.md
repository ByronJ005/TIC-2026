## ADDED Requirements

### Requirement: User registration with valid data
The system SHALL allow unauthenticated users to create an account by submitting: document type (CEDULA or PASAPORTE), document number, first name, last name, email, and password. Upon successful registration, the system SHALL persist the user with role PASAJERO, display the message "Cuenta creada satisfactoriamente", and redirect to the login page after approximately 2 seconds.

#### Scenario: Successful registration with all valid fields
- **WHEN** an unauthenticated user submits the registration form with valid document type, document number, first name, last name, email, and password
- **THEN** the system creates the account in the database with role PASAJERO, displays "Cuenta creada satisfactoriamente", and redirects to `/login`

#### Scenario: Role is always PASAJERO
- **WHEN** a user registers via the public registration form
- **THEN** the system assigns the role PASAJERO regardless of any client-side manipulation

### Requirement: Cédula validation
The system SHALL validate that a document number of type CEDULA complies with the Ecuadorian cédula algorithm (10 digits, modulo-10 check digit). Both frontend and backend MUST enforce this validation.

#### Scenario: Invalid cédula format rejected
- **WHEN** a user submits a registration form with document type CEDULA and a number that fails the modulo-10 algorithm
- **THEN** the system rejects the registration and displays "El número de documento proporcionado es inválido"

#### Scenario: Valid cédula accepted
- **WHEN** a user submits a registration form with document type CEDULA and a number that passes the modulo-10 algorithm
- **THEN** the system accepts the document number for registration

### Requirement: Strict passport validation
The system SHALL validate that a document number of type PASAPORTE is strictly alphanumeric containing at least one letter and at least one digit, and has a length between 6 and 20 characters. Both frontend and backend MUST enforce this validation. Values composed entirely of letters (such as "AAOOOOKKK") or entirely of digits MUST be rejected.

#### Scenario: Invalid passport length or special characters rejected
- **WHEN** a user submits a registration form with document type PASAPORTE and a value containing symbols or with length outside 6-20 characters
- **THEN** the system rejects the registration and displays "El número de documento proporcionado es inválido"

#### Scenario: Passport with only letters or only digits rejected
- **WHEN** a user submits a registration form with document type PASAPORTE containing only letters (e.g. "AAOOOOKKK") or only digits (e.g. "12345678")
- **THEN** the system rejects the registration and displays "El número de documento proporcionado es inválido"

#### Scenario: Valid strict alphanumeric passport accepted
- **WHEN** a user submits a registration form with document type PASAPORTE containing at least one letter and at least one digit, between 6 and 20 characters (e.g. "A1234567")
- **THEN** the system accepts the document number for registration

### Requirement: Name and surname validation
The system SHALL validate that first name and last name fields contain only Unicode letters, spaces, hyphens, and apostrophes, with a maximum length of 50 characters each. Both frontend and backend MUST enforce this validation.

#### Scenario: Invalid characters in name rejected
- **WHEN** a user submits names or surnames containing characters outside the allowed set (letters, spaces, hyphens, apostrophes) or exceeding 50 characters
- **THEN** the system rejects the registration and displays "Los nombres/apellidos proporcionados contienen caracteres inválidos"

### Requirement: Email format validation
The system SHALL validate that the email field contains a valid format with an '@' symbol and a valid top-level domain. Both frontend and backend MUST enforce this validation.

#### Scenario: Invalid email format rejected
- **WHEN** a user submits an email without '@' or without a valid top-level domain
- **THEN** the system rejects the registration and displays "Correo electrónico inválido"

### Requirement: Password strength validation
The system SHALL require passwords to be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number. A special character is optional. Both frontend and backend MUST enforce this validation with the error message: "La contraseña debe contener al menos 8 caracteres e incluir una mayúscula, minúscula, número y carácter especial opcional".

#### Scenario: Weak password rejected
- **WHEN** a user submits a password missing an uppercase letter, lowercase letter, number, or shorter than 8 characters
- **THEN** the system rejects the registration and displays "La contraseña debe contener al menos 8 caracteres e incluir una mayúscula, minúscula, número y carácter especial opcional"

### Requirement: Required fields enforcement
The system SHALL prevent registration when any required field is empty or contains only whitespace. Both frontend and backend MUST enforce this validation.

#### Scenario: Empty or whitespace-only fields rejected
- **WHEN** a user submits the registration form with any required field empty or filled only with whitespace
- **THEN** the system does not process the registration and marks the missing fields as required

### Requirement: Unique email constraint
The system SHALL enforce that each email address is unique across all user accounts.

#### Scenario: Duplicate email rejected
- **WHEN** a user attempts to register with an email that already exists in the database
- **THEN** the system rejects the registration and displays a message indicating the email is already registered

### Requirement: Unique document constraint
The system SHALL enforce that each combination of document type and document number is unique across all user accounts.

#### Scenario: Duplicate document rejected
- **WHEN** a user attempts to register with a document type and number combination that already exists
- **THEN** the system rejects the registration and displays a message indicating the document is already registered
