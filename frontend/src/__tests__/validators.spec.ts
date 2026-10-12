import { describe, expect, it } from 'vitest'
import {
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
    it('should accept valid alphanumeric passports (6-20 chars)', () => {
      const valid = ['A1234567', 'PASS123456', 'EC987654321', '12345678']
      valid.forEach((p) => {
        expect(validatePassport(p).isValid).toBe(true)
      })
    })

    it('should reject invalid passports', () => {
      const invalid = ['A1234', 'A'.repeat(21), 'PASS-1234', 'PASS@123']
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
