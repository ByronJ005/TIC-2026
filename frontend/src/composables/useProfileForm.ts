import { computed, reactive, ref } from 'vue'
import {
  ERROR_CURRENT_PASSWORD_REQUIRED,
  ERROR_CURRENT_PASSWORD_WRONG,
  ERROR_MANDATORY_FIELDS_EMPTY,
  ERROR_NEW_PASSWORD_SAME_AS_CURRENT,
  ERROR_PASSWORD_CONFIRMATION_MISMATCH,
  ERROR_REQUIRED_FIELD,
  validateAddress,
  validateBirthDate,
  validateName,
  validatePassword,
  validatePhone,
} from '@/composables/useFormValidation'
import type { ApiError } from '@/services/api-client'
import type { User } from '@/services/auth.service'
import type { ProfileUpdateData } from '@/services/profile.service'
import { useProfileStore } from '@/stores/profile.store'

type ProfileFormValues = ProfileUpdateData
type ProfileFormErrors = Record<keyof ProfileFormValues, string>

const PERSONAL_FIELDS = ['first_name', 'last_name', 'phone', 'address', 'birth_date'] as const
const PASSWORD_FIELDS = ['current_password', 'new_password', 'confirm_password'] as const
const GENERIC_UPDATE_ERROR = 'No se pudo actualizar el perfil. Intenta nuevamente.'

function emptyValues(): ProfileFormValues {
  return {
    first_name: '',
    last_name: '',
    phone: '',
    address: '',
    birth_date: '',
    current_password: '',
    new_password: '',
    confirm_password: '',
  }
}

function isBlank(value: string): boolean {
  return !value.trim()
}

export function useProfileForm() {
  const profileStore = useProfileStore()

  const form = reactive<ProfileFormValues>(emptyValues())
  const errors = reactive<ProfileFormErrors>(emptyValues())
  const isSaving = computed(() => profileStore.isSaving)
  const generalError = ref('')
  const successMessage = ref('')
  let savedPersonalData: Pick<ProfileFormValues, (typeof PERSONAL_FIELDS)[number]> = {
    first_name: '',
    last_name: '',
    phone: '',
    address: '',
    birth_date: '',
  }

  function clearErrors() {
    Object.assign(errors, emptyValues())
    generalError.value = ''
    successMessage.value = ''
  }

  function clearPasswordFields() {
    PASSWORD_FIELDS.forEach((field) => {
      form[field] = ''
    })
  }

  function loadFromUser(user: User | null) {
    if (!user) return
    savedPersonalData = {
      first_name: user.first_name ?? '',
      last_name: user.last_name ?? '',
      phone: user.phone ?? '',
      address: user.address ?? '',
      birth_date: user.birth_date ?? '',
    }
    restoreSavedData()
  }

  /** Puts the last saved personal data back in the form (CP-42) and empties password fields. */
  function restoreSavedData() {
    Object.assign(form, savedPersonalData)
    clearPasswordFields()
  }

  function validateRequiredNames(): boolean {
    if (isBlank(form.first_name) || isBlank(form.last_name)) {
      generalError.value = ERROR_MANDATORY_FIELDS_EMPTY
      if (isBlank(form.first_name)) errors.first_name = ERROR_MANDATORY_FIELDS_EMPTY
      if (isBlank(form.last_name)) errors.last_name = ERROR_MANDATORY_FIELDS_EMPTY
      return false
    }
    return true
  }

  function validateOptionalFields(today: Date): boolean {
    const checks: Array<[keyof ProfileFormValues, { isValid: boolean; errorMessage: string }]> = [
      ['first_name', validateName(form.first_name)],
      ['last_name', validateName(form.last_name)],
      ['phone', validatePhone(form.phone)],
      ['address', validateAddress(form.address)],
      ['birth_date', validateBirthDate(form.birth_date, today)],
    ]
    let allFieldsAreValid = true
    for (const [field, result] of checks) {
      errors[field] = result.errorMessage
      if (!result.isValid) allFieldsAreValid = false
    }
    return allFieldsAreValid
  }

  /** Password fields are all-or-nothing: if any is filled, all of them are required. */
  function validatePasswordChange(): boolean {
    const anyPasswordFieldFilled = PASSWORD_FIELDS.some((field) => !isBlank(form[field]))
    if (!anyPasswordFieldFilled) return true

    let isValid = true
    if (isBlank(form.current_password)) {
      errors.current_password = ERROR_CURRENT_PASSWORD_REQUIRED
      isValid = false
    }
    if (isBlank(form.new_password)) {
      errors.new_password = ERROR_REQUIRED_FIELD
      isValid = false
    }
    if (isBlank(form.confirm_password)) {
      errors.confirm_password = ERROR_REQUIRED_FIELD
      isValid = false
    }
    if (!isValid) return false

    const newPasswordResult = validatePassword(form.new_password)
    if (!newPasswordResult.isValid) {
      errors.new_password = newPasswordResult.errorMessage
      return false
    }
    if (form.new_password !== form.confirm_password) {
      errors.confirm_password = ERROR_PASSWORD_CONFIRMATION_MISMATCH
      return false
    }
    if (form.new_password === form.current_password) {
      errors.new_password = ERROR_NEW_PASSWORD_SAME_AS_CURRENT
      return false
    }
    return true
  }

  function validate(today: Date = new Date()): boolean {
    clearErrors()
    if (!validateRequiredNames()) {
      restoreSavedData()
      return false
    }
    const personalDataIsValid = validateOptionalFields(today)
    const passwordChangeIsValid = validatePasswordChange()
    return personalDataIsValid && passwordChangeIsValid
  }

  function applyServerError(error: ApiError) {
    const message = error.message || GENERIC_UPDATE_ERROR
    if (message === ERROR_CURRENT_PASSWORD_WRONG) {
      errors.current_password = message
      return
    }
    if (message === ERROR_MANDATORY_FIELDS_EMPTY) {
      restoreSavedData()
    }
    generalError.value = message
  }

  async function submit(): Promise<boolean> {
    if (!validate()) return false

    try {
      const response = await profileStore.updateProfile({ ...form })
      loadFromUser(response.user)
      successMessage.value = response.message
      return true
    } catch (err: unknown) {
      applyServerError(err as ApiError)
      return false
    }
  }

  return {
    form,
    errors,
    generalError,
    successMessage,
    isSaving,
    loadFromUser,
    restoreSavedData,
    validate,
    submit,
  }
}
