import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  CooperativasService,
  type Cooperativa,
  type CooperativaCreatePayload,
  type CooperativaPaginationResponse,
  type CooperativaUpdatePayload,
} from '@/services/cooperativas.service'

export type CooperativaViewMode = 'table' | 'cards'

export const useCooperativasStore = defineStore('cooperativas', () => {
  const cooperativas = ref<Cooperativa[]>([])
  const total = ref(0)
  const page = ref(1)
  const size = ref(12) // good for 3 or 4 cards per row
  const totalPages = ref(0)
  const searchQuery = ref('')
  const statusFilter = ref<boolean | undefined>(undefined)
  const viewMode = ref<CooperativaViewMode>('cards')
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const successMessage = ref<string | null>(null)

  let debounceTimer: ReturnType<typeof setTimeout> | null = null

  function toggleViewMode() {
    viewMode.value = viewMode.value === 'cards' ? 'table' : 'cards'
  }

  function setViewMode(mode: CooperativaViewMode) {
    viewMode.value = mode
  }

  function clearMessages() {
    error.value = null
    successMessage.value = null
  }

  async function fetchCooperativas(): Promise<CooperativaPaginationResponse | null> {
    isLoading.value = true
    error.value = null
    try {
      const response = await CooperativasService.getCooperativas({
        page: page.value,
        size: size.value,
        search: searchQuery.value,
        is_active: statusFilter.value,
      })
      cooperativas.value = response.items
      total.value = response.total
      totalPages.value = response.total_pages
      page.value = response.page
      return response
    } catch (err: unknown) {
      const apiErr = err as { message?: string }
      error.value = apiErr.message || 'Error al cargar las cooperativas'
      cooperativas.value = []
      total.value = 0
      totalPages.value = 0
      return null
    } finally {
      isLoading.value = false
    }
  }

  function onSearchInput(query: string, delay = 300) {
    searchQuery.value = query
    page.value = 1
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }
    debounceTimer = setTimeout(() => {
      fetchCooperativas()
    }, delay)
  }

  async function createCooperativa(data: CooperativaCreatePayload): Promise<Cooperativa | null> {
    isLoading.value = true
    clearMessages()
    try {
      const created = await CooperativasService.createCooperativa(data)
      successMessage.value = 'Cooperativa registrada exitosamente'
      await fetchCooperativas()
      return created
    } catch (err: unknown) {
      const apiErr = err as { message?: string }
      error.value = apiErr.message || 'Error al registrar la cooperativa'
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function updateCooperativa(
    id: number,
    data: CooperativaUpdatePayload,
  ): Promise<Cooperativa | null> {
    isLoading.value = true
    clearMessages()
    try {
      const updated = await CooperativasService.updateCooperativa(id, data)
      successMessage.value = 'Cooperativa actualizada exitosamente'
      await fetchCooperativas()
      return updated
    } catch (err: unknown) {
      const apiErr = err as { message?: string }
      error.value = apiErr.message || 'Error al actualizar la cooperativa'
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function updateEstado(id: number, isActive: boolean): Promise<Cooperativa | null> {
    isLoading.value = true
    clearMessages()
    try {
      const updated = await CooperativasService.updateEstado(id, isActive)
      successMessage.value = isActive
        ? 'Cooperativa activada exitosamente'
        : 'Cooperativa desactivada exitosamente'
      await fetchCooperativas()
      return updated
    } catch (err: unknown) {
      const apiErr = err as { message?: string }
      error.value = apiErr.message || 'Error al cambiar el estado de la cooperativa'
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function uploadLogo(id: number, file: File): Promise<Cooperativa | null> {
    isLoading.value = true
    clearMessages()
    try {
      const updated = await CooperativasService.uploadLogo(id, file)
      successMessage.value = 'Logo actualizado exitosamente'
      await fetchCooperativas()
      return updated
    } catch (err: unknown) {
      const apiErr = err as { message?: string }
      error.value = apiErr.message || 'Error al subir el logo'
      return null
    } finally {
      isLoading.value = false
    }
  }

  return {
    cooperativas,
    total,
    page,
    size,
    totalPages,
    searchQuery,
    statusFilter,
    viewMode,
    isLoading,
    error,
    successMessage,
    toggleViewMode,
    setViewMode,
    clearMessages,
    fetchCooperativas,
    onSearchInput,
    createCooperativa,
    updateCooperativa,
    updateEstado,
    uploadLogo,
  }
})

