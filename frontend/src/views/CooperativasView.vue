<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  AlertCircle,
  Building2,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  LayoutGrid,
  Loader2,
  Plus,
  Search,
  Table as TableIcon,
} from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { useCooperativasStore } from '@/stores/cooperativas.store'
import CooperativaCard from '@/components/cooperativas/CooperativaCard.vue'
import CooperativaTable from '@/components/cooperativas/CooperativaTable.vue'
import CooperativaFormDialog from '@/components/cooperativas/CooperativaFormDialog.vue'
import {
  CooperativasService,
  type Cooperativa,
  type CooperativaCreatePayload,
  type CooperativaUpdatePayload,
} from '@/services/cooperativas.service'
import { setCooperativaInactivaHandler } from '@/services/api-client'

const router = useRouter()
const store = useCooperativasStore()

const isFormDialogOpen = ref(false)
const selectedCoopForEdit = ref<Cooperativa | null>(null)
const isStatusConfirmOpen = ref(false)
const coopForStatusToggle = ref<Cooperativa | null>(null)
const isSubmitting = ref(false)

onMounted(() => {
  store.fetchCooperativas()

  // CP-60: Redirigir si se detecta que una cooperativa fue desactivada en otra sesión
  setCooperativaInactivaHandler((message: string) => {
    isFormDialogOpen.value = false
    router.push({ name: 'dashboard' })
    alert(message)
  })
})

function openCreateDialog() {
  selectedCoopForEdit.value = null
  isFormDialogOpen.value = true
}

function openEditDialog(coop: Cooperativa) {
  selectedCoopForEdit.value = coop
  isFormDialogOpen.value = true
}

function openStatusConfirm(coop: Cooperativa) {
  coopForStatusToggle.value = coop
  isStatusConfirmOpen.value = true
}

async function handleConfirmStatusToggle() {
  if (!coopForStatusToggle.value) return
  const coop = coopForStatusToggle.value
  await store.updateEstado(coop.id, !coop.is_active)
  isStatusConfirmOpen.value = false
  coopForStatusToggle.value = null
}

async function handleFormSubmit(payload: {
  data: CooperativaCreatePayload | CooperativaUpdatePayload
  file: File | null
  id?: number
  adminUserIds?: number[]
}) {
  isSubmitting.value = true
  try {
    let result: Cooperativa | null = null

    if (payload.id) {
      // Edit
      result = await store.updateCooperativa(payload.id, payload.data as CooperativaUpdatePayload)
      if (result && payload.file) {
        await store.uploadLogo(payload.id, payload.file)
      }
    } else {
      // Create
      result = await store.createCooperativa(payload.data as CooperativaCreatePayload)
      if (result) {
        if (payload.adminUserIds && payload.adminUserIds.length > 0) {
          try {
            await CooperativasService.updateAdministradores(result.id, payload.adminUserIds)
          } catch {
            // Se mantiene la cooperativa creada
          }
        }
        if (payload.file) {
          await store.uploadLogo(result.id, payload.file)
        }
        await store.fetchCooperativas()
      }
    }
  } finally {
    isSubmitting.value = false
    // El modal se cierra automáticamente tanto si finaliza con éxito o si ocurre un error,
    // permitiendo al usuario ver el mensaje de confirmación o alerta en la pantalla principal.
    isFormDialogOpen.value = false
    selectedCoopForEdit.value = null
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
          <Building2 class="h-6 w-6 text-primary" />
          Cooperativas
        </h1>
        <p class="text-sm text-muted-foreground">
          Gestión de cooperativas afiliadas al terminal terrestre.
        </p>
      </div>

      <div class="flex items-center gap-3">
        <!-- View mode toggle (CP-54) -->
        <div class="flex items-center rounded-lg border border-border bg-card p-1">
          <Button
            variant="ghost"
            size="sm"
            class="h-8 w-8 p-0"
            :class="{ 'bg-muted text-foreground': store.viewMode === 'cards' }"
            title="Vista de Tarjetas"
            @click="store.setViewMode('cards')"
            data-testid="view-cards-button"
          >
            <LayoutGrid class="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            class="h-8 w-8 p-0"
            :class="{ 'bg-muted text-foreground': store.viewMode === 'table' }"
            title="Vista de Tabla"
            @click="store.setViewMode('table')"
            data-testid="view-table-button"
          >
            <TableIcon class="h-4 w-4" />
          </Button>
        </div>

        <Button class="gap-2" @click="openCreateDialog" data-testid="new-cooperativa-button">
          <Plus class="h-4 w-4" />
          Nueva Cooperativa
        </Button>
      </div>
    </div>

    <!-- Alert Messages -->
    <div
      v-if="store.error"
      class="flex items-center gap-2 rounded-lg border border-destructive/20 bg-destructive/10 p-4 text-sm text-destructive"
      data-testid="coop-error-alert"
    >
      <AlertCircle class="h-4 w-4 shrink-0" />
      <span>{{ store.error }}</span>
    </div>

    <div
      v-if="store.successMessage"
      class="flex items-center gap-2 rounded-lg border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-600 dark:text-emerald-400"
      data-testid="coop-success-alert"
    >
      <CheckCircle2 class="h-4 w-4 shrink-0" />
      <span>{{ store.successMessage }}</span>
    </div>

    <!-- Search & Filter Bar -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div class="relative flex-1 max-w-md">
        <Search class="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
        <input
          type="text"
          v-model="store.searchQuery"
          placeholder="Buscar cooperativa por nombre o RUC..."
          class="w-full rounded-lg border border-input bg-card pl-9 pr-4 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          @input="store.onSearchInput(store.searchQuery)"
          data-testid="search-cooperativa-input"
        />
      </div>

      <!-- Estado Filter -->
      <div class="flex items-center gap-2 text-xs">
        <span class="text-muted-foreground">Estado:</span>
        <button
          type="button"
          class="px-2.5 py-1 rounded-md transition-colors"
          :class="store.statusFilter === undefined ? 'bg-primary text-primary-foreground font-medium' : 'text-muted-foreground hover:bg-muted'"
          @click="store.statusFilter = undefined; store.fetchCooperativas()"
        >
          Todas
        </button>
        <button
          type="button"
          class="px-2.5 py-1 rounded-md transition-colors"
          :class="store.statusFilter === true ? 'bg-primary text-primary-foreground font-medium' : 'text-muted-foreground hover:bg-muted'"
          @click="store.statusFilter = true; store.fetchCooperativas()"
        >
          Activas
        </button>
        <button
          type="button"
          class="px-2.5 py-1 rounded-md transition-colors"
          :class="store.statusFilter === false ? 'bg-primary text-primary-foreground font-medium' : 'text-muted-foreground hover:bg-muted'"
          @click="store.statusFilter = false; store.fetchCooperativas()"
        >
          Desactivadas
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="store.isLoading" class="flex h-64 items-center justify-center text-muted-foreground">
      <Loader2 class="h-8 w-8 animate-spin mr-2" />
      <span>Cargando cooperativas...</span>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="store.cooperativas.length === 0"
      class="flex h-64 flex-col items-center justify-center rounded-xl border border-dashed border-border bg-card p-8 text-center"
    >
      <Building2 class="h-12 w-12 text-muted-foreground/40 mb-3" />
      <h3 class="text-base font-medium text-foreground">No se encontraron cooperativas</h3>
      <p class="text-xs text-muted-foreground mt-1 max-w-sm">
        No hay cooperativas registradas o no coinciden con el criterio de búsqueda.
      </p>
      <Button variant="outline" size="sm" class="mt-4 gap-1.5" @click="openCreateDialog">
        <Plus class="h-4 w-4" />
        Registrar la primera
      </Button>
    </div>

    <!-- Content: Cards or Table (CP-54) -->
    <div v-else>
      <!-- Cards View -->
      <div
        v-if="store.viewMode === 'cards'"
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"
        data-testid="cards-container"
      >
        <CooperativaCard
          v-for="coop in store.cooperativas"
          :key="coop.id"
          :cooperativa="coop"
          @edit="openEditDialog"
          @toggle-status="openStatusConfirm"
        />
      </div>

      <!-- Table View -->
      <div v-else data-testid="table-container">
        <CooperativaTable
          :cooperativas="store.cooperativas"
          @edit="openEditDialog"
          @toggle-status="openStatusConfirm"
        />
      </div>

      <!-- Pagination -->
      <div v-if="store.totalPages > 1" class="mt-6 flex items-center justify-between border-t border-border pt-4">
        <p class="text-xs text-muted-foreground">
          Página {{ store.page }} de {{ store.totalPages }} (Total: {{ store.total }} cooperativas)
        </p>
        <div class="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            :disabled="store.page <= 1"
            @click="store.page--; store.fetchCooperativas()"
          >
            <ChevronLeft class="h-4 w-4 mr-1" />
            Anterior
          </Button>
          <Button
            variant="outline"
            size="sm"
            :disabled="store.page >= store.totalPages"
            @click="store.page++; store.fetchCooperativas()"
          >
            Siguiente
            <ChevronRight class="h-4 w-4 ml-1" />
          </Button>
        </div>
      </div>
    </div>

    <!-- Create / Edit Dialog -->
    <CooperativaFormDialog
      :is-open="isFormDialogOpen"
      :cooperativa="selectedCoopForEdit"
      :is-submitting="isSubmitting"
      @close="isFormDialogOpen = false"
      @submit="handleFormSubmit"
      @refresh="store.fetchCooperativas"
    />

    <!-- Status Change Confirmation Dialog (CP-58, CP-59) -->
    <div
      v-if="isStatusConfirmOpen && coopForStatusToggle"
      class="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4"
      data-testid="status-confirm-modal"
    >
      <div class="w-full max-w-md rounded-xl border border-border bg-card p-6 shadow-xl space-y-4">
        <h3 class="text-base font-semibold text-foreground">
          {{ coopForStatusToggle.is_active ? 'Desactivar Cooperativa' : 'Activar Cooperativa' }}
        </h3>
        <p class="text-xs text-muted-foreground">
          ¿Estás seguro de que deseas {{ coopForStatusToggle.is_active ? 'desactivar' : 'activar' }} la cooperativa
          <span class="font-semibold text-foreground">"{{ coopForStatusToggle.name }}"</span>?
          <span v-if="coopForStatusToggle.is_active" class="block mt-1 text-destructive">
            Una cooperativa desactivada no podrá asignar turnos ni operar en el terminal.
          </span>
        </p>
        <div class="flex items-center justify-end gap-3 pt-2">
          <Button variant="outline" size="sm" @click="isStatusConfirmOpen = false">
            Cancelar
          </Button>
          <Button
            size="sm"
            :variant="coopForStatusToggle.is_active ? 'destructive' : 'default'"
            @click="handleConfirmStatusToggle"
            data-testid="confirm-status-button"
          >
            {{ coopForStatusToggle.is_active ? 'Sí, desactivar' : 'Sí, activar' }}
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
