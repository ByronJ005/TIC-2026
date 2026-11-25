import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  type CooperativaGeneralRoute,
  type CooperativaRoutesGroup,
  type Route,
  type RouteCreatePayload,
  type RouteDetail,
  type RouteFilters,
  type RouteUpdatePayload,
  adoptGeneralRoutes as adoptGeneralRoutesApi,
  createGeneralRoute as createGeneralRouteApi,
  createSpecificRoute as createSpecificRouteApi,
  getAdoptedGeneralRoutes as getAdoptedGeneralRoutesApi,
  getAvailableGeneralRoutes as getAvailableGeneralRoutesApi,
  getGeneralRoutes as getGeneralRoutesApi,
  getRouteDetail as getRouteDetailApi,
  getSpecificRoutes as getSpecificRoutesApi,
  getSpecificRoutesSupervision as getSpecificRoutesSupervisionApi,
  updateAdoptionEstado as updateAdoptionEstadoApi,
  updateGeneralRoute as updateGeneralRouteApi,
  updateGeneralRouteEstado as updateGeneralRouteEstadoApi,
  updateSpecificRoute as updateSpecificRouteApi,
  updateSpecificRouteEstado as updateSpecificRouteEstadoApi,
} from '@/services/rutas.service'

export const useRutasStore = defineStore('rutas', () => {
  const generalRoutes = ref<Route[]>([])
  const generalRoutesTotal = ref(0)
  const generalRoutesPage = ref(1)
  const generalRoutesSize = ref(10)
  const generalRoutesTotalPages = ref(1)

  const specificRoutesGroups = ref<CooperativaRoutesGroup[]>([])
  const adoptedRoutes = ref<CooperativaGeneralRoute[]>([])
  const specificRoutes = ref<Route[]>([])
  const availableGeneralRoutes = ref<Route[]>([])
  const isCooperativeInactive = ref(false)

  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const feedbackMessage = ref<string | null>(null)

  function clearFeedback() {
    feedbackMessage.value = null
  }

  // ---------------- Shared ----------------
  async function fetchRouteDetail(routeId: number): Promise<RouteDetail | null> {
    try {
      return await getRouteDetailApi(routeId)
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Error al obtener detalle de la ruta'
      return null
    }
  }

  // ---------------- ADMIN_GENERAL Actions ----------------
  async function fetchGeneralRoutes(filters: RouteFilters = {}) {
    isLoading.value = true
    error.value = null
    try {
      const res = await getGeneralRoutesApi(filters)
      generalRoutes.value = res.items
      generalRoutesTotal.value = res.total
      generalRoutesPage.value = res.page
      generalRoutesSize.value = res.size
      generalRoutesTotalPages.value = res.total_pages
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Error al cargar las rutas generales'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchSpecificRoutesSupervision() {
    try {
      specificRoutesGroups.value = await getSpecificRoutesSupervisionApi()
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Error al cargar rutas de cooperativas'
    }
  }

  async function createGeneralRoute(data: RouteCreatePayload): Promise<RouteDetail> {
    const res = await createGeneralRouteApi(data)
    feedbackMessage.value = `Ruta "${res.name}" creada exitosamente`
    return res
  }

  async function updateGeneralRoute(routeId: number, data: RouteUpdatePayload): Promise<RouteDetail> {
    const res = await updateGeneralRouteApi(routeId, data)
    feedbackMessage.value = `Ruta "${res.name}" actualizada exitosamente`
    return res
  }

  async function toggleGeneralRouteEstado(
    routeId: number,
    isActive: boolean,
    confirm: boolean = false,
  ): Promise<RouteDetail> {
    const res = await updateGeneralRouteEstadoApi(routeId, isActive, confirm)
    feedbackMessage.value = `Estado de ruta "${res.name}" actualizado a ${isActive ? 'Activa' : 'Inactiva'}`
    await fetchGeneralRoutes({ page: generalRoutesPage.value, size: generalRoutesSize.value })
    return res
  }

  function isCooperativeInactiveError(err: unknown): boolean {
    if (typeof err === 'object' && err !== null) {
      const apiErr = err as {
        status?: number
        message?: string
        detail?: { code?: string; message?: string } | string
      }
      if (apiErr.status === 403) {
        if (typeof apiErr.detail === 'object' && apiErr.detail !== null && 'code' in apiErr.detail) {
          if (apiErr.detail.code === 'COOPERATIVA_ASIGNADA_INACTIVA') return true
        }
        const msg = typeof apiErr.detail === 'string'
          ? apiErr.detail
          : (apiErr.detail as { message?: string })?.message || apiErr.message || ''
        if (
          msg.includes('desactivada') ||
          msg.includes('inactiva') ||
          msg.includes('no tiene una cooperativa asignada')
        ) {
          return true
        }
      }
    }
    return false
  }

  // ---------------- ADMIN_COOPERATIVA Actions ----------------
  async function fetchCoopAdoptedRoutes() {
    isLoading.value = true
    error.value = null
    try {
      adoptedRoutes.value = await getAdoptedGeneralRoutesApi()
      isCooperativeInactive.value = false
    } catch (err: unknown) {
      if (isCooperativeInactiveError(err)) {
        isCooperativeInactive.value = true
        error.value = null
        return
      }
      error.value = err instanceof Error ? err.message : 'Error al cargar rutas adoptadas'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCoopSpecificRoutes() {
    isLoading.value = true
    error.value = null
    try {
      specificRoutes.value = await getSpecificRoutesApi()
      isCooperativeInactive.value = false
    } catch (err: unknown) {
      if (isCooperativeInactiveError(err)) {
        isCooperativeInactive.value = true
        error.value = null
        return
      }
      error.value = err instanceof Error ? err.message : 'Error al cargar rutas de su cooperativa'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchAvailableGeneralRoutes() {
    isLoading.value = true
    error.value = null
    try {
      availableGeneralRoutes.value = await getAvailableGeneralRoutesApi()
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Error al cargar rutas disponibles'
    } finally {
      isLoading.value = false
    }
  }

  async function adoptRoutes(routeIds: number[]) {
    const adopted = await adoptGeneralRoutesApi(routeIds)
    feedbackMessage.value = `Se adoptaron ${adopted.length} ruta(s) general(es)`
    await fetchCoopAdoptedRoutes()
    return adopted.length
  }

  async function toggleAdoptionEstado(adoptionId: number, isActive: boolean, confirm: boolean = false) {
    await updateAdoptionEstadoApi(adoptionId, isActive, confirm)
    feedbackMessage.value = `Operación de ruta adoptada actualizada a ${isActive ? 'Activa' : 'Inactiva'}`
    await fetchCoopAdoptedRoutes()
  }

  async function createSpecificRoute(data: RouteCreatePayload): Promise<RouteDetail> {
    const res = await createSpecificRouteApi(data)
    feedbackMessage.value = `Ruta propia "${res.name}" creada exitosamente`
    return res
  }

  async function updateSpecificRoute(routeId: number, data: RouteUpdatePayload): Promise<RouteDetail> {
    const res = await updateSpecificRouteApi(routeId, data)
    feedbackMessage.value = `Ruta propia "${res.name}" actualizada exitosamente`
    return res
  }

  async function toggleSpecificRouteEstado(routeId: number, isActive: boolean, confirm: boolean = false) {
    const res = await updateSpecificRouteEstadoApi(routeId, isActive, confirm)
    feedbackMessage.value = `Estado de ruta "${res.name}" actualizado a ${isActive ? 'Activa' : 'Inactiva'}`
    await fetchCoopSpecificRoutes()
  }

  return {
    generalRoutes,
    generalRoutesTotal,
    generalRoutesPage,
    generalRoutesSize,
    generalRoutesTotalPages,
    specificRoutesGroups,
    adoptedRoutes,
    specificRoutes,
    availableGeneralRoutes,
    isCooperativeInactive,
    isLoading,
    error,
    feedbackMessage,
    clearFeedback,
    fetchRouteDetail,
    fetchGeneralRoutes,
    fetchSpecificRoutesSupervision,
    createGeneralRoute,
    updateGeneralRoute,
    toggleGeneralRouteEstado,
    fetchCoopAdoptedRoutes,
    fetchCoopSpecificRoutes,
    fetchAvailableGeneralRoutes,
    adoptRoutes,
    toggleAdoptionEstado,
    createSpecificRoute,
    updateSpecificRoute,
    toggleSpecificRouteEstado,
  }
})
