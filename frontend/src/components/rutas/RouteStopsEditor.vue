<script setup lang="ts">
import { ref } from 'vue'
import { ArrowDown, ArrowUp, CheckSquare, Square, Trash2 } from '@lucide/vue'
import LocalityCombobox from './LocalityCombobox.vue'
import type { Locality } from '@/services/localidades.service'

const props = withDefaults(
  defineProps<{
    stops: Array<{ locality_id: number; stop_order: number; locality_name?: string }>
    originId: number | null
    destinationId: number | null
    onlyOriginDest: boolean
    error?: string
    disabled?: boolean
  }>(),
  {
    error: '',
    disabled: false,
  },
)

const emit = defineEmits<{
  (e: 'update:onlyOriginDest', value: boolean): void
  (e: 'addStop', payload: { localityId: number; localityName: string }): void
  (e: 'removeStop', index: number): void
  (e: 'moveUp', index: number): void
  (e: 'moveDown', index: number): void
}>()

const newStopId = ref<number | null>(null)
const newStopName = ref('')
const comboboxError = ref('')

function toggleOnlyOriginDest() {
  if (props.disabled) return
  emit('update:onlyOriginDest', !props.onlyOriginDest)
}

function onLocalitySelected(loc: Locality | null) {
  if (!loc) {
    newStopId.value = null
    newStopName.value = ''
    return
  }
  comboboxError.value = ''
  // CP-69: Intermediate stop cannot be origin or destination
  if (loc.id === props.originId || loc.id === props.destinationId) {
    comboboxError.value = 'Una parada intermedia no puede ser idéntica al origen o destino'
    newStopId.value = null
    newStopName.value = ''
    return
  }
  // CP-70: No duplicate stops
  if (props.stops.some((s) => s.locality_id === loc.id)) {
    comboboxError.value = 'Esta localidad ya ha sido agregada como parada'
    newStopId.value = null
    newStopName.value = ''
    return
  }

  emit('addStop', { localityId: loc.id, localityName: loc.name })
  newStopId.value = null
  newStopName.value = ''
}
</script>

<template>
  <div class="w-full text-left space-y-2" data-test="route-stops-editor">
    <label class="block text-xs font-semibold uppercase tracking-wider text-muted-foreground">
      Recorrido
    </label>

    <!-- Toggle Solo Origen y Destino -->
    <div
      class="flex items-center gap-2.5 p-3 rounded-xl border border-border bg-card/60 transition-colors select-none"
      :class="{ 'opacity-50 cursor-not-allowed': disabled, 'cursor-pointer hover:bg-muted/30': !disabled }"
      @click="toggleOnlyOriginDest"
    >
      <button
        type="button"
        class="text-primary cursor-pointer shrink-0"
        :disabled="disabled"
        aria-label="Solo las de origen y destino"
      >
        <CheckSquare v-if="onlyOriginDest" class="w-5 h-5 text-primary" />
        <Square v-else class="w-5 h-5 text-muted-foreground" />
      </button>

      <div class="flex-1 text-sm">
        <span class="font-medium text-foreground">Solo las de origen y destino</span>
        <p class="text-xs text-muted-foreground">
          Marque esta opción si la ruta es directa sin paradas intermedias
        </p>
      </div>
    </div>

    <!-- Intermediate stops container (shown only when unchecked) -->
    <div v-if="!onlyOriginDest" class="space-y-3 pt-1 animate-in fade-in-50 duration-150">
      <div class="flex items-center justify-between">
        <label class="block text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Paradas intermedias ordenadas
        </label>
        <span class="text-xs text-muted-foreground font-mono">
          {{ stops.length }} parada(s)
        </span>
      </div>

      <!-- Current stops list -->
      <div v-if="stops.length > 0" class="space-y-2">
        <div
          v-for="(stop, idx) in stops"
          :key="stop.locality_id"
          class="flex items-center gap-2.5 p-2.5 rounded-xl border border-border bg-muted/20 text-sm"
        >
          <!-- Sequence Badge (CP-71) -->
          <div
            class="flex items-center justify-center w-6 h-6 rounded-lg bg-primary/10 text-primary font-bold text-xs shrink-0"
          >
            {{ idx + 1 }}
          </div>

          <div class="flex-1 truncate font-medium text-foreground">
            {{ stop.locality_name || `Localidad #${stop.locality_id}` }}
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-1 shrink-0">
            <button
              type="button"
              class="p-1 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted disabled:opacity-30 disabled:pointer-events-none cursor-pointer transition-colors"
              title="Mover arriba"
              :disabled="disabled || idx === 0"
              @click="$emit('moveUp', idx)"
            >
              <ArrowUp class="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              class="p-1 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted disabled:opacity-30 disabled:pointer-events-none cursor-pointer transition-colors"
              title="Mover abajo"
              :disabled="disabled || idx === stops.length - 1"
              @click="$emit('moveDown', idx)"
            >
              <ArrowDown class="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              class="p-1 rounded-lg text-destructive hover:bg-destructive/10 cursor-pointer transition-colors"
              title="Quitar parada"
              :disabled="disabled"
              @click="$emit('removeStop', idx)"
            >
              <Trash2 class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      <!-- Empty state for stops -->
      <div
        v-else
        class="p-3 text-center rounded-xl border border-dashed border-border text-xs text-muted-foreground"
      >
        Aún no se han agregado paradas intermedias. Utilice el selector inferior para agregarlas.
      </div>

      <!-- Add stop selector -->
      <div v-if="!disabled" class="space-y-1">
        <LocalityCombobox
          :model-value="newStopId"
          placeholder="Buscar o registrar parada intermedia..."
          :error="comboboxError"
          @selected="onLocalitySelected"
        />
      </div>
    </div>

    <!-- General error message -->
    <p v-if="error" class="text-xs font-medium text-destructive mt-1">
      {{ error }}
    </p>
  </div>
</template>
