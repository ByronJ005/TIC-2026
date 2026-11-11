export interface ValidationResult {
  isValid: boolean
  errorMessage: string
}

export const ERROR_INVALID_DOCUMENT =
  'El número de documento proporcionado es inválido'
export const ERROR_INVALID_NAME =
  'Los nombres/apellidos proporcionados contienen caracteres inválidos'
export const ERROR_INVALID_EMAIL = 'Correo electrónico inválido'
export const ERROR_INVALID_PASSWORD =
  'La contraseña debe contener al menos 8 caracteres e incluir una mayúscula, minúscula, número y carácter especial opcional'
export const ERROR_REQUIRED_FIELD = 'Este campo es requerido'

const NAME_REGEX = /^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s'-]{1,50}$/
const EMAIL_REGEX = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/
const PASSPORT_REGEX = /^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z0-9]{6,20}$/

export function validateRequired(value: string | undefined | null): ValidationResult {
  if (!value || !value.trim()) {
    return { isValid: false, errorMessage: ERROR_REQUIRED_FIELD }
  }
  return { isValid: true, errorMessage: '' }
}

export function validateEcuadorianCedula(cedula: string | undefined | null): ValidationResult {
  if (!cedula || !cedula.trim()) {
    return { isValid: false, errorMessage: ERROR_REQUIRED_FIELD }
  }

  const cleanCedula = cedula.trim()
  if (!/^\d{10}$/.test(cleanCedula)) {
    return { isValid: false, errorMessage: ERROR_INVALID_DOCUMENT }
  }

  const province = parseInt(cleanCedula.substring(0, 2), 10)
  if (province < 1 || (province > 24 && province !== 30)) {
    return { isValid: false, errorMessage: ERROR_INVALID_DOCUMENT }
  }

  const thirdDigit = parseInt(cleanCedula.charAt(2), 10)
  if (thirdDigit >= 6) {
    return { isValid: false, errorMessage: ERROR_INVALID_DOCUMENT }
  }

  const coefficients = [2, 1, 2, 1, 2, 1, 2, 1, 2]
  let totalSum = 0

  for (let i = 0; i < 9; i++) {
    const coeff = coefficients[i] ?? 1
    let product = parseInt(cleanCedula.charAt(i), 10) * coeff
    if (product >= 10) {
      product -= 9
    }
    totalSum += product
  }

  const checkDigit = (10 - (totalSum % 10)) % 10
  const lastDigit = parseInt(cleanCedula.charAt(9), 10)

  if (lastDigit !== checkDigit) {
    return { isValid: false, errorMessage: ERROR_INVALID_DOCUMENT }
  }

  return { isValid: true, errorMessage: '' }
}

export function validatePassport(passport: string | undefined | null): ValidationResult {
  if (!passport || !passport.trim()) {
    return { isValid: false, errorMessage: ERROR_REQUIRED_FIELD }
  }

  const clean = passport.trim()
  if (!PASSPORT_REGEX.test(clean)) {
    return { isValid: false, errorMessage: ERROR_INVALID_DOCUMENT }
  }

  return { isValid: true, errorMessage: '' }
}

export function validateDocument(
  type: 'CEDULA' | 'PASAPORTE',
  number: string | undefined | null,
): ValidationResult {
  if (type === 'CEDULA') {
    return validateEcuadorianCedula(number)
  }
  return validatePassport(number)
}

export function validateName(name: string | undefined | null): ValidationResult {
  if (!name || !name.trim()) {
    return { isValid: false, errorMessage: ERROR_REQUIRED_FIELD }
  }

  const clean = name.trim()
  if (clean.length > 50 || !NAME_REGEX.test(clean)) {
    return { isValid: false, errorMessage: ERROR_INVALID_NAME }
  }

  return { isValid: true, errorMessage: '' }
}

export function validateEmail(email: string | undefined | null): ValidationResult {
  if (!email || !email.trim()) {
    return { isValid: false, errorMessage: ERROR_REQUIRED_FIELD }
  }

  const clean = email.trim()
  if (!EMAIL_REGEX.test(clean)) {
    return { isValid: false, errorMessage: ERROR_INVALID_EMAIL }
  }

  const parts = clean.split('@')
  if (parts.length !== 2) {
    return { isValid: false, errorMessage: ERROR_INVALID_EMAIL }
  }

  const domain = parts[1]
  if (!domain || !domain.includes('.') || domain.startsWith('.') || domain.endsWith('.')) {
    return { isValid: false, errorMessage: ERROR_INVALID_EMAIL }
  }

  const tld = domain.split('.').pop()
  if (!tld || tld.length < 2) {
    return { isValid: false, errorMessage: ERROR_INVALID_EMAIL }
  }

  return { isValid: true, errorMessage: '' }
}

export function validatePassword(password: string | undefined | null): ValidationResult {
  if (!password || !password.trim()) {
    return { isValid: false, errorMessage: ERROR_REQUIRED_FIELD }
  }

  if (password.length < 8) {
    return { isValid: false, errorMessage: ERROR_INVALID_PASSWORD }
  }

  const hasUpper = /[A-Z]/.test(password)
  const hasLower = /[a-z]/.test(password)
  const hasDigit = /\d/.test(password)

  if (!hasUpper || !hasLower || !hasDigit) {
    return { isValid: false, errorMessage: ERROR_INVALID_PASSWORD }
  }

  return { isValid: true, errorMessage: '' }
}

export function normalizeEmail(email: string): string {
  return (email || '').trim().toLowerCase()
}

export const MIN_BIRTH_DATE = '1900-01-01'
export const PHONE_LENGTH = 10
export const ADDRESS_MAX_LENGTH = 150

export const ERROR_EMAIL_REQUIRED = 'Se requiere el correo electrónico'
export const ERROR_MANDATORY_FIELDS_EMPTY = 'Los campos obligatorios no pueden quedar vacíos'
export const ERROR_PHONE_LENGTH = 'El número de celular debe tener exactamente 10 dígitos'
export const ERROR_PHONE_NOT_NUMERIC = 'El celular solo debe contener números'
export const ERROR_ADDRESS_TOO_LONG = 'La dirección no puede exceder los 150 caracteres'
export const ERROR_INVALID_BIRTH_DATE =
  'La fecha de nacimiento debe estar entre 1900 y la fecha actual'
export const ERROR_CURRENT_PASSWORD_REQUIRED = 'Debe ingresar su contraseña actual para cambiarla'
export const ERROR_CURRENT_PASSWORD_WRONG = 'La contraseña actual es incorrecta'
export const ERROR_NEW_PASSWORD_SAME_AS_CURRENT =
  'La nueva contraseña debe ser diferente de la actual'
export const ERROR_PASSWORD_CONFIRMATION_MISMATCH =
  'La confirmación no coincide con la nueva contraseña'

const VALID_RESULT: ValidationResult = { isValid: true, errorMessage: '' }
const ISO_DATE_REGEX = /^(\d{4})-(\d{2})-(\d{2})$/
const PHONE_DIGITS_REGEX = /^[0-9]+$/

function invalid(errorMessage: string): ValidationResult {
  return { isValid: false, errorMessage }
}

function isBlank(value: string | undefined | null): boolean {
  return !value || !value.trim()
}

/** Phone is optional; non-numeric characters take precedence over length errors. */
export function validatePhone(phone: string | undefined | null): ValidationResult {
  if (isBlank(phone)) return VALID_RESULT
  if (!PHONE_DIGITS_REGEX.test(phone as string)) return invalid(ERROR_PHONE_NOT_NUMERIC)
  if ((phone as string).length !== PHONE_LENGTH) return invalid(ERROR_PHONE_LENGTH)
  return VALID_RESULT
}

/** Address is optional and limited to 150 characters (without surrounding spaces). */
export function validateAddress(address: string | undefined | null): ValidationResult {
  if (isBlank(address)) return VALID_RESULT
  if ((address as string).trim().length > ADDRESS_MAX_LENGTH) return invalid(ERROR_ADDRESS_TOO_LONG)
  return VALID_RESULT
}

/** Formats a date as YYYY-MM-DD using the local calendar day (matches <input type="date">). */
export function toIsoDate(date: Date): string {
  const year = String(date.getFullYear()).padStart(4, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function isRealCalendarDate(year: number, month: number, day: number): boolean {
  const candidate = new Date(year, month - 1, day)
  return (
    candidate.getFullYear() === year &&
    candidate.getMonth() === month - 1 &&
    candidate.getDate() === day
  )
}

/**
 * Birth date is optional and must be between 1900-01-01 and today (inclusive).
 * The upper bound comes from `today`, never from a hardcoded year.
 */
export function validateBirthDate(
  value: string | undefined | null,
  today: Date = new Date(),
): ValidationResult {
  if (isBlank(value)) return VALID_RESULT

  const match = ISO_DATE_REGEX.exec((value as string).trim())
  if (!match) return invalid(ERROR_INVALID_BIRTH_DATE)

  const [, year, month, day] = match
  if (!isRealCalendarDate(Number(year), Number(month), Number(day))) {
    return invalid(ERROR_INVALID_BIRTH_DATE)
  }

  const isoDate = (value as string).trim()
  if (isoDate < MIN_BIRTH_DATE || isoDate > toIsoDate(today)) {
    return invalid(ERROR_INVALID_BIRTH_DATE)
  }
  return VALID_RESULT
}

/** Email on the recovery screen: blank has its own message, then the registration format rules. */
export function validateRecoveryEmail(email: string | undefined | null): ValidationResult {
  if (isBlank(email)) return invalid(ERROR_EMAIL_REQUIRED)
  return validateEmail(email)
}

export function useFormValidation() {
  return {
    validateRequired,
    validateEcuadorianCedula,
    validatePassport,
    validateDocument,
    validateName,
    validateEmail,
    validatePassword,
    validatePhone,
    validateAddress,
    validateBirthDate,
    validateRecoveryEmail,
    normalizeEmail,
  }
}

