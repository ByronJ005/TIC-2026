<script setup lang="ts">
import { watch } from 'vue'
import { AlertCircle, Loader2, Navigation, Route as RouteIcon, X } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import LocalityCombobox from './LocalityCombobox.vue'
import RouteStopsEditor from './RouteStopsEditor.vue'
import RouteTimeInput from './RouteTimeInput.vue'
import { useRouteForm } from '@/composables/useRouteForm'
import type { RouteCreatePayload, RouteDetail } from '@/services/rutas.service'
import type { Locality } from '@/services/localidades.service'

const props = defineProps<{
  isOpen: boolean
  route: RouteDetail | null
  cooperativaId?: number | null
  isSubmitting?: boolean
  submitError?: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'submit', payload: RouteCreatePayload): void
}>()

const {
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
  errors,
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
} = useRouteForm()

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      if (props.route) {
        populateFromRoute(props.route)
      } else {
        resetForm()
      }
    }
  },
  { immediate: true },
)

function onOriginSelected(loc: Locality | null) {
  originId.value = loc?.id ?? null
  originName.value = loc?.name ?? ''
  validateField('origin_id')
}

function onDestinationSelected(loc: Locality | null) {
  destinationId.value = loc?.id ?? null
  destinationName.value = loc?.name ?? ''
  validateField('destination_id')
}

function onDistanceInput(e: Event) {
  const target = e.target as HTMLInputElement
  let val = target.value.replace(/[^0-9.]/g, '')
  const parts = val.split('.')
  const integerPart = parts[0].slice(0, 3)
  if (parts.length > 1) {
    val = `${integerPart}.${parts[1].slice(0, 2)}`
  } else {
    val = integerPart
  }
  target.value = val
  distanceKm.value = val
  validateField('distance_km')
}

function filterDistanceKey(e: KeyboardEvent) {
  // Allow control keys
  if (
    ['Backspace', 'Tab', 'Enter', 'Delete', 'ArrowLeft', 'ArrowRight', 'Escape'].includes(e.key) ||
    (e.ctrlKey || e.metaKey)
  ) {
    return
  }
  // Allow digits and single decimal dot
  if (!/^\d$/.test(e.key) && e.key !== '.') {
    e.preventDefault()
    return
  }
  if (e.key === '.' && distanceKm.value.includes('.')) {
    e.preventDefault()
    return
  }
  // Limit integer digits to at most 3
  const target = e.target as HTMLInputElement
  const hasSelection = (target.selectionEnd ?? 0) - (target.selectionStart ?? 0) > 0
  if (!hasSelection && /^\d$/.test(e.key)) {
    const dotIdx = distanceKm.value.indexOf('.')
    const cursor = target.selectionStart ?? distanceKm.value.length
    if (dotIdx === -1 && distanceKm.value.length >= 3) {
      e.preventDefault()
    } else if (dotIdx !== -1 && cursor <= dotIdx && distanceKm.value.slice(0, dotIdx).length >= 3) {
      e.preventDefault()
    }
  }
}

function handleClose() {
  if (props.isSubmitting) return
  emit('close')
}

function handleSubmit() {
  if (props.isSubmitting) return
  const isValid = validateAll()
  if (!isValid) return
  const payload = buildPayload()
  emit('submit', payload)
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 overflow-y-auto animate-in fade-in-50 duration-200"
    data-test="route-form-dialog"
  >
    <div
      class="relative w-full max-w-2xl rounded-2xl border border-border bg-card shadow-2xl my-8 overflow-hidden"
      @click.stop
    >
      <!-- Dialog Header -->
      <div class="flex items-center justify-between border-b border-border px-6 py-4 bg-muted/20">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <RouteIcon class="w-5 h-5" />
          </div>
          <div>
            <h2 class="text-base font-bold text-foreground">
              {{ isEditMode ? 'Editar ruta' : 'Nueva ruta' }}
            </h2>
            <p class="text-xs text-muted-foreground">
              {{
                isEditMode
                  ? 'Modifique los datos informativos de la ruta seleccionada'
                  : 'Complete los campos obligatorios para registrar una nueva ruta'
              }}
            </p>
          </div>
        </div>

        <button
          type="button"
          class="rounded-xl p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors cursor-pointer"
          title="Cerrar"
          @click="handleClose"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Warning if route has associations (CP-79) -->
      <div
        v-if="isEditMode && hasAssociations"
        class="mx-6 mt-4 flex items-start gap-3 rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-800 dark:text-amber-200"
      >
        <AlertCircle class="w-4 h-4 shrink-0 text-amber-600 dark:text-amber-400 mt-0.5" />
        <div>
          <p class="font-semibold">Origen y Destino no modificables</p>
          <p>
            Esta ruta tiene cooperativas, turnos o viajes asociados. Solo se permite editar la información complementaria
            (distancia, tiempo, paradas intermedias, texto adicional y descripción).
          </p>
        </div>
      </div>

      <!-- Dialog Body -->
      <div class="p-6 space-y-5 max-h-[75vh] overflow-y-auto">
        <!-- Origin & Destination -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <LocalityCombobox
            :model-value="originId"
            :model-name="originName"
            label="Localidad de origen"
            placeholder="Seleccione ciudad o localidad de origen..."
            :error="errors.origin_id"
            :disabled="isEditMode && hasAssociations"
            :exclude-id="destinationId"
            required
            @selected="onOriginSelected"
          />

          <LocalityCombobox
            :model-value="destinationId"
            :model-name="destinationName"
            label="Localidad de destino"
            placeholder="Seleccione ciudad o localidad de destino..."
            :error="errors.destination_id"
            :disabled="isEditMode && hasAssociations"
            :exclude-id="originId"
            required
            @selected="onDestinationSelected"
          />
        </div>

        <!-- Calculated Name Preview + Suffix -->
        <div class="rounded-xl border border-border bg-muted/20 p-4 space-y-3">
          <div class="flex items-center justify-between">
            <label class="block text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Nombre de la ruta
            </label>
            <span class="text-[11px] font-mono text-muted-foreground">
              {{ nameSuffix.length }}/30 caracteres adicionales
            </span>
          </div>

          <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <!-- Non-editable Prefix Badge -->
            <div
              class="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-primary/10 border border-primary/20 text-primary text-sm font-semibold shrink-0 select-none"
              title="Prefijo autogenerado por Origen y Destino"
            >
              <Navigation class="w-3.5 h-3.5" />
              <span>{{ computedPrefix }}</span>
            </div>

            <!-- Optional Additional Suffix -->
            <input
              type="text"
              v-model="nameSuffix"
              maxlength="30"
              placeholder="Texto adicional (ej: Vía Catamayo)"
              class="flex-1 px-3 py-2 rounded-xl border bg-background text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-colors"
              :class="errors.name_suffix ? 'border-destructive' : 'border-border'"
              @input="validateField('name_suffix')"
            />
          </div>

          <p class="text-xs text-muted-foreground">
            Nombre resultante: <strong class="text-foreground font-semibold">{{ computedFullName }}</strong>
          </p>
          <p v-if="errors.name_suffix" class="text-xs font-medium text-destructive">
            {{ errors.name_suffix }}
          </p>
        </div>

        <!-- Distance & Time -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <!-- Distance -->
          <div>
            <label class="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
              Distancia (km)
              <span class="text-destructive ml-0.5">*</span>
            </label>
            <div class="relative flex items-center">
              <input
                type="text"
                inputmode="decimal"
                maxlength="6"
                :value="distanceKm"
                placeholder="Ej: 68.5"
                class="w-full pl-3 pr-10 py-2 rounded-xl border bg-background text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-colors"
                :class="errors.distance_km ? 'border-destructive' : 'border-border'"
                data-test="distance-km-input"
                @keydown="filterDistanceKey"
                @input="onDistanceInput"
              />
              <span class="absolute right-3 text-xs font-medium text-muted-foreground pointer-events-none select-none">
                km
              </span>
            </div>
            <p v-if="errors.distance_km" class="text-xs font-medium text-destructive mt-1">
              {{ errors.distance_km }}
            </p>
          </div>

          <!-- Estimated Time -->
          <RouteTimeInput
            :hours="hours"
            :minutes="minutes"
            :error="errors.estimated_time_minutes"
            required
            @update:hours="(val) => { hours = val; validateField('estimated_time_minutes') }"
            @update:minutes="(val) => { minutes = val; validateField('estimated_time_minutes') }"
            @blur="validateField('estimated_time_minutes')"
          />
        </div>

        <!-- Stops Editor -->
        <RouteStopsEditor
          :stops="stops"
          :origin-id="originId"
          :destination-id="destinationId"
          :only-origin-dest="onlyOriginDest"
          :error="errors.stops"
          @update:only-origin-dest="(val) => { onlyOriginDest = val; if (val) stops = []; validateField('stops') }"
          @add-stop="({ localityId, localityName }) => { addStop(localityId, localityName); validateField('stops') }"
          @remove-stop="(idx) => { removeStop(idx); validateField('stops') }"
          @move-up="moveStopUp"
          @move-down="moveStopDown"
        />

        <!-- Description (Optional, max 100) -->
        <div>
          <div class="flex items-center justify-between mb-1.5">
            <label class="block text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Descripción (opcional)
            </label>
            <span class="text-[11px] font-mono text-muted-foreground">
              {{ description.length }}/100 caracteres
            </span>
          </div>
          <textarea
            v-model="description"
            rows="2"
            maxlength="100"
            placeholder="Detalles adicionales sobre la ruta..."
            class="w-full p-3 rounded-xl border bg-background text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-colors resize-none"
            :class="errors.description ? 'border-destructive' : 'border-border'"
            @input="validateField('description')"
          ></textarea>
          <p v-if="errors.description" class="text-xs font-medium text-destructive mt-1">
            {{ errors.description }}
          </p>
        </div>
      </div>

      <!-- Dialog Footer -->
      <div
        v-if="submitError"
        role="alert"
        class="mx-6 mb-4 flex items-start gap-2 rounded-xl border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive"
        data-test="route-submit-error"
      >
        <AlertCircle class="w-4 h-4 shrink-0 mt-0.5" />
        <span>{{ submitError }}</span>
      </div>
      <div class="flex items-center justify-end gap-3 border-t border-border px-6 py-4 bg-muted/10">
        <Button
          type="button"
          variant="outline"
          class="rounded-xl cursor-pointer"
          :disabled="isSubmitting"
          @click="handleClose"
        >
          Cancelar
        </Button>
        <Button
          type="button"
          class="rounded-xl gap-2 shadow-xs cursor-pointer"
          :disabled="isSubmitting"
          data-test="save-route-btn"
          @click="handleSubmit"
        >
          <Loader2 v-if="isSubmitting" class="w-4 h-4 animate-spin" />
          <span>{{ isEditMode ? 'Guardar cambios' : 'Crear ruta' }}</span>
        </Button>
      </div>
    </div>
  </div>
</template>
