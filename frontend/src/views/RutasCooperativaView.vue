<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import {
  AlertCircle,
  AlertTriangle,
  Building2,
  CheckCircle2,
  Eye,
  Loader2,
  Pencil,
  Plus,
  Power,
  RefreshCw,
  Route as RouteIcon,
  XCircle,
} from '@lucide/vue'
import { Button } from '@/components/ui/button'
import GeneralRoutesPickerModal from '@/components/rutas/GeneralRoutesPickerModal.vue'
import RouteFormDialog from '@/components/rutas/RouteFormDialog.vue'
import RouteDetailDialog from '@/components/rutas/RouteDetailDialog.vue'
import { useAuthStore } from '@/stores/auth.store'
import { useRutasStore } from '@/stores/rutas.store'
import { useRouteSubmission } from '@/composables/useRouteSubmission'
import { CooperativasService } from '@/services/cooperativas.service'
import type { Route, RouteCreatePayload, RouteDetail } from '@/services/rutas.service'

const authStore = useAuthStore()
const rutasStore = useRutasStore()

const cooperativaId = computed(() => authStore.user?.cooperativa_id ?? 0)
const cooperativaNombre = ref('')
const cooperativaLabel = computed(() => {
  return cooperativaNombre.value || authStore.user?.cooperativa_name || 'Específicas de la Cooperativa'
})
const localCoopInactive = ref(false)
const isCooperativeInactive = computed(() => rutasStore.isCooperativeInactive || localCoopInactive.value)

const isPickerOpen = ref(false)
const isFormOpen = ref(false)
const isDetailOpen = ref(false)
const selectedRouteDetail = ref<RouteDetail | null>(null)
const { isSubmitting: isSubmittingForm, submitError, clearSubmitError, submitRoute } = useRouteSubmission()
watch(isFormOpen, clearSubmitError)

// Status toggling for specific routes
const isConfirmDeactivateOpen = ref(false)
const isConfirmActivateOpen = ref(false)
const routeToToggle = ref<Route | null>(null)
const isTogglingStatus = ref(false)

onMounted(async () => {
  rutasStore.error = null
  if (cooperativaId.value) {
    await loadData()
  }
})

async function loadData() {
  if (!cooperativaId.value) {
    rutasStore.error = null
    return
  }

  if (!authStore.user?.cooperativa_name && !cooperativaNombre.value) {
    CooperativasService.getCooperativaById(cooperativaId.value)
      .then((coop) => {
        if (coop) {
          if (coop.name) cooperativaNombre.value = coop.name
          if (coop.is_active === false) {
            localCoopInactive.value = true
          }
        }
      })
      .catch((err: unknown) => {
        const apiErr = err as { status?: number; detail?: { code?: string } }
        if (apiErr?.status === 403 || apiErr?.detail?.code === 'COOPERATIVA_ASIGNADA_INACTIVA') {
          localCoopInactive.value = true
        }
      })
  }

  await Promise.all([
    rutasStore.fetchCoopAdoptedRoutes(),
    rutasStore.fetchCoopSpecificRoutes(),
  ])
}

function formatTime(minutes: number): string {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  if (h > 0 && m > 0) return `${h}h ${m}m`
  if (h > 0) return `${h}h`
  return `${m}m`
}

function openCreateSpecificRoute() {
  selectedRouteDetail.value = null
  isFormOpen.value = true
}

async function openEditSpecificRoute(routeItem: Route) {
  const detail = await rutasStore.fetchRouteDetail(routeItem.id)
  if (detail) {
    selectedRouteDetail.value = detail
    isFormOpen.value = true
  }
}

async function openDetailDialog(routeId: number) {
  const detail = await rutasStore.fetchRouteDetail(routeId)
  if (detail) {
    selectedRouteDetail.value = detail
    isDetailOpen.value = true
  }
}

async function handleFormSubmit(payload: RouteCreatePayload) {
  if (!cooperativaId.value) return
  const saved = await submitRoute(() => selectedRouteDetail.value
    ? rutasStore.updateSpecificRoute(selectedRouteDetail.value.id, payload)
    : rutasStore.createSpecificRoute(payload))
  if (!saved) return
  isFormOpen.value = false
  await loadData()
}

async function handleToggleAdoptedStatus(adoptionId: number, currentActive: boolean) {
  if (!cooperativaId.value) return
  await rutasStore.toggleAdoptionEstado(adoptionId, !currentActive)
}

function handleToggleSpecificStatusClick(routeItem: Route) {
  routeToToggle.value = routeItem
  if (routeItem.is_active) {
    isConfirmDeactivateOpen.value = true
  } else {
    isConfirmActivateOpen.value = true
  }
}

async function confirmToggleSpecificStatus(targetStatus?: boolean) {
  if (!routeToToggle.value || !cooperativaId.value) return
  isTogglingStatus.value = true
  const newStatus = targetStatus !== undefined ? targetStatus : !routeToToggle.value.is_active
  try {
    await rutasStore.toggleSpecificRouteEstado(routeToToggle.value.id, newStatus, true)
    isConfirmDeactivateOpen.value = false
    isConfirmActivateOpen.value = false
    routeToToggle.value = null
    await loadData()
  } finally {
    isTogglingStatus.value = false
  }
}
</script>

<template>
  <div class="space-y-8" data-test="rutas-cooperativa-view">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-foreground">Gestión de Rutas</h1>
        <p class="text-sm text-muted-foreground">
          Administre las rutas generales incorporadas y las rutas exclusivas de su cooperativa.
        </p>
      </div>

      <div class="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          class="rounded-xl gap-2 cursor-pointer"
          :disabled="rutasStore.isLoading"
          @click="loadData"
        >
          <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': rutasStore.isLoading }" />
          <span class="hidden sm:inline">Actualizar</span>
        </Button>
      </div>
    </div>

    <!-- No assigned cooperative notice -->
    <div
      v-if="!cooperativaId"
      class="p-6 rounded-2xl border border-amber-500/30 bg-amber-500/10 text-amber-800 dark:text-amber-200 flex items-start gap-4"
      data-test="no-coop-notice"
    >
      <AlertCircle class="w-6 h-6 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
      <div>
        <h3 class="font-bold text-base">Sin cooperativa asignada</h3>
        <p class="text-sm mt-1">
          Su usuario administrador no tiene una cooperativa asignada en el sistema. Contacte al Administrador General
          para configurar su asignación.
        </p>
      </div>
    </div>

    <!-- Deactivated cooperative notice (CA-97) -->
    <div
      v-else-if="isCooperativeInactive"
      class="p-6 rounded-2xl border border-amber-500/30 bg-amber-500/10 text-amber-800 dark:text-amber-200 flex items-start gap-4"
      data-test="coop-inactive-notice"
    >
      <AlertCircle class="w-6 h-6 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
      <div>
        <h3 class="font-bold text-base">Cooperativa desactivada</h3>
        <p class="text-sm mt-1">
          Por el momento, su cooperativa se encuentra desactivada. El Administrador General ha deshabilitado su cooperativa, por lo que no es posible gestionar ni operar rutas. Contacte a la administración para más información.
        </p>
      </div>
    </div>

    <!-- Feedback Banner -->
    <div
      v-if="rutasStore.feedbackMessage && cooperativaId && !isCooperativeInactive"
      class="p-4 rounded-xl border border-primary/20 bg-primary/10 text-primary text-sm flex items-center justify-between"
    >
      <span>{{ rutasStore.feedbackMessage }}</span>
      <button
        type="button"
        class="text-xs font-semibold hover:underline cursor-pointer"
        @click="rutasStore.clearFeedback"
      >
        Descartar
      </button>
    </div>

    <!-- Error Banner -->
    <div
      v-if="rutasStore.error && cooperativaId && !isCooperativeInactive"
      class="p-4 rounded-xl border border-destructive/20 bg-destructive/10 text-destructive text-sm flex items-center justify-between"
    >
      <span>{{ rutasStore.error }}</span>
      <button
        type="button"
        class="text-xs font-semibold hover:underline cursor-pointer"
        @click="rutasStore.error = null"
      >
        Descartar
      </button>
    </div>

    <!-- SECTION 1: Adopted General Routes (Rutas Generales) -->
    <section v-if="cooperativaId && !isCooperativeInactive" class="space-y-4" data-test="adopted-routes-section">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <h2 class="text-base font-bold text-foreground flex items-center gap-2">
            <RouteIcon class="w-5 h-5 text-primary" />
            <span>Rutas Generales Adoptadas</span>
          </h2>
          <p class="text-xs text-muted-foreground">
            Rutas interprovinciales habilitadas desde el catálogo general para su operación.
          </p>
        </div>

        <Button
          class="rounded-xl gap-2 shadow-xs cursor-pointer"
          data-test="add-general-route-btn"
          @click="isPickerOpen = true"
        >
          <Plus class="w-4 h-4" />
          <span>Agregar ruta general</span>
        </Button>
      </div>

      <!-- Adopted Routes Table -->
      <div class="overflow-x-auto rounded-xl border border-border bg-card shadow-xs">
        <table class="w-full text-left text-sm text-foreground">
          <thead class="border-b border-border bg-muted/40 text-xs font-semibold uppercase text-muted-foreground">
            <tr>
              <th scope="col" class="px-5 py-3.5">Ruta General</th>
              <th scope="col" class="px-5 py-3.5">Trayecto</th>
              <th scope="col" class="px-5 py-3.5">Distancia / Tiempo</th>
              <th scope="col" class="px-5 py-3.5">Catálogo General</th>
              <th scope="col" class="px-5 py-3.5">Operación Propia</th>
              <th scope="col" class="px-5 py-3.5 text-right">Detalle</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            <tr
              v-for="ag in rutasStore.adoptedRoutes"
              :key="ag.id"
              class="transition-colors hover:bg-muted/20"
              :class="{ 'opacity-70 bg-muted/10': !ag.is_active || !ag.route.is_active }"
            >
              <!-- Name -->
              <td class="px-5 py-4 font-semibold text-foreground">
                <span class="truncate max-w-xs">{{ ag.route.name }}</span>
              </td>

              <!-- Origin -> Dest -->
              <td class="px-5 py-4 text-xs">
                <div class="flex items-center gap-1.5 font-medium">
                  <span>{{ ag.route.origin_name }}</span>
                  <span class="text-muted-foreground">→</span>
                  <span>{{ ag.route.destination_name }}</span>
                </div>
              </td>

              <!-- Distance / Time -->
              <td class="px-5 py-4 text-xs font-mono text-muted-foreground">
                <div>{{ ag.route.distance_km }} km</div>
                <div class="text-[11px]">{{ formatTime(ag.route.estimated_time_minutes) }}</div>
              </td>

              <!-- General Route Status -->
              <td class="px-5 py-4">
                <span
                  class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
                  :class="
                    ag.route.is_active
                      ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                      : 'bg-destructive/10 text-destructive border border-destructive/20'
                  "
                >
                  {{ ag.route.is_active ? 'Activa' : 'Inactiva en catálogo' }}
                </span>
              </td>

              <!-- Switch Activa/Inactiva (CP-91) -->
              <td class="px-5 py-4">
                <div class="flex items-center gap-2">
                  <button
                    type="button"
                    class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary/20"
                    :class="[
                      ag.is_active && ag.route.is_active ? 'bg-primary' : 'bg-muted',
                      !ag.route.is_active ? 'opacity-50 cursor-not-allowed' : '',
                    ]"
                    :disabled="!ag.route.is_active"
                    :title="
                      !ag.route.is_active
                        ? 'No se puede activar mientras la ruta general esté inactiva en el catálogo'
                        : ag.is_active
                          ? 'Desactivar operación de ruta'
                          : 'Activar operación de ruta'
                    "
                    data-test="toggle-adopted-switch"
                    @click="handleToggleAdoptedStatus(ag.id, ag.is_active)"
                  >
                    <span
                      class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-background shadow-lg ring-0 transition duration-200 ease-in-out"
                      :class="ag.is_active && ag.route.is_active ? 'translate-x-5' : 'translate-x-0'"
                    />
                  </button>
                  <span class="text-xs font-medium" :class="ag.is_active ? 'text-foreground' : 'text-muted-foreground'">
                    {{ ag.is_active ? 'Operando' : 'Pausada' }}
                  </span>
                </div>
              </td>

              <!-- Detail Action -->
              <td class="px-5 py-4 text-right">
                <Button
                  variant="ghost"
                  size="icon"
                  class="h-8 w-8 rounded-lg text-muted-foreground hover:text-foreground cursor-pointer"
                  title="Ver detalle"
                  @click="openDetailDialog(ag.route_id)"
                >
                  <Eye class="w-4 h-4" />
                </Button>
              </td>
            </tr>

            <tr v-if="rutasStore.adoptedRoutes.length === 0">
              <td colspan="6" class="px-5 py-8 text-center text-sm text-muted-foreground">
                No ha adoptado ninguna ruta general. Haga clic en "Agregar ruta general" para incorporar rutas a su catálogo.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- SECTION 2: Cooperative Specific Routes (Mis Rutas) -->
    <section v-if="cooperativaId && !isCooperativeInactive" class="space-y-4 pt-6 border-t border-border" data-test="specific-routes-section">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <h2 class="text-base font-bold text-foreground flex items-center gap-2">
            <Building2 class="w-5 h-5 text-primary" />
            <span>Mis Rutas ({{ cooperativaLabel }})</span>
          </h2>
          <p class="text-xs text-muted-foreground">
            Rutas exclusivas registradas por su cooperativa que no forman parte del catálogo general.
          </p>
        </div>

        <Button
          class="rounded-xl gap-2 shadow-xs cursor-pointer"
          data-test="new-specific-route-btn"
          @click="openCreateSpecificRoute"
        >
          <Plus class="w-4 h-4" />
          <span>Nueva ruta propia</span>
        </Button>
      </div>

      <!-- Specific Routes Table -->
      <div class="overflow-x-auto rounded-xl border border-border bg-card shadow-xs">
        <table class="w-full text-left text-sm text-foreground">
          <thead class="border-b border-border bg-muted/40 text-xs font-semibold uppercase text-muted-foreground">
            <tr>
              <th scope="col" class="px-5 py-3.5">Ruta</th>
              <th scope="col" class="px-5 py-3.5">Trayecto</th>
              <th scope="col" class="px-5 py-3.5">Distancia / Tiempo</th>
              <th scope="col" class="px-5 py-3.5">Estado</th>
              <th scope="col" class="px-5 py-3.5 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            <tr
              v-for="sr in rutasStore.specificRoutes"
              :key="sr.id"
              class="transition-colors hover:bg-muted/20"
              :class="{ 'opacity-70 bg-muted/10': !sr.is_active }"
            >
              <!-- Name -->
              <td class="px-5 py-4 font-semibold text-foreground">
                <span class="truncate max-w-xs">{{ sr.name }}</span>
              </td>

              <!-- Origin -> Dest -->
              <td class="px-5 py-4 text-xs">
                <div class="flex items-center gap-1.5 font-medium">
                  <span>{{ sr.origin_name }}</span>
                  <span class="text-muted-foreground">→</span>
                  <span>{{ sr.destination_name }}</span>
                </div>
              </td>

              <!-- Distance / Time -->
              <td class="px-5 py-4 text-xs font-mono text-muted-foreground">
                <div>{{ sr.distance_km }} km</div>
                <div class="text-[11px]">{{ formatTime(sr.estimated_time_minutes) }}</div>
              </td>

              <!-- Status -->
              <td class="px-5 py-4">
                <span
                  class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold"
                  :class="
                    sr.is_active
                      ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                      : 'bg-muted text-muted-foreground border border-border'
                  "
                >
                  <CheckCircle2 v-if="sr.is_active" class="w-3 h-3" />
                  <XCircle v-else class="w-3 h-3" />
                  {{ sr.is_active ? 'Activa' : 'Inactiva' }}
                </span>
              </td>

              <!-- Actions -->
              <td class="px-5 py-4 text-right">
                <div class="flex items-center justify-end gap-1.5">
                  <Button
                    variant="ghost"
                    size="icon"
                    class="h-8 w-8 rounded-lg text-muted-foreground hover:text-foreground cursor-pointer"
                    title="Ver detalle"
                    @click="openDetailDialog(sr.id)"
                  >
                    <Eye class="w-4 h-4" />
                  </Button>

                  <Button
                    variant="ghost"
                    size="icon"
                    class="h-8 w-8 rounded-lg text-muted-foreground hover:text-foreground cursor-pointer"
                    title="Editar ruta propia"
                    data-test="edit-specific-route-btn"
                    @click="openEditSpecificRoute(sr)"
                  >
                    <Pencil class="w-4 h-4" />
                  </Button>

                  <Button
                    variant="ghost"
                    size="icon"
                    class="h-8 w-8 rounded-lg cursor-pointer"
                    :class="
                      sr.is_active
                        ? 'text-muted-foreground hover:text-destructive hover:bg-destructive/10'
                        : 'text-emerald-600 hover:bg-emerald-500/10'
                    "
                    :title="sr.is_active ? 'Desactivar ruta propia' : 'Activar ruta propia'"
                    data-test="toggle-specific-status-btn"
                    @click="handleToggleSpecificStatusClick(sr)"
                  >
                    <Power class="w-4 h-4" />
                  </Button>
                </div>
              </td>
            </tr>

            <tr v-if="rutasStore.specificRoutes.length === 0">
              <td colspan="5" class="px-5 py-8 text-center text-sm text-muted-foreground">
                No tiene rutas específicas creadas. Haga clic en "Nueva ruta propia" para registrar una.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Dialogs -->
    <GeneralRoutesPickerModal
      :is-open="isPickerOpen"
      :cooperativa-id="cooperativaId"
      @close="isPickerOpen = false"
      @adopted="() => loadData()"
    />

    <RouteFormDialog
      :is-open="isFormOpen"
      :route="selectedRouteDetail"
      :cooperativa-id="cooperativaId"
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

    <!-- Specific Route Deactivation Confirmation Dialog -->
    <div
      v-if="isConfirmDeactivateOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in-50 duration-200"
      data-test="deactivate-specific-dialog"
    >
      <div class="relative w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-2xl space-y-4">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400 shrink-0">
            <AlertTriangle class="w-5 h-5" />
          </div>
          <div>
            <h3 class="text-base font-bold text-foreground">¿Desactivar ruta propia?</h3>
            <p class="text-xs text-muted-foreground">{{ routeToToggle?.name }}</p>
          </div>
        </div>

        <p class="text-sm text-foreground/80 leading-relaxed">
          Al desactivar esta ruta, no se podrán programar nuevos turnos para ella. Los viajes ya programados o con
          boletos reservados serán notificados a los usuarios.
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
            @click="confirmToggleSpecificStatus(false)"
          >
            <Loader2 v-if="isTogglingStatus" class="w-4 h-4 animate-spin" />
            <span>Confirmar desactivación</span>
          </Button>
        </div>
      </div>
    </div>

    <!-- Specific Route Activation Confirmation Dialog -->
    <div
      v-if="isConfirmActivateOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in-50 duration-200"
      data-test="activate-specific-dialog"
    >
      <div class="relative w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-2xl space-y-4">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 shrink-0">
            <CheckCircle2 class="w-5 h-5" />
          </div>
          <div>
            <h3 class="text-base font-bold text-foreground">¿Reactivar ruta propia?</h3>
            <p class="text-xs text-muted-foreground">{{ routeToToggle?.name }}</p>
          </div>
        </div>

        <p class="text-sm text-foreground/80 leading-relaxed">
          Al reactivar esta ruta, volverá a estar habilitada para la operación de la cooperativa y la asignación de turnos.
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
            data-test="confirm-activate-specific-btn"
            @click="confirmToggleSpecificStatus(true)"
          >
            <Loader2 v-if="isTogglingStatus" class="w-4 h-4 animate-spin" />
            <span>Confirmar reactivación</span>
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
