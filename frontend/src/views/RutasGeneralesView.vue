<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import {
  AlertTriangle,
  Building2,
  CheckCircle2,
  ChevronDown,
  Eye,
  Filter,
  Loader2,
  Plus,
  RefreshCw,
  Search,
} from '@lucide/vue'
import { Button } from '@/components/ui/button'
import GeneralRoutesTable from '@/components/rutas/GeneralRoutesTable.vue'
import RouteFormDialog from '@/components/rutas/RouteFormDialog.vue'
import RouteDetailDialog from '@/components/rutas/RouteDetailDialog.vue'
import { useRutasStore } from '@/stores/rutas.store'
import { useRouteSubmission } from '@/composables/useRouteSubmission'
import type { Route, RouteCreatePayload, RouteDetail } from '@/services/rutas.service'

const store = useRutasStore()

const searchQuery = ref('')
const statusFilter = ref<'all' | 'active' | 'inactive'>('all')

const isFormOpen = ref(false)
const isDetailOpen = ref(false)
const selectedRouteDetail = ref<RouteDetail | null>(null)
const { isSubmitting: isSubmittingForm, submitError, clearSubmitError, submitRoute } = useRouteSubmission()
watch(isFormOpen, clearSubmitError)

// Toggle Status Confirmation Modal State
const isConfirmDeactivateOpen = ref(false)
const isConfirmActivateOpen = ref(false)
const routeToToggle = ref<Route | null>(null)
const isTogglingStatus = ref(false)

// Expanded cooperatives in specific routes section
const expandedCoops = ref<Record<number, boolean>>({})

onMounted(async () => {
  await loadData()
})

async function loadData() {
  await Promise.all([
    store.fetchGeneralRoutes(),
    store.fetchSpecificRoutesSupervision(),
  ])
}

const filteredGeneralRoutes = computed(() => {
  let list = store.generalRoutes

  // Filter by status
  if (statusFilter.value === 'active') {
    list = list.filter((r) => r.is_active)
  } else if (statusFilter.value === 'inactive') {
    list = list.filter((r) => !r.is_active)
  }

  // Filter by query (CP-83)
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

function openCreateDialog() {
  selectedRouteDetail.value = null
  isFormOpen.value = true
}

async function openEditDialog(routeItem: Route) {
  const detail = await store.fetchRouteDetail(routeItem.id)
  if (detail) {
    selectedRouteDetail.value = detail
    isFormOpen.value = true
  }
}

async function openDetailDialog(routeItem: Route | RouteDetail) {
  const detail = await store.fetchRouteDetail(routeItem.id)
  if (detail) {
    selectedRouteDetail.value = detail
    isDetailOpen.value = true
  }
}

async function handleFormSubmit(payload: RouteCreatePayload) {
  const saved = await submitRoute(() => selectedRouteDetail.value
    ? store.updateGeneralRoute(selectedRouteDetail.value.id, payload)
    : store.createGeneralRoute(payload))
  if (!saved) return
  isFormOpen.value = false
  try {
    await loadData()
  } catch {
    store.error = 'La ruta se guardó, pero no se pudo actualizar el listado. Pulse Actualizar.'
  }
}

function handleToggleStatusClick(routeItem: Route) {
  routeToToggle.value = routeItem
  if (routeItem.is_active) {
    // Show confirmation modal for deactivation (cascade warning)
    isConfirmDeactivateOpen.value = true
  } else {
    // Show confirmation modal for activation
    isConfirmActivateOpen.value = true
  }
}

async function confirmStatusToggle(targetStatus?: boolean) {
  if (!routeToToggle.value) return
  isTogglingStatus.value = true
  const newStatus = targetStatus !== undefined ? targetStatus : !routeToToggle.value.is_active
  try {
    await store.toggleGeneralRouteEstado(routeToToggle.value.id, newStatus, true)
    isConfirmDeactivateOpen.value = false
    isConfirmActivateOpen.value = false
    routeToToggle.value = null
    await loadData()
  } finally {
    isTogglingStatus.value = false
  }
}

function toggleCoopAccordion(coopId: number) {
  expandedCoops.value[coopId] = !expandedCoops.value[coopId]
}
</script>

<template>
  <div class="space-y-8" data-test="rutas-generales-view">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-foreground">Rutas Generales</h1>
        <p class="text-sm text-muted-foreground">
          Catálogo base de rutas interprovinciales disponibles para ser adoptadas por las cooperativas de transporte.
        </p>
      </div>

      <div class="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          class="rounded-xl gap-2 cursor-pointer"
          :disabled="store.isLoading"
          @click="loadData"
        >
          <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': store.isLoading }" />
          <span class="hidden sm:inline">Actualizar</span>
        </Button>

        <Button
          class="rounded-xl gap-2 shadow-xs cursor-pointer"
          data-test="new-general-route-btn"
          @click="openCreateDialog"
        >
          <Plus class="w-4 h-4" />
          <span>Nueva ruta</span>
        </Button>
      </div>
    </div>

    <!-- Feedback Banner -->
    <div
      v-if="store.feedbackMessage"
      class="p-4 rounded-xl border border-primary/20 bg-primary/10 text-primary text-sm flex items-center justify-between"
    >
      <span>{{ store.feedbackMessage }}</span>
      <button
        type="button"
        class="text-xs font-semibold hover:underline cursor-pointer"
        @click="store.clearFeedback"
      >
        Descartar
      </button>
    </div>

    <!-- Error Banner -->
    <div
      v-if="store.error"
      class="p-4 rounded-xl border border-destructive/20 bg-destructive/10 text-destructive text-sm flex items-center justify-between"
    >
      <span>{{ store.error }}</span>
      <button
        type="button"
        class="text-xs font-semibold hover:underline cursor-pointer"
        @click="store.error = null"
      >
        Descartar
      </button>
    </div>

    <!-- Filters Bar (CP-83) -->
    <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
      <!-- Search input -->
      <div class="relative flex-1">
        <Search class="w-4 h-4 text-muted-foreground absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Filtrar por nombre, origen o destino..."
          class="w-full pl-9 pr-4 py-2 rounded-xl border border-border bg-card text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-colors"
          data-test="search-routes-input"
        />
      </div>

      <!-- Status dropdown -->
      <div class="flex items-center gap-2">
        <Filter class="w-4 h-4 text-muted-foreground shrink-0" />
        <select
          v-model="statusFilter"
          class="rounded-xl border border-border bg-card px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-colors cursor-pointer"
          data-test="status-filter-select"
        >
          <option value="all">Todas las rutas</option>
          <option value="active">Solo activas</option>
          <option value="inactive">Solo inactivas</option>
        </select>
      </div>
    </div>

    <!-- General Routes Table -->
    <section class="space-y-3">
      <div class="flex items-center justify-between">
        <h2 class="text-sm font-bold uppercase tracking-wider text-muted-foreground">
          Rutas Generales del Sistema
        </h2>
        <span class="text-xs font-mono text-muted-foreground">
          {{ filteredGeneralRoutes.length }} ruta(s)
        </span>
      </div>

      <GeneralRoutesTable
        :routes="filteredGeneralRoutes"
        :is-loading="store.isLoading"
        @view="openDetailDialog"
        @edit="openEditDialog"
        @toggle-status="handleToggleStatusClick"
      />
    </section>

    <!-- Supervised Specific Routes Section (CP-84) -->
    <section class="space-y-4 pt-4 border-t border-border">
      <div>
        <h2 class="text-base font-bold text-foreground flex items-center gap-2">
          <Building2 class="w-5 h-5 text-primary" />
          <span>Rutas Específicas por Cooperativa (Supervisión)</span>
        </h2>
        <p class="text-xs text-muted-foreground">
          Visualización en modo solo lectura de las rutas exclusivas creadas por cada cooperativa de transporte.
        </p>
      </div>

      <div
        v-if="store.specificRoutesGroups.length === 0"
        class="p-6 rounded-xl border border-dashed border-border text-center text-sm text-muted-foreground"
      >
        No hay rutas específicas registradas por cooperativas en este momento.
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="group in store.specificRoutesGroups"
          :key="group.cooperativa_id"
          class="rounded-xl border border-border bg-card overflow-hidden shadow-xs"
        >
          <!-- Cooperative Group Header Accordion -->
          <button
            type="button"
            class="w-full flex items-center justify-between px-5 py-3.5 bg-muted/20 hover:bg-muted/40 transition-colors text-left cursor-pointer"
            @click="toggleCoopAccordion(group.cooperativa_id)"
          >
            <div class="flex items-center gap-3">
              <div class="flex items-center justify-center w-7 h-7 rounded-lg bg-primary/10 text-primary font-bold text-xs">
                <Building2 class="w-4 h-4" />
              </div>
              <div>
                <span class="font-bold text-sm text-foreground">{{ group.cooperativa_name }}</span>
                <span class="text-xs text-muted-foreground ml-2 font-mono">
                  ({{ group.routes.length }} ruta{{ group.routes.length === 1 ? '' : 's' }})
                </span>
              </div>
            </div>

            <ChevronDown
              class="w-4 h-4 text-muted-foreground transition-transform duration-200"
              :class="{ 'rotate-180': expandedCoops[group.cooperativa_id] }"
            />
          </button>

          <!-- Group Routes Table (shown when expanded) -->
          <div v-if="expandedCoops[group.cooperativa_id]" class="border-t border-border overflow-x-auto">
            <table class="w-full text-left text-xs text-foreground">
              <thead class="bg-muted/30 text-muted-foreground uppercase font-semibold">
                <tr>
                  <th class="px-4 py-2.5">Ruta</th>
                  <th class="px-4 py-2.5">Origen → Destino</th>
                  <th class="px-4 py-2.5">Distancia</th>
                  <th class="px-4 py-2.5">Tiempo est.</th>
                  <th class="px-4 py-2.5">Estado</th>
                  <th class="px-4 py-2.5 text-right">Detalle</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-border">
                <tr v-for="sr in group.routes" :key="sr.id" class="hover:bg-muted/10">
                  <td class="px-4 py-3 font-semibold">{{ sr.name }}</td>
                  <td class="px-4 py-3">{{ sr.origin_name }} → {{ sr.destination_name }}</td>
                  <td class="px-4 py-3 font-mono">{{ sr.distance_km }} km</td>
                  <td class="px-4 py-3 font-mono">{{ sr.estimated_time_minutes }} min</td>
                  <td class="px-4 py-3">
                    <span
                      class="px-2 py-0.5 rounded-full text-[10px] font-semibold"
                      :class="
                        sr.is_active
                          ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                          : 'bg-muted text-muted-foreground border border-border'
                      "
                    >
                      {{ sr.is_active ? 'Activa' : 'Inactiva' }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-right">
                    <Button
                      variant="ghost"
                      size="icon"
                      class="h-7 w-7 rounded-lg cursor-pointer"
                      title="Ver detalle de ruta específica"
                      @click="openDetailDialog(sr)"
                    >
                      <Eye class="w-3.5 h-3.5" />
                    </Button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>

    <!-- Dialogs -->
    <RouteFormDialog
      :is-open="isFormOpen"
      :route="selectedRouteDetail"
      :is-submitting="isSubmittingForm"
      :submit-error="submitError"
      @close="isFormOpen = false"
      @submit="handleFormSubmit"
    />

    <RouteDetailDialog
      :is-open="isDetailOpen"
      :route="selectedRouteDetail"
      @close="isDetailOpen = false"
    />

    <!-- Deactivation Cascade Confirmation Dialog (CP-80, CP-81, CP-82) -->
    <div
      v-if="isConfirmDeactivateOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in-50 duration-200"
      data-test="deactivate-confirm-dialog"
    >
      <div class="relative w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-2xl space-y-4">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400 shrink-0">
            <AlertTriangle class="w-5 h-5" />
          </div>
          <div>
            <h3 class="text-base font-bold text-foreground">¿Desactivar ruta general?</h3>
            <p class="text-xs text-muted-foreground">{{ routeToToggle?.name }}</p>
          </div>
        </div>

        <p class="text-sm text-foreground/80 leading-relaxed">
          Al desactivar esta ruta general, se desactivarán automáticamente en cascada todas las rutas adoptadas por las
          cooperativas que la tenían asociada, y se enviará una notificación a sus administradores.
        </p>

        <div class="flex items-center justify-end gap-3 pt-2">
          <Button
            type="button"
            variant="outline"
            class="rounded-xl cursor-pointer"
            :disabled="isTogglingStatus"
            @click="isConfirmDeactivateOpen = false"
          >
            Cancelar
          </Button>
          <Button
            type="button"
            variant="destructive"
            class="rounded-xl gap-2 cursor-pointer shadow-xs"
            :disabled="isTogglingStatus"
            data-test="confirm-deactivate-btn"
            @click="confirmStatusToggle(false)"
          >
            <Loader2 v-if="isTogglingStatus" class="w-4 h-4 animate-spin" />
            <span>Confirmar desactivación</span>
          </Button>
        </div>
      </div>
    </div>

    <!-- Activation Confirmation Dialog -->
    <div
      v-if="isConfirmActivateOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in-50 duration-200"
      data-test="activate-confirm-dialog"
    >
      <div class="relative w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-2xl space-y-4">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 shrink-0">
            <CheckCircle2 class="w-5 h-5" />
          </div>
          <div>
            <h3 class="text-base font-bold text-foreground">¿Reactivar ruta general?</h3>
            <p class="text-xs text-muted-foreground">{{ routeToToggle?.name }}</p>
          </div>
        </div>

        <p class="text-sm text-foreground/80 leading-relaxed">
          Al reactivar esta ruta general, volverá a estar disponible en el catálogo base para ser adoptada por las cooperativas de transporte.
        </p>

        <div class="flex items-center justify-end gap-3 pt-2">
          <Button
            type="button"
            variant="outline"
            class="rounded-xl cursor-pointer"
            :disabled="isTogglingStatus"
            @click="isConfirmActivateOpen = false"
          >
            Cancelar
          </Button>
          <Button
            type="button"
            class="rounded-xl gap-2 cursor-pointer shadow-xs bg-emerald-600 hover:bg-emerald-700 text-white"
            :disabled="isTogglingStatus"
            data-test="confirm-activate-btn"
            @click="confirmStatusToggle(true)"
          >
            <Loader2 v-if="isTogglingStatus" class="w-4 h-4 animate-spin" />
            <span>Confirmar reactivación</span>
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
