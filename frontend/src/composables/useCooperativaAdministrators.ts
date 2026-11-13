import { ref } from 'vue'
import {
  CooperativasService,
  type AdministradorSummary,
  type EligibleAdmin,
} from '@/services/cooperativas.service'

export function useCooperativaAdministrators() {
  const currentAdmins = ref<AdministradorSummary[]>([])
  const eligibleUsers = ref<EligibleAdmin[]>([])
  const selectedUserIds = ref<number[]>([])
  const searchQuery = ref('')
  const isLoading = ref(false)
  const isSaving = ref(false)
  const error = ref<string | null>(null)
  const successMessage = ref<string | null>(null)

  let debounceTimer: ReturnType<typeof setTimeout> | null = null

  async function loadAdministrators(cooperativaId: number) {
    isLoading.value = true
    error.value = null
    try {
      currentAdmins.value = await CooperativasService.getAdministradores(cooperativaId)
      selectedUserIds.value = currentAdmins.value.map((a) => a.id)
    } catch (err: unknown) {
      const apiErr = err as { message?: string }
      error.value = apiErr.message || 'Error al cargar los administradores'
    } finally {
      isLoading.value = false
    }
  }

  async function loadEligibleUsers(cooperativaId: number, query = '') {
    isLoading.value = true
    error.value = null
    try {
      eligibleUsers.value = await CooperativasService.getEligibleAdministrators(
        cooperativaId,
        query,
      )
    } catch (err: unknown) {
      const apiErr = err as { message?: string }
      error.value = apiErr.message || 'Error al cargar usuarios elegibles'
    } finally {
      isLoading.value = false
    }
  }

  function onSearchEligibleInput(cooperativaId: number, query: string, delay = 300) {
    searchQuery.value = query
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }
    debounceTimer = setTimeout(() => {
      loadEligibleUsers(cooperativaId, query)
    }, delay)
  }

  function toggleUserSelection(userId: number) {
    const index = selectedUserIds.value.indexOf(userId)
    if (index > -1) {
      selectedUserIds.value.splice(index, 1)
    } else {
      if (selectedUserIds.value.length < 3) {
        selectedUserIds.value.push(userId)
      }
    }
  }

  function isSelectionDisabled(userId: number): boolean {
    const isSelected = selectedUserIds.value.includes(userId)
    if (isSelected) {
      return false
    }
    return selectedUserIds.value.length >= 3
  }

  async function saveAdministrators(cooperativaId: number): Promise<boolean> {
    isSaving.value = true
    error.value = null
    successMessage.value = null
    try {
      currentAdmins.value = await CooperativasService.updateAdministradores(
        cooperativaId,
        selectedUserIds.value,
      )
      successMessage.value = 'Administradores asignados exitosamente'
      return true
    } catch (err: unknown) {
      const apiErr = err as { message?: string }
      error.value = apiErr.message || 'Error al actualizar administradores'
      return false
    } finally {
      isSaving.value = false
    }
  }

  async function removeAdministrator(cooperativaId: number, userId: number): Promise<boolean> {
    isSaving.value = true
    error.value = null
    successMessage.value = null
    try {
      const newIds = currentAdmins.value.filter((a) => a.id !== userId).map((a) => a.id)
      currentAdmins.value = await CooperativasService.updateAdministradores(
        cooperativaId,
        newIds,
      )
      selectedUserIds.value = newIds
      successMessage.value = 'Administrador desvinculado exitosamente'
      return true
    } catch (err: unknown) {
      const apiErr = err as { message?: string }
      error.value = apiErr.message || 'Error al desvincular el administrador'
      return false
    } finally {
      isSaving.value = false
    }
  }

  return {
    currentAdmins,
    eligibleUsers,
    selectedUserIds,
    searchQuery,
    isLoading,
    isSaving,
    error,
    successMessage,
    loadAdministrators,
    loadEligibleUsers,
    onSearchEligibleInput,
    toggleUserSelection,
    isSelectionDisabled,
    saveAdministrators,
    removeAdministrator,
  }
}

