<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { CheckSquare, Loader2, Route as RouteIcon, Search, Square, X } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { useRutasStore } from '@/stores/rutas.store'

const props = defineProps<{
  isOpen: boolean
  cooperativaId: number
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'adopted', count: number): void
}>()

const store = useRutasStore()
const searchQuery = ref('')
const selectedRouteIds = ref<number[]>([])
const isAdopting = ref(false)

watch(
  () => props.isOpen,
  async (open) => {
    if (open && props.cooperativaId) {
      selectedRouteIds.value = []
      searchQuery.value = ''
      await store.fetchAvailableGeneralRoutes()
    }
  },
  { immediate: true },
)

const filteredAvailableRoutes = computed(() => {
  let list = store.availableGeneralRoutes
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    list = list.filter(
      (r) =>
        r.name.toLowerCase().includes(q) ||
        (r.origin_name && r.origin_name.toLowerCase().includes(q)) ||
        (r.destination_name && r.destination_name.toLowerCase().includes(q)),
    )
  }
  return list
})

function toggleSelection(routeId: number) {
  const idx = selectedRouteIds.value.indexOf(routeId)
  if (idx > -1) {
    selectedRouteIds.value.splice(idx, 1)
  } else {
    selectedRouteIds.value.push(routeId)
  }
}

function selectAll() {
  if (selectedRouteIds.value.length === filteredAvailableRoutes.value.length) {
    selectedRouteIds.value = []
  } else {
    selectedRouteIds.value = filteredAvailableRoutes.value.map((r) => r.id)
  }
}

async function handleAdopt() {
  if (selectedRouteIds.value.length === 0 || !props.cooperativaId) return
  isAdopting.value = true
  try {
    const count = await store.adoptRoutes(selectedRouteIds.value)
    emit('adopted', count)
    emit('close')
  } finally {
    isAdopting.value = false
  }
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 overflow-y-auto animate-in fade-in-50 duration-200"
    data-test="general-routes-picker-modal"
  >
    <div
      class="relative w-full max-w-xl rounded-2xl border border-border bg-card shadow-2xl my-8 overflow-hidden"
      @click.stop
    >
      <!-- Modal Header -->
      <div class="flex items-center justify-between border-b border-border px-6 py-4 bg-muted/20">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <RouteIcon class="w-5 h-5" />
          </div>
          <div>
            <h2 class="text-base font-bold text-foreground">Agregar Rutas Generales</h2>
            <p class="text-xs text-muted-foreground">
              Seleccione las rutas interprovinciales que su cooperativa desea incorporar a su operación
            </p>
          </div>
        </div>

        <button
          type="button"
          class="rounded-xl p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors cursor-pointer"
          title="Cerrar"
          @click="emit('close')"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Modal Body -->
      <div class="p-6 space-y-4 max-h-[70vh] overflow-y-auto">
        <!-- Search bar -->
        <div class="relative">
          <Search class="w-4 h-4 text-muted-foreground absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar entre las rutas disponibles..."
            class="w-full pl-9 pr-4 py-2 rounded-xl border border-border bg-background text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-colors"
          />
        </div>

        <!-- Select All Toggle -->
        <div
          v-if="filteredAvailableRoutes.length > 0"
          class="flex items-center justify-between text-xs text-muted-foreground px-1"
        >
          <button
            type="button"
            class="flex items-center gap-2 font-medium hover:text-foreground cursor-pointer select-none"
            @click="selectAll"
          >
            <CheckSquare
              v-if="selectedRouteIds.length === filteredAvailableRoutes.length && filteredAvailableRoutes.length > 0"
              class="w-4 h-4 text-primary"
            />
            <Square v-else class="w-4 h-4" />
            <span>Seleccionar todas ({{ filteredAvailableRoutes.length }})</span>
          </button>

          <span class="font-mono">
            {{ selectedRouteIds.length }} seleccionada(s)
          </span>
        </div>

        <!-- Loading -->
        <div v-if="store.isLoading" class="py-8 text-center text-xs text-muted-foreground flex items-center justify-center gap-2">
          <Loader2 class="w-4 h-4 animate-spin text-primary" />
          <span>Cargando rutas disponibles...</span>
        </div>

        <!-- Empty State -->
        <div
          v-else-if="filteredAvailableRoutes.length === 0"
          class="py-8 text-center rounded-xl border border-dashed border-border text-xs text-muted-foreground"
        >
          No hay rutas generales disponibles para agregar en este momento.
        </div>

        <!-- Routes List -->
        <div v-else class="space-y-2 max-h-64 overflow-y-auto pr-1">
          <div
            v-for="r in filteredAvailableRoutes"
            :key="r.id"
            class="flex items-center justify-between p-3 rounded-xl border transition-colors cursor-pointer select-none"
            :class="
              selectedRouteIds.includes(r.id)
                ? 'border-primary/40 bg-primary/5'
                : 'border-border bg-card hover:bg-muted/30'
            "
            @click="toggleSelection(r.id)"
          >
            <div class="flex items-center gap-3">
              <button
                type="button"
                class="text-primary cursor-pointer shrink-0"
                :aria-label="r.name"
              >
                <CheckSquare v-if="selectedRouteIds.includes(r.id)" class="w-4 h-4 text-primary" />
                <Square v-else class="w-4 h-4 text-muted-foreground" />
              </button>
              <div>
                <p class="font-semibold text-sm text-foreground">{{ r.name }}</p>
                <p class="text-xs text-muted-foreground font-mono">
                  {{ r.distance_km }} km • {{ r.estimated_time_minutes }} min
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="flex items-center justify-end gap-3 border-t border-border px-6 py-4 bg-muted/10">
        <Button
          type="button"
          variant="outline"
          class="rounded-xl cursor-pointer"
          :disabled="isAdopting"
          @click="emit('close')"
        >
          Cancelar
        </Button>
        <Button
          type="button"
          class="rounded-xl gap-2 shadow-xs cursor-pointer"
          :disabled="selectedRouteIds.length === 0 || isAdopting"
          data-test="confirm-adopt-btn"
          @click="handleAdopt"
        >
          <Loader2 v-if="isAdopting" class="w-4 h-4 animate-spin" />
          <span>Adoptar seleccionadas ({{ selectedRouteIds.length }})</span>
        </Button>
      </div>
    </div>
  </div>
</template>
