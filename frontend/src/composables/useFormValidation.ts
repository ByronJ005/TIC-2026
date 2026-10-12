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
  'La contraseña debe incluir al menos una mayúscula, minúscula, número y carácter especial opcional'
export const ERROR_REQUIRED_FIELD = 'Este campo es requerido'

const NAME_REGEX = /^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s'-]{1,50}$/
const EMAIL_REGEX = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/
const PASSPORT_REGEX = /^[a-zA-Z0-9]{6,20}$/

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

export function useFormValidation() {
  return {
    validateRequired,
    validateEcuadorianCedula,
    validatePassport,
    validateDocument,
    validateName,
    validateEmail,
    validatePassword,
    normalizeEmail,
  }
}
