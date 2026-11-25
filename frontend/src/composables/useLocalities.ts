import { computed, ref } from 'vue'
import {
  type Locality,
  createLocality as createLocalityApi,
  getLocalidades as getLocalidadesApi,
} from '@/services/localidades.service'

export function useLocalities() {
  const localities = ref<Locality[]>([])
  const searchQuery = ref('')
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  let debounceTimer: ReturnType<typeof setTimeout> | null = null

  async function fetchLocalities(query: string = '') {
    isLoading.value = true
    error.value = null
    try {
      const res = await getLocalidadesApi(query)
      localities.value = res.items
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Error al cargar localidades'
    } finally {
      isLoading.value = false
    }
  }

  function handleSearchDebounced(query: string) {
    searchQuery.value = query
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      fetchLocalities(query)
    }, 250)
  }

  const normalizedQuery = computed(() => {
    return searchQuery.value.trim().replace(/\s+/g, ' ').toLowerCase()
  })

  // Detects if the typed search already has an exact match in the catalogue
  const exactMatch = computed<Locality | null>(() => {
    if (!normalizedQuery.value) return null
    return (
      localities.value.find(
        (loc) => loc.name.trim().replace(/\s+/g, ' ').toLowerCase() === normalizedQuery.value,
      ) || null
    )
  })

  async function createNewLocality(name: string): Promise<Locality> {
    const trimmed = name.trim().replace(/\s+/g, ' ')
    const created = await createLocalityApi({ name: trimmed })
    await fetchLocalities('')
    return created
  }

  return {
    localities,
    searchQuery,
    isLoading,
    error,
    exactMatch,
    fetchLocalities,
    handleSearchDebounced,
    createNewLocality,
  }
}
