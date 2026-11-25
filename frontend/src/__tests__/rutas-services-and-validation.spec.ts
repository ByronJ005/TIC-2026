import { describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import {
  setCooperativaInactivaHandler,
  setRecursoAjenoHandler,
  apiClient,
} from '@/services/api-client'
import * as routesApi from '@/services/rutas.service'
import { useRutasStore } from '@/stores/rutas.store'
import {
  validateLocalityName,
  validateRouteDescription,
  validateRouteDistance,
  validateRouteNameSuffix,
  validateRouteOriginAndDestination,
  validateRouteStops,
  validateRouteTime,
  ERROR_DISTANCE_REQUIRED,
  ERROR_LOCALITY_NAME_EMPTY,
  ERROR_LOCALITY_NAME_TOO_LONG,
  ERROR_ORIGIN_REQUIRED,
  ERROR_ROUTE_DESCRIPTION_TOO_LONG,
  ERROR_ROUTE_DISTANCE_INVALID,
  ERROR_ROUTE_NAME_SUFFIX_TOO_LONG,
  ERROR_ROUTE_ORIGIN_DESTINATION_SAME,
  ERROR_ROUTE_STOP_DUPLICATED,
  ERROR_ROUTE_STOP_EQUALS_ORIGIN_OR_DESTINATION,
  ERROR_ROUTE_STOPS_EMPTY,
  ERROR_ROUTE_TIME_INVALID,
  ERROR_TIME_REQUIRED,
} from '@/composables/useFormValidation'
import { useRouteForm } from '@/composables/useRouteForm'

describe('Route Form Validation (useFormValidation)', () => {
  it('validates locality name', () => {
    expect(validateLocalityName('Loja').isValid).toBe(true)
    expect(validateLocalityName('   ').errorMessage).toBe(ERROR_LOCALITY_NAME_EMPTY)
    expect(validateLocalityName('A'.repeat(101)).errorMessage).toBe(ERROR_LOCALITY_NAME_TOO_LONG)
  })

  it('validates origin and destination', () => {
    expect(validateRouteOriginAndDestination(1, 2).isValid).toBe(true)
    expect(validateRouteOriginAndDestination(null, 2).errorMessage).toBe(ERROR_ORIGIN_REQUIRED)
    expect(validateRouteOriginAndDestination(1, 1).errorMessage).toBe(ERROR_ROUTE_ORIGIN_DESTINATION_SAME)
  })

  it('validates route distance', () => {
    expect(validateRouteDistance(100.5).isValid).toBe(true)
    expect(validateRouteDistance('250.75').isValid).toBe(true)
    expect(validateRouteDistance('').errorMessage).toBe(ERROR_DISTANCE_REQUIRED)
    expect(validateRouteDistance(0).errorMessage).toBe(ERROR_ROUTE_DISTANCE_INVALID)
    expect(validateRouteDistance(-10).errorMessage).toBe(ERROR_ROUTE_DISTANCE_INVALID)
    expect(validateRouteDistance('abc').errorMessage).toBe(ERROR_ROUTE_DISTANCE_INVALID)
  })

  it('validates route time (hours & minutes)', () => {
    expect(validateRouteTime(2, 30).isValid).toBe(true)
    expect(validateRouteTime('', '').errorMessage).toBe(ERROR_TIME_REQUIRED)
    expect(validateRouteTime(0, 0).errorMessage).toBe(ERROR_ROUTE_TIME_INVALID)
    expect(validateRouteTime(24, 0).isValid).toBe(true)
    expect(validateRouteTime(99, 59).isValid).toBe(true)
    expect(validateRouteTime(100, 0).errorMessage).toBe(ERROR_ROUTE_TIME_INVALID)
    expect(validateRouteTime(2, 60).errorMessage).toBe(ERROR_ROUTE_TIME_INVALID)
  })

  it('validates suffix and description lengths', () => {
    expect(validateRouteNameSuffix('Vía Cuenca').isValid).toBe(true)
    expect(validateRouteNameSuffix('A'.repeat(31)).errorMessage).toBe(ERROR_ROUTE_NAME_SUFFIX_TOO_LONG)

    expect(validateRouteDescription('Ruta directa').isValid).toBe(true)
    expect(validateRouteDescription('A'.repeat(101)).errorMessage).toBe(ERROR_ROUTE_DESCRIPTION_TOO_LONG)
  })

  it('validates route stops', () => {
    // Only origin and dest -> valid even with empty stops
    expect(validateRouteStops(1, 2, true, []).isValid).toBe(true)

    // Intermediate stops enabled but empty -> error
    expect(validateRouteStops(1, 2, false, []).errorMessage).toBe(ERROR_ROUTE_STOPS_EMPTY)

    // Stop equals origin or destination -> error
    expect(
      validateRouteStops(1, 2, false, [{ locality_id: 1, stop_order: 1 }]).errorMessage,
    ).toBe(ERROR_ROUTE_STOP_EQUALS_ORIGIN_OR_DESTINATION)

    // Duplicate stop -> error
    expect(
      validateRouteStops(1, 2, false, [
        { locality_id: 3, stop_order: 1 },
        { locality_id: 3, stop_order: 2 },
      ]).errorMessage,
    ).toBe(ERROR_ROUTE_STOP_DUPLICATED)

    // Distinct stops -> valid
    expect(
      validateRouteStops(1, 2, false, [
        { locality_id: 3, stop_order: 1 },
        { locality_id: 4, stop_order: 2 },
      ]).isValid,
    ).toBe(true)
  })
})

describe('Route Form Composable (useRouteForm)', () => {
  it('computes route names, adds and removes stops', () => {
    const form = useRouteForm()
    form.originName.value = 'Loja'
    form.destinationName.value = 'Quito'
    expect(form.computedPrefix.value).toBe('Loja - Quito')
    expect(form.computedFullName.value).toBe('Loja - Quito')

    form.nameSuffix.value = 'Expreso'
    expect(form.computedFullName.value).toBe('Loja - Quito Expreso')

    form.addStop(5, 'Cuenca')
    form.addStop(6, 'Riobamba')
    expect(form.stops.value.length).toBe(2)
    expect(form.stops.value.map(stop => stop.stop_order)).toEqual([1, 2])

    form.removeStop(0)
    expect(form.stops.value.length).toBe(1)
    expect(form.stops.value).toEqual([
      { locality_id: 6, locality_name: 'Riobamba', stop_order: 1 },
    ])
  })
})

describe('API Client 403 Interceptors (CP-97, CP-98)', () => {
  it('triggers setCooperativaInactivaHandler on COOPERATIVA_ASIGNADA_INACTIVA', async () => {
    const mockHandler = vi.fn<(msg?: string) => void>()
    setCooperativaInactivaHandler(mockHandler)

    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      status: 403,
      ok: false,
      json: async () => ({
        detail: {
          code: 'COOPERATIVA_ASIGNADA_INACTIVA',
          message: 'Por el momento, su cooperativa se encuentra desactivada',
        },
      }),
    } as unknown as Response)

    await expect(apiClient('/rutas-cooperativa/especificas')).rejects.toMatchObject({
      status: 403,
    })
    expect(mockHandler).toHaveBeenCalledWith('Por el momento, su cooperativa se encuentra desactivada')
  })

  it('triggers setRecursoAjenoHandler when message indicates resource of another cooperative', async () => {
    const mockAjenoHandler = vi.fn<() => void>()
    setRecursoAjenoHandler(mockAjenoHandler)

    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      status: 403,
      ok: false,
      json: async () => ({
        detail: 'Recurso de otra cooperativa',
      }),
    } as unknown as Response)

    await expect(apiClient('/rutas/99')).rejects.toMatchObject({
      status: 403,
    })
    expect(mockAjenoHandler).toHaveBeenCalledWith('Recurso de otra cooperativa')
  })
})

describe('Rutas Store inactive cooperative handling (CA-97)', () => {
  it('sets isCooperativeInactive and suppresses error message on 403 COOPERATIVA_ASIGNADA_INACTIVA', async () => {
    setActivePinia(createPinia())
    const store = useRutasStore()
    vi.spyOn(routesApi, 'getSpecificRoutes').mockRejectedValue({
      status: 403,
      detail: { code: 'COOPERATIVA_ASIGNADA_INACTIVA', message: 'Por el momento, su cooperativa se encuentra desactivada' },
    })

    await store.fetchCoopSpecificRoutes()
    expect(store.isCooperativeInactive).toBe(true)
    expect(store.error).toBeNull()
  })
})
