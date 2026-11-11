import { ref } from 'vue'
import {
  ERROR_PASSWORD_CONFIRMATION_MISMATCH,
  normalizeEmail,
  validatePassword,
  validateRecoveryEmail,
} from '@/composables/useFormValidation'
import type { ApiError } from '@/services/api-client'
import { PasswordRecoveryService } from '@/services/password-recovery.service'

export const INVALID_RESET_LINK_MESSAGE = 'El enlace de restablecimiento es inválido o ha expirado'
const GENERIC_ERROR = 'No se pudo procesar la solicitud. Intenta nuevamente.'
const INVALID_LINK_STATUS = 400

export function useForgotPasswordForm() {
  const email = ref('')
  const emailError = ref('')
  const generalError = ref('')
  const successMessage = ref('')
  const isLoading = ref(false)

  async function submit(): Promise<boolean> {
    emailError.value = ''
    generalError.value = ''
    successMessage.value = ''

    const emailResult = validateRecoveryEmail(email.value)
    if (!emailResult.isValid) {
      emailError.value = emailResult.errorMessage
      return false
    }

    isLoading.value = true
    try {
      const response = await PasswordRecoveryService.forgotPassword(normalizeEmail(email.value))
      successMessage.value = response.message
      return true
    } catch (err: unknown) {
      generalError.value = (err as ApiError).message || GENERIC_ERROR
      return false
    } finally {
      isLoading.value = false
    }
  }

  return { email, emailError, generalError, successMessage, isLoading, submit }
}

export function useResetPasswordForm(token: string) {
  const newPassword = ref('')
  const confirmPassword = ref('')
  const newPasswordError = ref('')
  const confirmPasswordError = ref('')
  const generalError = ref('')
  const successMessage = ref('')
  const isLoading = ref(false)
  // A missing token can never work, so the invalid-link state starts immediately
  const linkIsInvalid = ref(!token || !token.trim())

  function validateForm(): boolean {
    newPasswordError.value = ''
    confirmPasswordError.value = ''

    const passwordResult = validatePassword(newPassword.value)
    if (!passwordResult.isValid) {
      newPasswordError.value = passwordResult.errorMessage
      return false
    }
    if (newPassword.value !== confirmPassword.value) {
      confirmPasswordError.value = ERROR_PASSWORD_CONFIRMATION_MISMATCH
      return false
    }
    return true
  }

  async function submit(): Promise<boolean> {
    generalError.value = ''
    successMessage.value = ''
    if (linkIsInvalid.value || !validateForm()) return false

    isLoading.value = true
    try {
      const response = await PasswordRecoveryService.resetPassword(token, newPassword.value)
      successMessage.value = response.message
      return true
    } catch (err: unknown) {
      const apiError = err as ApiError
      if (apiError.status === INVALID_LINK_STATUS) {
        linkIsInvalid.value = true
        generalError.value = apiError.message || INVALID_RESET_LINK_MESSAGE
      } else {
        generalError.value = apiError.message || GENERIC_ERROR
      }
      return false
    } finally {
      isLoading.value = false
    }
  }

  return {
    newPassword,
    confirmPassword,
    newPasswordError,
    confirmPasswordError,
    generalError,
    successMessage,
    isLoading,
    linkIsInvalid,
    submit,
  }
}

