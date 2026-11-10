<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Loader2,
  Search,
  SlidersHorizontal,
  UserCheck,
  UserX,
  Users,
  X,
} from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/auth.store'
import { useUsersStore } from '@/stores/users.store'
import type { User, UserRole } from '@/services/auth.service'

const authStore = useAuthStore()
const usersStore = useUsersStore()

// Role Modal State
const isRoleModalOpen = ref(false)
const selectedUserForRoles = ref<User | null>(null)
const roleSelections = ref<Record<UserRole, boolean>>({
  ADMIN_GENERAL: false,
  ADMIN_COOPERATIVA: false,
  SECRETARIA_COOPERATIVA: false,
  PASAJERO: true,
})
const isSavingRoles = ref(false)

// Status Modal State
const isStatusModalOpen = ref(false)
const selectedUserForStatus = ref<User | null>(null)
const isUpdatingStatus = ref(false)

const ALL_ROLES_LIST: { id: UserRole; label: string; desc: string }[] = [
  {
    id: 'ADMIN_GENERAL',
    label: 'Administrador General',
    desc: 'Gestión total: cooperativas, rutas, precios generales y usuarios.',
  },
  {
    id: 'ADMIN_COOPERATIVA',
    label: 'Administrador de Cooperativa',
    desc: 'Gestión de buses, turnos, rutas de cooperativa y tarifas.',
  },
  {
    id: 'SECRETARIA_COOPERATIVA',
    label: 'Secretaria de Cooperativa',
    desc: 'Atención a ventanilla y gestión de reservas.',
  },
  {
    id: 'PASAJERO',
    label: 'Pasajero (Rol Base)',
    desc: 'Rol permanente del sistema. Consulta y reserva de pasajes.',
  },
]

onMounted(() => {
  usersStore.fetchUsers()
})

function formatDate(isoDate: string): string {
  try {
    const d = new Date(isoDate)
    return d.toLocaleDateString('es-EC', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    })
  } catch {
    return isoDate
  }
}

function isCurrentUser(user: User): boolean {
  return authStore.user?.id === user.id
}

// Role Modal Handlers
function openRoleModal(user: User) {
  if (isCurrentUser(user)) return
  selectedUserForRoles.value = user

  roleSelections.value = {
    ADMIN_GENERAL: user.roles?.includes('ADMIN_GENERAL') ?? false,
    ADMIN_COOPERATIVA: user.roles?.includes('ADMIN_COOPERATIVA') ?? false,
    SECRETARIA_COOPERATIVA:
      user.roles?.includes('SECRETARIA_COOPERATIVA') ?? false,
    PASAJERO: true, // Always locked and true
  }

  isRoleModalOpen.value = true
}

function closeRoleModal() {
  isRoleModalOpen.value = false
  selectedUserForRoles.value = null
}

async function handleSaveRoles() {
  if (!selectedUserForRoles.value) return
  isSavingRoles.value = true

  const updatedRoles: UserRole[] = []
  if (roleSelections.value.ADMIN_GENERAL) updatedRoles.push('ADMIN_GENERAL')
  if (roleSelections.value.ADMIN_COOPERATIVA) updatedRoles.push('ADMIN_COOPERATIVA')
  if (roleSelections.value.SECRETARIA_COOPERATIVA) updatedRoles.push('SECRETARIA_COOPERATIVA')
  // PASAJERO is permanently included
  if (!updatedRoles.includes('PASAJERO')) {
    updatedRoles.push('PASAJERO')
  }

  const success = await usersStore.changeRoles(
    selectedUserForRoles.value.id,
    updatedRoles,
  )
  isSavingRoles.value = false
  if (success) {
    closeRoleModal()
  }
}

// Status Modal Handlers
function openStatusModal(user: User) {
  if (isCurrentUser(user)) return
  selectedUserForStatus.value = user
  isStatusModalOpen.value = true
}

function closeStatusModal() {
  isStatusModalOpen.value = false
  selectedUserForStatus.value = null
}

async function handleConfirmStatusChange() {
  if (!selectedUserForStatus.value) return
  isUpdatingStatus.value = true

  const targetState = !selectedUserForStatus.value.is_active
  const success = await usersStore.changeStatus(
    selectedUserForStatus.value.id,
    targetState,
  )
  isUpdatingStatus.value = false
  if (success) {
    closeStatusModal()
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
          <Users class="w-6 h-6 text-primary" />
          <span>Gestión de Usuarios</span>
        </h2>
        <p class="text-sm text-muted-foreground mt-1">
          Administra los roles, permisos y estados de acceso de los usuarios registrados en la plataforma.
        </p>
      </div>

      <!-- Search Input -->
      <div class="relative w-full sm:w-72">
        <Search class="w-4 h-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          :value="usersStore.searchQuery"
          type="text"
          placeholder="Buscar por nombre o correo..."
          class="w-full pl-9 pr-4 py-2 rounded-xl bg-card border border-border text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all placeholder:text-muted-foreground"
          @input="usersStore.onSearchInput(($event.target as HTMLInputElement).value)"
        />
      </div>
    </div>

    <!-- Alert Feedback -->
    <div
      v-if="usersStore.error"
      class="p-4 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-sm flex items-center justify-between gap-3 animate-in fade-in"
    >
      <div class="flex items-center gap-2">
        <AlertCircle class="w-5 h-5 shrink-0" />
        <span>{{ usersStore.error }}</span>
      </div>
      <button
        class="text-destructive/80 hover:text-destructive cursor-pointer"
        @click="usersStore.clearMessages"
      >
        <X class="w-4 h-4" />
      </button>
    </div>

    <div
      v-if="usersStore.successMessage"
      class="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-sm flex items-center justify-between gap-3 animate-in fade-in"
    >
      <div class="flex items-center gap-2">
        <CheckCircle2 class="w-5 h-5 shrink-0" />
        <span>{{ usersStore.successMessage }}</span>
      </div>
      <button
        class="text-emerald-600/80 hover:text-emerald-600 cursor-pointer"
        @click="usersStore.clearMessages"
      >
        <X class="w-4 h-4" />
      </button>
    </div>

    <!-- Users Table Card -->
    <div class="rounded-2xl border border-border bg-card shadow-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="border-b border-border bg-muted/40 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            <tr>
              <th scope="col" class="py-3.5 px-4 sm:px-6">Nombre completo</th>
              <th scope="col" class="py-3.5 px-4">Correo electrónico</th>
              <th scope="col" class="py-3.5 px-4">Rol(es)</th>
              <th scope="col" class="py-3.5 px-4">Estado</th>
              <th scope="col" class="py-3.5 px-4">Registro</th>
              <th scope="col" class="py-3.5 px-4 sm:px-6 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border/60">
            <!-- Loading State -->
            <tr v-if="usersStore.isLoading && usersStore.users.length === 0">
              <td colspan="6" class="py-12 text-center text-muted-foreground">
                <Loader2 class="w-6 h-6 animate-spin mx-auto text-primary mb-2" />
                <span>Cargando usuarios...</span>
              </td>
            </tr>

            <!-- Empty State -->
            <tr v-else-if="usersStore.users.length === 0">
              <td colspan="6" class="py-12 text-center text-muted-foreground">
                <Users class="w-8 h-8 mx-auto text-muted-foreground/40 mb-2" />
                <p class="font-medium text-foreground">No se encontraron usuarios</p>
                <p class="text-xs text-muted-foreground mt-0.5">
                  Intenta modificar los términos de tu búsqueda.
                </p>
              </td>
            </tr>

            <!-- User Rows -->
            <tr
              v-for="user in usersStore.users"
              v-else
              :key="user.id"
              class="hover:bg-muted/30 transition-colors"
              :class="{ 'bg-primary/5': isCurrentUser(user) }"
            >
              <!-- Name & Doc -->
              <td class="py-3.5 px-4 sm:px-6">
                <div class="font-semibold text-foreground">
                  {{ user.first_name }} {{ user.last_name }}
                  <span
                    v-if="isCurrentUser(user)"
                    class="ml-2 inline-block px-2 py-0.5 rounded text-[10px] font-semibold bg-primary text-primary-foreground"
                  >
                    Tú
                  </span>
                </div>
                <div class="text-xs text-muted-foreground">
                  {{ user.document_type }}: {{ user.document_number }}
                </div>
              </td>

              <!-- Email -->
              <td class="py-3.5 px-4 text-muted-foreground truncate max-w-xs">
                {{ user.email }}
              </td>

              <!-- Roles Badges -->
              <td class="py-3.5 px-4">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="r in user.roles"
                    :key="r"
                    class="inline-block px-2 py-0.5 rounded-md text-[11px] font-semibold bg-primary/10 text-primary border border-primary/20"
                  >
                    {{ r }}
                  </span>
                </div>
              </td>

              <!-- Status Badge -->
              <td class="py-3.5 px-4">
                <span
                  v-if="user.is_active"
                  class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20"
                >
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  Activo
                </span>
                <span
                  v-else
                  class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-destructive/10 text-destructive border border-destructive/20"
                >
                  <span class="w-1.5 h-1.5 rounded-full bg-destructive"></span>
                  Inactivo
                </span>
              </td>

              <!-- Registration Date -->
              <td class="py-3.5 px-4 text-xs text-muted-foreground whitespace-nowrap">
                {{ formatDate(user.created_at) }}
              </td>

              <!-- Action Buttons -->
              <td class="py-3.5 px-4 sm:px-6 text-right whitespace-nowrap">
                <div class="inline-flex items-center justify-end gap-2">
                  <!-- Asignar Rol -->
                  <Button
                    variant="outline"
                    size="sm"
                    class="rounded-xl text-xs gap-1.5 cursor-pointer"
                    :disabled="isCurrentUser(user)"
                    :title="isCurrentUser(user) ? 'No puedes modificar tus propios roles' : 'Asignar o revocar roles'"
                    @click="openRoleModal(user)"
                  >
                    <SlidersHorizontal class="w-3.5 h-3.5" />
                    <span>Asignar rol</span>
                  </Button>

                  <!-- Dar de baja / Habilitar -->
                  <Button
                    v-if="user.is_active"
                    variant="destructive"
                    size="sm"
                    class="rounded-xl text-xs gap-1.5 cursor-pointer"
                    :disabled="isCurrentUser(user)"
                    :title="isCurrentUser(user) ? 'No puedes darte de baja a ti mismo' : 'Dar de baja al usuario'"
                    @click="openStatusModal(user)"
                  >
                    <UserX class="w-3.5 h-3.5" />
                    <span>Dar de baja</span>
                  </Button>

                  <Button
                    v-else
                    variant="outline"
                    size="sm"
                    class="rounded-xl text-xs gap-1.5 border-emerald-500/30 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-500/10 cursor-pointer"
                    :disabled="isCurrentUser(user)"
                    @click="openStatusModal(user)"
                  >
                    <UserCheck class="w-3.5 h-3.5" />
                    <span>Habilitar</span>
                  </Button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination Footer -->
      <div class="border-t border-border px-4 sm:px-6 py-3 flex items-center justify-between text-xs text-muted-foreground bg-muted/20">
        <div>
          Mostrando página <span class="font-semibold text-foreground">{{ usersStore.page }}</span> de
          <span class="font-semibold text-foreground">{{ usersStore.pages || 1 }}</span>
          ({{ usersStore.total }} usuario{{ usersStore.total === 1 ? '' : 's' }} en total)
        </div>

        <div class="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            class="rounded-xl h-8 px-2.5 cursor-pointer"
            :disabled="usersStore.page <= 1 || usersStore.isLoading"
            @click="usersStore.setPage(usersStore.page - 1)"
          >
            <ChevronLeft class="w-4 h-4" />
            <span class="sr-only sm:not-sr-only sm:ml-1">Anterior</span>
          </Button>

          <Button
            variant="outline"
            size="sm"
            class="rounded-xl h-8 px-2.5 cursor-pointer"
            :disabled="usersStore.page >= usersStore.pages || usersStore.isLoading"
            @click="usersStore.setPage(usersStore.page + 1)"
          >
            <span class="sr-only sm:not-sr-only sm:mr-1">Siguiente</span>
            <ChevronRight class="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>

    <!-- Modal: Asignación de Roles -->
    <Teleport to="body">
      <div
        v-if="isRoleModalOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-xs transition-opacity animate-in fade-in"
        role="dialog"
        aria-modal="true"
        aria-labelledby="role-modal-title"
      >
        <div class="w-full max-w-lg bg-card text-card-foreground rounded-2xl border border-border shadow-2xl p-6 space-y-5 animate-in zoom-in-95">
          <div class="flex items-start justify-between">
            <div class="space-y-1">
              <h3 id="role-modal-title" class="text-lg font-bold text-foreground">
                Asignación de Roles
              </h3>
              <p class="text-xs text-muted-foreground">
                Usuario: <span class="font-semibold text-foreground">{{ selectedUserForRoles?.first_name }} {{ selectedUserForRoles?.last_name }}</span> ({{ selectedUserForRoles?.email }})
              </p>
            </div>
            <button
              class="text-muted-foreground hover:text-foreground cursor-pointer rounded-lg p-1"
              @click="closeRoleModal"
            >
              <X class="w-5 h-5" />
            </button>
          </div>

          <div class="space-y-3 py-2">
            <div
              v-for="roleItem in ALL_ROLES_LIST"
              :key="roleItem.id"
              class="flex items-start gap-3 p-3 rounded-xl border border-border transition-colors"
              :class="[
                roleItem.id === 'PASAJERO'
                  ? 'bg-muted/40 cursor-not-allowed opacity-90'
                  : 'bg-card hover:bg-muted/30 cursor-pointer',
              ]"
            >
              <input
                :id="`role-checkbox-${roleItem.id}`"
                v-model="roleSelections[roleItem.id]"
                type="checkbox"
                class="mt-1 h-4 w-4 rounded-md border-border text-primary focus:ring-primary/20 accent-primary"
                :disabled="roleItem.id === 'PASAJERO'"
              />
              <label
                :for="`role-checkbox-${roleItem.id}`"
                class="text-sm select-none"
                :class="roleItem.id === 'PASAJERO' ? 'cursor-not-allowed' : 'cursor-pointer'"
              >
                <div class="font-semibold text-foreground flex items-center gap-2">
                  <span>{{ roleItem.label }}</span>
                  <span
                    v-if="roleItem.id === 'PASAJERO'"
                    class="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground border border-border"
                  >
                    Bloqueado
                  </span>
                </div>
                <div class="text-xs text-muted-foreground mt-0.5">
                  {{ roleItem.desc }}
                </div>
              </label>
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 pt-3 border-t border-border">
            <Button
              variant="outline"
              class="rounded-xl"
              :disabled="isSavingRoles"
              @click="closeRoleModal"
            >
              Cancelar
            </Button>

            <Button
              variant="default"
              class="rounded-xl gap-2 shadow-xs cursor-pointer"
              :disabled="isSavingRoles"
              @click="handleSaveRoles"
            >
              <Loader2 v-if="isSavingRoles" class="w-4 h-4 animate-spin" />
              <span>{{ isSavingRoles ? 'Guardando...' : 'Guardar cambios' }}</span>
            </Button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Modal: Confirmación de Baja / Rehabilitación -->
    <Teleport to="body">
      <div
        v-if="isStatusModalOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-xs transition-opacity animate-in fade-in"
        role="dialog"
        aria-modal="true"
        aria-labelledby="status-modal-title"
      >
        <div class="w-full max-w-md bg-card text-card-foreground rounded-2xl border border-border shadow-2xl p-6 space-y-5 animate-in zoom-in-95">
          <div class="flex items-start gap-4">
            <div
              class="w-11 h-11 rounded-xl flex items-center justify-center shrink-0"
              :class="selectedUserForStatus?.is_active ? 'bg-destructive/15 text-destructive' : 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'"
            >
              <AlertTriangle v-if="selectedUserForStatus?.is_active" class="w-6 h-6" />
              <UserCheck v-else class="w-6 h-6" />
            </div>

            <div class="space-y-1.5">
              <h3 id="status-modal-title" class="text-lg font-bold text-foreground leading-snug">
                {{ selectedUserForStatus?.is_active ? '¿Dar de baja a este usuario?' : '¿Habilitar cuenta de usuario?' }}
              </h3>
              <p class="text-sm text-muted-foreground leading-relaxed">
                <template v-if="selectedUserForStatus?.is_active">
                  La cuenta de <span class="font-semibold text-foreground">{{ selectedUserForStatus?.first_name }} {{ selectedUserForStatus?.last_name }}</span> pasará a estado inactivo mediante borrado lógico. No podrá iniciar sesión hasta ser rehabilitada.
                </template>
                <template v-else>
                  La cuenta de <span class="font-semibold text-foreground">{{ selectedUserForStatus?.first_name }} {{ selectedUserForStatus?.last_name }}</span> se reactivará y recuperará de inmediato su capacidad para iniciar sesión.
                </template>
              </p>
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 pt-2">
            <Button
              variant="outline"
              class="rounded-xl"
              :disabled="isUpdatingStatus"
              @click="closeStatusModal"
            >
              Cancelar
            </Button>

            <Button
              :variant="selectedUserForStatus?.is_active ? 'destructive' : 'default'"
              class="rounded-xl gap-2 shadow-xs cursor-pointer"
              :disabled="isUpdatingStatus"
              @click="handleConfirmStatusChange"
            >
              <Loader2 v-if="isUpdatingStatus" class="w-4 h-4 animate-spin" />
              <span>{{ isUpdatingStatus ? 'Procesando...' : (selectedUserForStatus?.is_active ? 'Confirmar baja' : 'Confirmar activación') }}</span>
            </Button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
