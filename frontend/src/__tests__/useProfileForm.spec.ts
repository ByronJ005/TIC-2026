import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useProfileForm } from '@/composables/useProfileForm'
import {
  ERROR_ADDRESS_TOO_LONG,
  ERROR_CURRENT_PASSWORD_REQUIRED,
  ERROR_CURRENT_PASSWORD_WRONG,
  ERROR_INVALID_BIRTH_DATE,
  ERROR_INVALID_NAME,
  ERROR_INVALID_PASSWORD,
  ERROR_MANDATORY_FIELDS_EMPTY,
  ERROR_NEW_PASSWORD_SAME_AS_CURRENT,
  ERROR_PASSWORD_CONFIRMATION_MISMATCH,
  ERROR_PHONE_LENGTH,
  ERROR_PHONE_NOT_NUMERIC,
  ERROR_REQUIRED_FIELD,
} from '@/composables/useFormValidation'
import { ProfileService, type ProfileUpdateResponse } from '@/services/profile.service'
import type { User } from '@/services/auth.service'
import { AUTH_TOKEN_KEY } from '@/services/api-client'
import { useAuthStore } from '@/stores/auth.store'

const savedUser: User = {
  id: 1,
  document_type: 'CEDULA',
  document_number: '1710034065',
  first_name: 'Ana',
  last_name: 'Gomez',
  email: 'ana@example.com',
  roles: ['PASAJERO'],
  is_active: true,
  phone: '0991234567',
  address: 'Calle Falsa 123',
  birth_date: '1990-05-20',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

function setupForm() {
  const profileForm = useProfileForm()
  profileForm.loadFromUser(savedUser)
  return profileForm
}

function fillPasswords(
  form: ReturnType<typeof useProfileForm>['form'],
  values: { current?: string; next?: string; confirm?: string },
) {
  form.current_password = values.current ?? ''
  form.new_password = values.next ?? ''
  form.confirm_password = values.confirm ?? ''
}

describe('useProfileForm', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it('loads saved user data into the form with empty password fields', () => {
    const { form } = setupForm()

    expect(form.first_name).toBe('Ana')
    expect(form.phone).toBe('0991234567')
    expect(form.birth_date).toBe('1990-05-20')
    expect(form.current_password).toBe('')
  })

  it('loads null optional values as empty strings', () => {
    const { form, loadFromUser } = useProfileForm()

    loadFromUser({ ...savedUser, phone: null, address: null, birth_date: null })

    expect(form.phone).toBe('')
    expect(form.address).toBe('')
    expect(form.birth_date).toBe('')
  })

  it('accepts unchanged valid data', () => {
    const { validate } = setupForm()

    expect(validate()).toBe(true)
  })

  it.each(['first_name', 'last_name'] as const)(
    'CP-42: blank %s shows the mandatory message and restores previous data',
    (field) => {
      const { form, errors, generalError, validate } = setupForm()
      form[field] = '   '
      form.phone = '0987654321'

      expect(validate()).toBe(false)

      expect(generalError.value).toBe(ERROR_MANDATORY_FIELDS_EMPTY)
      expect(errors[field]).toBe(ERROR_MANDATORY_FIELDS_EMPTY)
      expect(form[field]).toBe(savedUser[field])
      expect(form.phone).toBe('0991234567')
    },
  )

  it('rejects names with numbers or more than 50 characters', () => {
    const { form, errors, validate } = setupForm()
    form.first_name = 'Ana1'
    form.last_name = 'a'.repeat(51)

    expect(validate()).toBe(false)
    expect(errors.first_name).toBe(ERROR_INVALID_NAME)
    expect(errors.last_name).toBe(ERROR_INVALID_NAME)
  })

  it('reports phone length and numeric errors', () => {
    const { form, errors, validate } = setupForm()

    form.phone = '123'
    expect(validate()).toBe(false)
    expect(errors.phone).toBe(ERROR_PHONE_LENGTH)

    form.phone = '099-123-456'
    expect(validate()).toBe(false)
    expect(errors.phone).toBe(ERROR_PHONE_NOT_NUMERIC)
  })

  it('reports address longer than 150 characters', () => {
    const { form, errors, validate } = setupForm()
    form.address = 'a'.repeat(151)

    expect(validate()).toBe(false)
    expect(errors.address).toBe(ERROR_ADDRESS_TOO_LONG)
  })

  it('rejects future and too old birth dates using the given reference day', () => {
    const { form, errors, validate } = setupForm()
    const today = new Date(2026, 10, 10)

    form.birth_date = '2026-11-11'
    expect(validate(today)).toBe(false)
    expect(errors.birth_date).toBe(ERROR_INVALID_BIRTH_DATE)

    form.birth_date = '1899-12-31'
    expect(validate(today)).toBe(false)

    form.birth_date = '2026-11-10'
    expect(validate(today)).toBe(true)
  })

  it('accepts clearing optional fields', () => {
    const { form, validate } = setupForm()
    form.phone = ''
    form.address = ''
    form.birth_date = ''

    expect(validate()).toBe(true)
  })

  describe('password fields are all-or-nothing', () => {
    it('does not require anything when all three are blank or spaces', () => {
      const { form, validate } = setupForm()
      fillPasswords(form, { current: '  ', next: '', confirm: ' ' })

      expect(validate()).toBe(true)
    })

    it('requires the current password when only new or confirmation is filled', () => {
      const { form, errors, validate } = setupForm()
      fillPasswords(form, { next: 'NewPass456' })

      expect(validate()).toBe(false)
      expect(errors.current_password).toBe(ERROR_CURRENT_PASSWORD_REQUIRED)
      expect(errors.confirm_password).toBe(ERROR_REQUIRED_FIELD)
    })

    it('requires new password and confirmation when only the current one is filled', () => {
      const { form, errors, validate } = setupForm()
      fillPasswords(form, { current: 'OldPass123' })

      expect(validate()).toBe(false)
      expect(errors.new_password).toBe(ERROR_REQUIRED_FIELD)
      expect(errors.confirm_password).toBe(ERROR_REQUIRED_FIELD)
    })

    it('rejects a new password with invalid format', () => {
      const { form, errors, validate } = setupForm()
      fillPasswords(form, { current: 'OldPass123', next: 'corta1A', confirm: 'corta1A' })

      expect(validate()).toBe(false)
      expect(errors.new_password).toBe(ERROR_INVALID_PASSWORD)
    })

    it('rejects a confirmation that does not match', () => {
      const { form, errors, validate } = setupForm()
      fillPasswords(form, { current: 'OldPass123', next: 'NewPass456', confirm: 'NewPass457' })

      expect(validate()).toBe(false)
      expect(errors.confirm_password).toBe(ERROR_PASSWORD_CONFIRMATION_MISMATCH)
    })

    it('rejects a new password equal to the current one', () => {
      const { form, errors, validate } = setupForm()
      fillPasswords(form, { current: 'OldPass123', next: 'OldPass123', confirm: 'OldPass123' })

      expect(validate()).toBe(false)
      expect(errors.new_password).toBe(ERROR_NEW_PASSWORD_SAME_AS_CURRENT)
    })

    it('accepts a complete valid password change', () => {
      const { form, validate } = setupForm()
      fillPasswords(form, { current: 'OldPass123', next: 'NewPass456', confirm: 'NewPass456' })

      expect(validate()).toBe(true)
    })
  })

  describe('submit', () => {
    function mockUpdate(overrides: Partial<ProfileUpdateResponse> = {}) {
      const response: ProfileUpdateResponse = {
        user: { ...savedUser, first_name: 'Anita' },
        message: 'Perfil actualizado exitosamente',
        access_token: null,
        token_type: null,
        ...overrides,
      }
      return vi.spyOn(ProfileService, 'updateProfile').mockResolvedValue(response)
    }

    it('does not call the API when the form is invalid', async () => {
      const spy = mockUpdate()
      const { form, submit } = setupForm()
      form.phone = '123'

      expect(await submit()).toBe(false)
      expect(spy).not.toHaveBeenCalled()
    })

    it('CP-37: shows the success message and reloads saved data', async () => {
      mockUpdate()
      const { form, successMessage, submit } = setupForm()
      form.first_name = 'Anita'

      expect(await submit()).toBe(true)
      expect(successMessage.value).toBe('Perfil actualizado exitosamente')
      expect(form.first_name).toBe('Anita')
      expect(useAuthStore().user?.first_name).toBe('Anita')
    })

    it('clears password fields after a password change and replaces the session token', async () => {
      mockUpdate({
        message: 'Contraseña actualizada exitosamente',
        access_token: 'fresh-token',
        token_type: 'bearer',
      })
      const { form, successMessage, submit } = setupForm()
      fillPasswords(form, { current: 'OldPass123', next: 'NewPass456', confirm: 'NewPass456' })

      expect(await submit()).toBe(true)
      expect(successMessage.value).toBe('Contraseña actualizada exitosamente')
      expect(form.current_password).toBe('')
      expect(form.new_password).toBe('')
      expect(localStorage.getItem(AUTH_TOKEN_KEY)).toBe('fresh-token')
    })

    it('keeps the original token when the password did not change', async () => {
      mockUpdate()
      useAuthStore().setToken('original-token')
      const { submit } = setupForm()

      await submit()

      expect(localStorage.getItem(AUTH_TOKEN_KEY)).toBe('original-token')
    })

    it('shows a wrong current password error on that field only', async () => {
      vi.spyOn(ProfileService, 'updateProfile').mockRejectedValue({
        status: 400,
        message: ERROR_CURRENT_PASSWORD_WRONG,
      })
      const { form, errors, generalError, successMessage, submit } = setupForm()
      fillPasswords(form, { current: 'Wrong12345', next: 'NewPass456', confirm: 'NewPass456' })

      expect(await submit()).toBe(false)
      expect(errors.current_password).toBe(ERROR_CURRENT_PASSWORD_WRONG)
      expect(generalError.value).toBe('')
      expect(successMessage.value).toBe('')
      expect(form.new_password).toBe('NewPass456')
    })

    it('restores data when the server reports empty mandatory fields', async () => {
      vi.spyOn(ProfileService, 'updateProfile').mockRejectedValue({
        status: 422,
        message: ERROR_MANDATORY_FIELDS_EMPTY,
      })
      const { form, generalError, submit } = setupForm()
      form.first_name = 'Ana María'

      await submit()

      expect(generalError.value).toBe(ERROR_MANDATORY_FIELDS_EMPTY)
      expect(form.first_name).toBe('Ana')
    })

    it('shows a generic message when the server error has no message', async () => {
      vi.spyOn(ProfileService, 'updateProfile').mockRejectedValue({ status: 500, message: '' })
      const { generalError, submit } = setupForm()

      expect(await submit()).toBe(false)
      expect(generalError.value).not.toBe('')
    })

    it('clears the previous success message when validating again', async () => {
      mockUpdate()
      const { form, successMessage, submit } = setupForm()
      await submit()
      expect(successMessage.value).not.toBe('')

      form.phone = '123'
      await submit()

      expect(successMessage.value).toBe('')
    })
  })
})

