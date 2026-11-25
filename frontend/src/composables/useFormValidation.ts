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

export const ERROR_RUC_REQUIRED = 'El RUC es obligatorio'
export const ERROR_RUC_LENGTH_OR_FORMAT = 'El RUC debe tener exactamente 13 dígitos numéricos'
export const ERROR_RUC_INVALID_ALGORITHM = 'El RUC ingresado no es válido según el estándar ecuatoriano'
export const ERROR_COOP_NAME_EMPTY = 'El nombre de la cooperativa no puede quedar vacío'
export const ERROR_COOP_NAME_INVALID_CHARS =
  'El nombre solo puede contener letras, números, espacios, guiones medios y apóstrofes'
export const ERROR_COOP_NAME_TOO_LONG = 'El nombre de la cooperativa no puede exceder los 100 caracteres'

const NAME_REGEX = /^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s'-]{1,50}$/
const COOP_NAME_REGEX = /^[A-Za-z0-9ÁÉÍÓÚáéíóúÑñÜü\s'-]+$/
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

export function validateCooperativaName(name: string | undefined | null): ValidationResult {
  if (isBlank(name)) return invalid(ERROR_COOP_NAME_EMPTY)
  const trimmed = (name as string).trim()
  if (trimmed.length > 100) return invalid(ERROR_COOP_NAME_TOO_LONG)
  if (!COOP_NAME_REGEX.test(trimmed)) return invalid(ERROR_COOP_NAME_INVALID_CHARS)
  return VALID_RESULT
}

export function validateEcuadorianRuc(ruc: string | undefined | null): ValidationResult {
  if (isBlank(ruc)) return invalid(ERROR_RUC_REQUIRED)
  const cleanRuc = (ruc as string).trim()
  if (!/^\d{13}$/.test(cleanRuc)) return invalid(ERROR_RUC_LENGTH_OR_FORMAT)

  const province = parseInt(cleanRuc.substring(0, 2), 10)
  if (province < 1 || (province > 24 && province !== 30)) {
    return invalid(ERROR_RUC_INVALID_ALGORITHM)
  }

  const thirdDigit = parseInt(cleanRuc.charAt(2), 10)

  // 1. Persona natural (0-5)
  if (thirdDigit < 6) {
    const cedulaValidation = validateEcuadorianCedula(cleanRuc.substring(0, 10))
    if (!cedulaValidation.isValid) {
      return invalid(ERROR_RUC_INVALID_ALGORITHM)
    }
    const establishment = parseInt(cleanRuc.substring(10), 10)
    if (establishment < 1) {
      return invalid(ERROR_RUC_INVALID_ALGORITHM)
    }
    return VALID_RESULT
  }

  // 2. Sociedades públicas (6)
  if (thirdDigit === 6) {
    const coefficients = [3, 2, 7, 6, 5, 4, 3, 2]
    let totalSum = 0
    for (let i = 0; i < 8; i++) {
      totalSum += parseInt(cleanRuc.charAt(i), 10) * (coefficients[i] ?? 0)
    }
    const remainder = totalSum % 11
    const verifier = remainder === 0 ? 0 : 11 - remainder
    if (parseInt(cleanRuc.charAt(8), 10) !== verifier) {
      return invalid(ERROR_RUC_INVALID_ALGORITHM)
    }
    const establishment = parseInt(cleanRuc.substring(9), 10)
    if (establishment < 1) {
      return invalid(ERROR_RUC_INVALID_ALGORITHM)
    }
    return VALID_RESULT
  }

  // 3. Sociedades privadas / jurídicas (9)
  if (thirdDigit === 9) {
    const coefficients = [4, 3, 2, 7, 6, 5, 4, 3, 2]
    let totalSum = 0
    for (let i = 0; i < 9; i++) {
      totalSum += parseInt(cleanRuc.charAt(i), 10) * (coefficients[i] ?? 0)
    }
    const remainder = totalSum % 11
    const verifier = remainder === 0 ? 0 : 11 - remainder
    if (parseInt(cleanRuc.charAt(9), 10) !== verifier) {
      return invalid(ERROR_RUC_INVALID_ALGORITHM)
    }
    const establishment = parseInt(cleanRuc.substring(10), 10)
    if (establishment < 1) {
      return invalid(ERROR_RUC_INVALID_ALGORITHM)
    }
    return VALID_RESULT
  }

  return invalid(ERROR_RUC_INVALID_ALGORITHM)
}

// Submodule 05 - Rutas, Localidades y Notificaciones
export const ERROR_ORIGIN_REQUIRED = 'El origen es obligatorio'
export const ERROR_DESTINATION_REQUIRED = 'El destino es obligatorio'
export const ERROR_DISTANCE_REQUIRED = 'La distancia es obligatoria'
export const ERROR_TIME_REQUIRED = 'El tiempo estimado es obligatorio'
export const ERROR_ROUTE_ORIGIN_DESTINATION_SAME = 'El origen y el destino deben ser diferentes'
export const ERROR_ROUTE_STOP_EQUALS_ORIGIN_OR_DESTINATION =
  'Una parada intermedia no puede ser igual al origen o al destino'
export const ERROR_ROUTE_STOP_DUPLICATED = 'La localidad ya fue agregada como parada de esta ruta'
export const ERROR_ROUTE_STOPS_EMPTY =
  "Debe agregar al menos una parada intermedia o marcar la opción 'Solo las de origen y destino'"
export const ERROR_ROUTE_DISTANCE_INVALID = 'La distancia debe ser un número mayor a 0'
export const ERROR_ROUTE_TIME_INVALID =
  'Ingrese un tiempo estimado válido. El tiempo total debe ser mayor a cero y los minutos deben estar entre 0 y 59'
export const ERROR_LOCALITY_NAME_EMPTY = 'El nombre de la localidad no puede quedar vacío'
export const ERROR_LOCALITY_NAME_TOO_LONG = 'El nombre de la localidad no puede exceder los 100 caracteres'
export const ERROR_ROUTE_NAME_SUFFIX_TOO_LONG = 'El texto adicional del nombre no puede exceder los 30 caracteres'
export const ERROR_ROUTE_DESCRIPTION_TOO_LONG = 'La descripción no puede exceder los 100 caracteres'

export function validateLocalityName(name: string | undefined | null): ValidationResult {
  if (!name || !name.trim()) {
    return invalid(ERROR_LOCALITY_NAME_EMPTY)
  }
  const clean = name.trim().replace(/\s+/g, ' ')
  if (clean.length > 100) {
    return invalid(ERROR_LOCALITY_NAME_TOO_LONG)
  }
  return VALID_RESULT
}

export function validateRouteNameSuffix(suffix: string | undefined | null): ValidationResult {
  if (!suffix) return VALID_RESULT
  if (suffix.trim().length > 30) {
    return invalid(ERROR_ROUTE_NAME_SUFFIX_TOO_LONG)
  }
  return VALID_RESULT
}

export function validateRouteDescription(desc: string | undefined | null): ValidationResult {
  if (!desc) return VALID_RESULT
  if (desc.trim().length > 100) {
    return invalid(ERROR_ROUTE_DESCRIPTION_TOO_LONG)
  }
  return VALID_RESULT
}

export function validateRouteDistance(dist: number | string | undefined | null): ValidationResult {
  if (dist === undefined || dist === null || dist === '') {
    return invalid(ERROR_DISTANCE_REQUIRED)
  }
  const num = typeof dist === 'number' ? dist : parseFloat(String(dist))
  if (isNaN(num) || num <= 0) {
    return invalid(ERROR_ROUTE_DISTANCE_INVALID)
  }
  return VALID_RESULT
}

export function validateRouteTime(
  hours: number | string | undefined | null,
  minutes: number | string | undefined | null,
): ValidationResult {
  if (
    (hours === undefined || hours === null || hours === '') &&
    (minutes === undefined || minutes === null || minutes === '')
  ) {
    return invalid(ERROR_TIME_REQUIRED)
  }
  const h = hours ? parseInt(String(hours), 10) : 0
  const m = minutes ? parseInt(String(minutes), 10) : 0

  if (isNaN(h) || isNaN(m) || h < 0 || m < 0 || m > 59) {
    return invalid(ERROR_ROUTE_TIME_INVALID)
  }
  const totalMinutes = h * 60 + m
  if (totalMinutes <= 0 || totalMinutes > 5999) {
    return invalid(ERROR_ROUTE_TIME_INVALID)
  }
  return VALID_RESULT
}

export function validateRouteOriginAndDestination(
  originId: number | undefined | null,
  destId: number | undefined | null,
): ValidationResult {
  if (!originId) return invalid(ERROR_ORIGIN_REQUIRED)
  if (!destId) return invalid(ERROR_DESTINATION_REQUIRED)
  if (originId === destId) return invalid(ERROR_ROUTE_ORIGIN_DESTINATION_SAME)
  return VALID_RESULT
}

export function validateRouteStops(
  originId: number | undefined | null,
  destId: number | undefined | null,
  onlyOriginDest: boolean,
  stops: Array<{ locality_id: number; stop_order: number }> = [],
): ValidationResult {
  if (onlyOriginDest) return VALID_RESULT

  if (!stops || stops.length === 0) {
    return invalid(ERROR_ROUTE_STOPS_EMPTY)
  }

  const seen = new Set<number>()
  for (const s of stops) {
    if (!s.locality_id) {
      return invalid(ERROR_ROUTE_STOPS_EMPTY)
    }
    if (originId && s.locality_id === originId) {
      return invalid(ERROR_ROUTE_STOP_EQUALS_ORIGIN_OR_DESTINATION)
    }
    if (destId && s.locality_id === destId) {
      return invalid(ERROR_ROUTE_STOP_EQUALS_ORIGIN_OR_DESTINATION)
    }
    if (seen.has(s.locality_id)) {
      return invalid(ERROR_ROUTE_STOP_DUPLICATED)
    }
    seen.add(s.locality_id)
  }
  return VALID_RESULT
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
    validateCooperativaName,
    validateEcuadorianRuc,
    validateLocalityName,
    validateRouteNameSuffix,
    validateRouteDescription,
    validateRouteDistance,
    validateRouteTime,
    validateRouteOriginAndDestination,
    validateRouteStops,
    normalizeEmail,
  }
}

