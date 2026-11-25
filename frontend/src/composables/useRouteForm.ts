import { computed, ref } from 'vue'
import type { RouteCreatePayload, RouteDetail, RouteStopInput } from '@/services/rutas.service'
import {
  ERROR_DESTINATION_REQUIRED,
  ERROR_ORIGIN_REQUIRED,
  useFormValidation,
} from './useFormValidation'

type RouteField = keyof RouteCreatePayload
type RouteErrors = Partial<Record<RouteField, string>>

export function useRouteForm() {
  const {
    validateRouteOriginAndDestination,
    validateRouteDistance,
    validateRouteTime,
    validateRouteNameSuffix,
    validateRouteDescription,
    validateRouteStops,
  } = useFormValidation()

  const originId = ref<number | null>(null)
  const destinationId = ref<number | null>(null)
  const originName = ref('')
  const destinationName = ref('')
  const nameSuffix = ref('')
  const distanceKm = ref<string>('')
  const hours = ref<string>('')
  const minutes = ref<string>('')
  const description = ref('')
  const onlyOriginDest = ref(true)
  const stops = ref<Array<{ locality_id: number; stop_order: number; locality_name?: string }>>([])

  const isEditMode = ref(false)
  const hasAssociations = ref(false)
  const editingRouteId = ref<number | null>(null)

  const errors = ref<RouteErrors>({})
  const isSubmitting = ref(false)

  const computedPrefix = computed(() => {
    const o = originName.value || 'Origen'
    const d = destinationName.value || 'Destino'
    return `${o} - ${d}`
  })

  const computedFullName = computed(() => {
    const prefix = computedPrefix.value
    if (nameSuffix.value.trim()) {
      return `${prefix} ${nameSuffix.value.trim()}`
    }
    return prefix
  })

  function resetForm() {
    originId.value = null
    destinationId.value = null
    originName.value = ''
    destinationName.value = ''
    nameSuffix.value = ''
    distanceKm.value = ''
    hours.value = ''
    minutes.value = ''
    description.value = ''
    onlyOriginDest.value = true
    stops.value = []
    isEditMode.value = false
    hasAssociations.value = false
    editingRouteId.value = null
    errors.value = {}
    isSubmitting.value = false
  }

  function populateFromRoute(route: RouteDetail) {
    editingRouteId.value = route.id
    isEditMode.value = true
    hasAssociations.value = route.has_associations
    originId.value = route.origin_id
    destinationId.value = route.destination_id
    originName.value = route.origin_name || ''
    destinationName.value = route.destination_name || ''
    nameSuffix.value = route.name_suffix || ''
    distanceKm.value = String(route.distance_km)

    const totalMinutes = route.estimated_time_minutes || 0
    hours.value = String(Math.floor(totalMinutes / 60))
    minutes.value = String(totalMinutes % 60)

    description.value = route.description || ''

    if (route.stops && route.stops.length > 0) {
      onlyOriginDest.value = false
      stops.value = route.stops.map((s) => ({
        locality_id: s.locality_id,
        stop_order: s.stop_order,
        locality_name: s.locality_name,
      }))
    } else {
      onlyOriginDest.value = true
      stops.value = []
    }
    errors.value = {}
  }

  function addStop(localityId: number, localityName: string) {
    const nextOrder = stops.value.length + 1
    stops.value.push({
      locality_id: localityId,
      stop_order: nextOrder,
      locality_name: localityName,
    })
  }

  function removeStop(index: number) {
    if (index < 0 || index >= stops.value.length) return
    stops.value.splice(index, 1)
    updateStopOrder()
  }

  function updateStopOrder() {
    stops.value.forEach((s, i) => {
      s.stop_order = i + 1
    })
  }

  function moveStop(index: number, targetIndex: number) {
    if (index < 0 || index >= stops.value.length || targetIndex < 0 || targetIndex >= stops.value.length) return
    const [stop] = stops.value.splice(index, 1)
    if (!stop) return
    stops.value.splice(targetIndex, 0, stop)
    updateStopOrder()
  }

  function moveStopUp(index: number) {
    moveStop(index, index - 1)
  }

  function moveStopDown(index: number) {
    moveStop(index, index + 1)
  }

  function collectErrors(): RouteErrors {
    const errs: RouteErrors = {}

    if (!originId.value) errs.origin_id = ERROR_ORIGIN_REQUIRED
    if (!destinationId.value) errs.destination_id = ERROR_DESTINATION_REQUIRED
    const pairRes = validateRouteOriginAndDestination(originId.value, destinationId.value)
    if (originId.value && destinationId.value && !pairRes.isValid) {
      errs.destination_id = pairRes.errorMessage
    }

    const distRes = validateRouteDistance(distanceKm.value)
    if (!distRes.isValid) {
      errs.distance_km = distRes.errorMessage
    }

    const timeRes = validateRouteTime(hours.value, minutes.value)
    if (!timeRes.isValid) {
      errs.estimated_time_minutes = timeRes.errorMessage
    }

    const suffixRes = validateRouteNameSuffix(nameSuffix.value)
    if (!suffixRes.isValid) {
      errs.name_suffix = suffixRes.errorMessage
    }

    const descRes = validateRouteDescription(description.value)
    if (!descRes.isValid) {
      errs.description = descRes.errorMessage
    }

    const stopsRes = validateRouteStops(originId.value, destinationId.value, onlyOriginDest.value, stops.value)
    if (!stopsRes.isValid) {
      errs.stops = stopsRes.errorMessage
    }

    return errs
  }

  function validateField(field: RouteField): boolean {
    const currentErrors = collectErrors()
    // Origen y destino también condicionan la validez de las paradas.
    const relatedFields: RouteField[] = field === 'origin_id' || field === 'destination_id'
      ? ['origin_id', 'destination_id', 'stops']
      : [field]
    for (const relatedField of relatedFields) {
      if (currentErrors[relatedField]) {
        errors.value[relatedField] = currentErrors[relatedField]
      } else {
        delete errors.value[relatedField]
      }
    }
    return !errors.value[field]
  }

  function validateAll(): boolean {
    errors.value = collectErrors()
    return Object.keys(errors.value).length === 0
  }

  function buildPayload(): RouteCreatePayload {
    const h = hours.value ? parseInt(String(hours.value), 10) : 0
    const m = minutes.value ? parseInt(String(minutes.value), 10) : 0
    const totalMinutes = h * 60 + m

    const stopsPayload: RouteStopInput[] = onlyOriginDest.value
      ? []
      : stops.value.map((s, idx) => ({
          locality_id: s.locality_id,
          stop_order: idx + 1,
        }))

    return {
      origin_id: originId.value!,
      destination_id: destinationId.value!,
      name_suffix: nameSuffix.value.trim() ? nameSuffix.value.trim() : null,
      distance_km: parseFloat(String(distanceKm.value)),
      estimated_time_minutes: totalMinutes,
      description: description.value.trim() ? description.value.trim() : null,
      stops: stopsPayload,
    }
  }

  return {
    originId,
    destinationId,
    originName,
    destinationName,
    nameSuffix,
    distanceKm,
    hours,
    minutes,
    description,
    onlyOriginDest,
    stops,
    isEditMode,
    hasAssociations,
    editingRouteId,
    errors,
    isSubmitting,
    computedPrefix,
    computedFullName,
    resetForm,
    populateFromRoute,
    addStop,
    removeStop,
    moveStopUp,
    moveStopDown,
    validateField,
    validateAll,
    buildPayload,
  }
}
