import { describe, expect, it } from 'vitest'
import {
  ERROR_ADDRESS_TOO_LONG,
  ERROR_EMAIL_REQUIRED,
  ERROR_INVALID_BIRTH_DATE,
  ERROR_PHONE_LENGTH,
  ERROR_PHONE_NOT_NUMERIC,
  toIsoDate,
  validateAddress,
  validateBirthDate,
  validatePhone,
  validateRecoveryEmail,
  ERROR_INVALID_DOCUMENT,
  ERROR_INVALID_EMAIL,
  ERROR_INVALID_NAME,
  ERROR_INVALID_PASSWORD,
  ERROR_REQUIRED_FIELD,
  normalizeEmail,
  validateDocument,
  validateEcuadorianCedula,
  validateEmail,
  validateName,
  validatePassport,
  validatePassword,
  validateRequired,
} from '@/composables/useFormValidation'

describe('useFormValidation Composable', () => {
  describe('validateRequired', () => {
    it('should reject empty or whitespace strings', () => {
      expect(validateRequired('')).toEqual({
        isValid: false,
        errorMessage: ERROR_REQUIRED_FIELD,
      })
      expect(validateRequired('   ')).toEqual({
        isValid: false,
        errorMessage: ERROR_REQUIRED_FIELD,
      })
      expect(validateRequired(null)).toEqual({
        isValid: false,
        errorMessage: ERROR_REQUIRED_FIELD,
      })
    })

    it('should accept non-empty string', () => {
      expect(validateRequired('texto')).toEqual({
        isValid: true,
        errorMessage: '',
      })
    })
  })

  describe('validateEcuadorianCedula', () => {
    it('14.1: should validate correct Ecuadorian cédulas', () => {
      const validCedulas = [
        '1710034065',
        '0926691452',
        '1104609829',
        '0102555547',
      ]
      validCedulas.forEach((c) => {
        const res = validateEcuadorianCedula(c)
        expect(res.isValid).toBe(true)
        expect(res.errorMessage).toBe('')
      })
    })

    it('14.1: should reject invalid Ecuadorian cédulas', () => {
      const invalidCedulas = [
        '1710034066', // wrong check digit
        '1234567890', // invalid
        '9910034065', // invalid province
        '1780034065', // 3rd digit >= 6
        '171003406',  // 9 digits
        '17100340651', // 11 digits
        'abcdefghij', // non-digit
      ]
      invalidCedulas.forEach((c) => {
        const res = validateEcuadorianCedula(c)
        expect(res.isValid).toBe(false)
        expect(res.errorMessage).toBe(ERROR_INVALID_DOCUMENT)
      })
    })
  })

  describe('validatePassport', () => {
    it('should accept valid strict alphanumeric passports (letters and digits, 6-20 chars)', () => {
      const valid = ['A1234567', 'PASS123456', 'EC987654321']
      valid.forEach((p) => {
        expect(validatePassport(p).isValid).toBe(true)
      })
    })

    it('should reject invalid passports (letters only, numbers only, special chars, length)', () => {
      const invalid = [
        'AAOOOOKKK', // letters only rejected
        '12345678',  // digits only rejected
        'A1234',     // < 6 chars
        'A1' + 'A'.repeat(19), // > 20 chars
        'PASS-1234',
        'PASS@123',
      ]
      invalid.forEach((p) => {
        const res = validatePassport(p)
        expect(res.isValid).toBe(false)
        expect(res.errorMessage).toBe(ERROR_INVALID_DOCUMENT)
      })
    })
  })

  describe('validateDocument', () => {
    it('routes correctly to cedula or passport', () => {
      expect(validateDocument('CEDULA', '1710034065').isValid).toBe(true)
      expect(validateDocument('PASAPORTE', 'PASS123456').isValid).toBe(true)
    })
  })

  describe('validateName', () => {
    it('14.4: should accept valid Unicode names up to 50 chars', () => {
      const valid = ["Juan Carlos", "María-José", "O'Connor", "Ángel René"]
      valid.forEach((n) => {
        expect(validateName(n).isValid).toBe(true)
      })
    })

    it('14.4: should reject names with invalid characters or exceeding 50 chars', () => {
      const invalid = ['Juan123', 'Maria_Jose', 'Carlos@home', 'A'.repeat(51)]
      invalid.forEach((n) => {
        const res = validateName(n)
        expect(res.isValid).toBe(false)
        expect(res.errorMessage).toBe(ERROR_INVALID_NAME)
      })
    })
  })

  describe('validateEmail', () => {
    it('14.3: should accept standard emails', () => {
      expect(validateEmail('test@example.com').isValid).toBe(true)
      expect(validateEmail('user.name+tag@sub.domain.edu.ec').isValid).toBe(true)
    })

    it('14.3: should reject malformed emails', () => {
      const invalid = ['testexample.com', 'test@', 'test@domain', 'test@.com']
      invalid.forEach((e) => {
        const res = validateEmail(e)
        expect(res.isValid).toBe(false)
        expect(res.errorMessage).toBe(ERROR_INVALID_EMAIL)
      })
    })
  })

  describe('validatePassword', () => {
    it('14.2: should accept passwords with uppercase, lowercase, digit, >=8 chars', () => {
      expect(validatePassword('Password123').isValid).toBe(true)
      expect(validatePassword('P@ssw0rd!#').isValid).toBe(true)
    })

    it('14.2: should reject passwords not meeting criteria', () => {
      const invalid = [
        'short1A',      // < 8 chars
        'alllower123',  // missing upper
        'ALLUPPER123',  // missing lower
        'NoDigitsHere', // missing digit
      ]
      invalid.forEach((pwd) => {
        const res = validatePassword(pwd)
        expect(res.isValid).toBe(false)
        expect(res.errorMessage).toBe(ERROR_INVALID_PASSWORD)
      })
    })
  })

  describe('normalizeEmail', () => {
    it('should trim and lowercase email', () => {
      expect(normalizeEmail('  J.Perez@Email.COM  ')).toBe('j.perez@email.com')
    })
  })
})

describe('Profile and recovery validators', () => {
  describe('validatePhone', () => {
    it.each(['0991234567', '0000000000'])('accepts exactly 10 digits: %s', (phone) => {
      expect(validatePhone(phone).isValid).toBe(true)
    })

    it.each(['', '   ', null, undefined])('accepts blank optional value: %s', (phone) => {
      expect(validatePhone(phone).isValid).toBe(true)
    })

    it.each(['099123456', '09912345678', '1'])('reports length error for %s', (phone) => {
      expect(validatePhone(phone)).toEqual({ isValid: false, errorMessage: ERROR_PHONE_LENGTH })
    })

    it.each(['09912345ab', '099-123-456', '099 123 4567', ' 0991234567', '+593991234', 'abc'])(
      'reports non numeric error for %s',
      (phone) => {
        expect(validatePhone(phone)).toEqual({
          isValid: false,
          errorMessage: ERROR_PHONE_NOT_NUMERIC,
        })
      },
    )
  })

  describe('validateAddress', () => {
    it.each([1, 149, 150])('accepts %i characters', (length) => {
      expect(validateAddress('a'.repeat(length)).isValid).toBe(true)
    })

    it('rejects 151 characters', () => {
      expect(validateAddress('a'.repeat(151))).toEqual({
        isValid: false,
        errorMessage: ERROR_ADDRESS_TOO_LONG,
      })
    })

    it('accepts blank values and ignores surrounding spaces when counting', () => {
      expect(validateAddress('').isValid).toBe(true)
      expect(validateAddress('    ').isValid).toBe(true)
      expect(validateAddress(`  ${'a'.repeat(150)}  `).isValid).toBe(true)
    })
  })

  describe('validateBirthDate', () => {
    const today = new Date(2026, 10, 10) // 10 Nov 2026 (local)

    it.each(['1900-01-01', '1985-06-15', '2026-11-09', '2026-11-10'])('accepts %s', (date) => {
      expect(validateBirthDate(date, today).isValid).toBe(true)
    })

    it.each(['1899-12-31', '2026-11-11', '2026-12-31', '2027-01-01'])('rejects %s', (date) => {
      expect(validateBirthDate(date, today)).toEqual({
        isValid: false,
        errorMessage: ERROR_INVALID_BIRTH_DATE,
      })
    })

    it.each(['no-es-fecha', '2025-02-30', '31/12/1990', '2025-13-01', '1990-1-1'])(
      'rejects malformed or impossible date %s',
      (date) => {
        expect(validateBirthDate(date, today).isValid).toBe(false)
      },
    )

    it('accepts blank values because the field is optional', () => {
      expect(validateBirthDate('', today).isValid).toBe(true)
      expect(validateBirthDate(null, today).isValid).toBe(true)
    })

    it('computes the upper bound from the reference day, not from a fixed year', () => {
      const futureReference = new Date(2030, 2, 1)

      expect(validateBirthDate('2030-03-01', today).isValid).toBe(false)
      expect(validateBirthDate('2030-03-01', futureReference).isValid).toBe(true)
    })

    it('uses the current date by default', () => {
      const now = new Date()
      const tomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1)

      expect(validateBirthDate(toIsoDate(now)).isValid).toBe(true)
      expect(validateBirthDate(toIsoDate(tomorrow)).isValid).toBe(false)
    })
  })

  describe('toIsoDate', () => {
    it('pads month and day', () => {
      expect(toIsoDate(new Date(2026, 0, 5))).toBe('2026-01-05')
    })
  })

  describe('validateRecoveryEmail', () => {
    it.each(['', '   ', null, undefined])('uses the required message for %s', (email) => {
      expect(validateRecoveryEmail(email)).toEqual({
        isValid: false,
        errorMessage: ERROR_EMAIL_REQUIRED,
      })
    })

    it('reuses the registration email format rules', () => {
      expect(validateRecoveryEmail('sin-arroba').isValid).toBe(false)
      expect(validateRecoveryEmail('ana@example.com').isValid).toBe(true)
    })
  })
})
