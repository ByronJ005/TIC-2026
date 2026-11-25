import { ref } from 'vue'

const SAVE_ERROR = 'No se pudo guardar la ruta. Inténtelo nuevamente.'
const CONNECTION_ERROR = 'No se pudo conectar con el servidor. Verifica tu conexión.'

function getSubmissionError(error: unknown): string {
  if (typeof error !== 'object' || error === null || !('status' in error)) return SAVE_ERROR
  if (error.status === 0) return CONNECTION_ERROR
  if (
    typeof error.status === 'number' && error.status >= 400 && error.status < 500 &&
    'message' in error && typeof error.message === 'string' && error.message.trim()
  ) {
    return error.message
  }
  return SAVE_ERROR
}

export function useRouteSubmission() {
  const isSubmitting = ref(false)
  const submitError = ref('')

  function clearSubmitError() {
    submitError.value = ''
  }

  async function submitRoute(save: () => Promise<unknown>): Promise<boolean> {
    if (isSubmitting.value) return false
    clearSubmitError()
    isSubmitting.value = true
    try {
      await save()
      return true
    } catch (error: unknown) {
      submitError.value = getSubmissionError(error)
      return false
    } finally {
      isSubmitting.value = false
    }
  }

  return { isSubmitting, submitError, clearSubmitError, submitRoute }
}
