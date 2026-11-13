import { describe, expect, it } from 'vitest'
import {
  ERROR_COOP_NAME_EMPTY,
  ERROR_COOP_NAME_INVALID_CHARS,
  ERROR_COOP_NAME_TOO_LONG,
  ERROR_RUC_INVALID_ALGORITHM,
  ERROR_RUC_LENGTH_OR_FORMAT,
  ERROR_RUC_REQUIRED,
  validateCooperativaName,
  validateEcuadorianRuc,
} from '@/composables/useFormValidation'

describe('Cooperativa and RUC Validators', () => {
  describe('validateEcuadorianRuc', () => {
    it('accepts valid natural person RUC', () => {
      const res = validateEcuadorianRuc('1104609829001')
      expect(res.isValid).toBe(true)
      expect(res.errorMessage).toBe('')
    })

    it('accepts valid private society RUC (digit 9)', () => {
      const res = validateEcuadorianRuc('1790011216001')
      expect(res.isValid).toBe(true)
      expect(res.errorMessage).toBe('')
    })

    it('accepts valid public society RUC (digit 6)', () => {
      const res = validateEcuadorianRuc('1760001550001')
      expect(res.isValid).toBe(true)
      expect(res.errorMessage).toBe('')
    })

    it('rejects length different from 13 digits', () => {
      expect(validateEcuadorianRuc('1104609829').errorMessage).toBe(ERROR_RUC_LENGTH_OR_FORMAT)
      expect(validateEcuadorianRuc('110460982900111').errorMessage).toBe(ERROR_RUC_LENGTH_OR_FORMAT)
    })

    it('rejects empty or whitespace RUC with required error', () => {
      expect(validateEcuadorianRuc('').errorMessage).toBe(ERROR_RUC_REQUIRED)
      expect(validateEcuadorianRuc('   ').errorMessage).toBe(ERROR_RUC_REQUIRED)
    })

    it('rejects non-numeric characters', () => {
      expect(validateEcuadorianRuc('110460982900A').errorMessage).toBe(ERROR_RUC_LENGTH_OR_FORMAT)
      expect(validateEcuadorianRuc('110460-829001').errorMessage).toBe(ERROR_RUC_LENGTH_OR_FORMAT)
    })

    it('rejects invalid province', () => {
      expect(validateEcuadorianRuc('0004609829001').errorMessage).toBe(ERROR_RUC_INVALID_ALGORITHM)
      expect(validateEcuadorianRuc('2504609829001').errorMessage).toBe(ERROR_RUC_INVALID_ALGORITHM)
    })

    it('rejects invalid verifier check digit', () => {
      expect(validateEcuadorianRuc('1104609828001').errorMessage).toBe(ERROR_RUC_INVALID_ALGORITHM)
    })

    it('rejects establishment 000', () => {
      expect(validateEcuadorianRuc('1104609829000').errorMessage).toBe(ERROR_RUC_INVALID_ALGORITHM)
    })
  })

  describe('validateCooperativaName', () => {
    it('accepts valid names with letters, numbers, spaces, hyphens, and apostrophes', () => {
      expect(validateCooperativaName('Cooperativa Loja').isValid).toBe(true)
      expect(validateCooperativaName('Coop. 24 de Mayo').isValid).toBe(false) // period is not in allowed chars
      expect(validateCooperativaName('Coop 24 de Mayo').isValid).toBe(true)
      expect(validateCooperativaName("Trans-Loja O'Higgins").isValid).toBe(true)
    })

    it('rejects empty or whitespace', () => {
      expect(validateCooperativaName('').errorMessage).toBe(ERROR_COOP_NAME_EMPTY)
      expect(validateCooperativaName('   ').errorMessage).toBe(ERROR_COOP_NAME_EMPTY)
    })

    it('rejects forbidden characters like @, #, $, _', () => {
      expect(validateCooperativaName('Coop @ Loja').errorMessage).toBe(ERROR_COOP_NAME_INVALID_CHARS)
      expect(validateCooperativaName('Trans_Loja').errorMessage).toBe(ERROR_COOP_NAME_INVALID_CHARS)
    })

    it('enforces 100 characters max', () => {
      expect(validateCooperativaName('A'.repeat(100)).isValid).toBe(true)
      expect(validateCooperativaName('A'.repeat(101)).errorMessage).toBe(ERROR_COOP_NAME_TOO_LONG)
    })
  })
})

