import { ref } from 'vue'
import { useRutasStore } from '@/stores/rutas.store'
import type { RouteFilters } from '@/services/rutas.service'

export function useRoutes() {
  const store = useRutasStore()

  const originFilter = ref<number | undefined>(undefined)
  const destinationFilter = ref<number | undefined>(undefined)
  const activeFilter = ref<boolean | undefined>(undefined)

  function applyFilters(page: number = 1) {
    const filters: RouteFilters = {
      origin_id: originFilter.value,
      destination_id: destinationFilter.value,
      is_active: activeFilter.value,
      page,
      size: store.generalRoutesSize,
    }
    return store.fetchGeneralRoutes(filters)
  }

  function resetFilters() {
    originFilter.value = undefined
    destinationFilter.value = undefined
    activeFilter.value = undefined
    return applyFilters(1)
  }

  return {
    store,
    originFilter,
    destinationFilter,
    activeFilter,
    applyFilters,
    resetFilters,
  }
}
