<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { Check, Loader2, Search, Users, X } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { useCooperativaAdministrators } from '@/composables/useCooperativaAdministrators'
import type { EligibleAdmin } from '@/services/cooperativas.service'

const props = defineProps<{
  cooperativaId?: number | null
  isOpen: boolean
  initialSelectedUserIds?: number[]
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved', payload?: { userIds: number[]; users: EligibleAdmin[] }): void
}>()

const {
  eligibleUsers,
  selectedUserIds,
  searchQuery,
  isLoading,
  isSaving,
  error,
  loadEligibleUsers,
  onSearchEligibleInput,
  toggleUserSelection,
  isSelectionDisabled,
  saveAdministrators,
} = useCooperativaAdministrators()

onMounted(() => {
  if (props.isOpen) {
    if (props.initialSelectedUserIds) {
      selectedUserIds.value = [...props.initialSelectedUserIds]
    }
    loadEligibleUsers(props.cooperativaId ?? 0)
  }
})

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      if (props.initialSelectedUserIds) {
        selectedUserIds.value = [...props.initialSelectedUserIds]
      }
      loadEligibleUsers(props.cooperativaId ?? 0)
    }
  },
)

async function handleSave() {
  if (props.cooperativaId) {
    const success = await saveAdministrators(props.cooperativaId)
    if (success) {
      emit('saved')
      emit('close')
    }
  } else {
    const selectedUsers = eligibleUsers.value.filter((u) => selectedUserIds.value.includes(u.id))
    emit('saved', { userIds: [...selectedUserIds.value], users: selectedUsers })
    emit('close')
  }
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4"
    data-testid="administrators-modal"
  >
    <div
      class="flex max-h-[90vh] w-full max-w-lg flex-col rounded-xl border border-border bg-card p-6 shadow-xl"
    >
      <!-- Header -->
      <div class="flex items-center justify-between border-b border-border pb-4">
        <div class="flex items-center gap-2.5">
          <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Users class="h-5 w-5" />
          </div>
          <div>
            <h3 class="text-base font-semibold text-foreground">Gestionar Administradores</h3>
            <p class="text-xs text-muted-foreground">
              Selecciona hasta 3 usuarios con rol Administrador de cooperativa
            </p>
          </div>
        </div>
        <Button variant="ghost" size="icon" class="h-8 w-8 rounded-full" @click="emit('close')">
          <X class="h-4 w-4" />
        </Button>
      </div>

      <!-- Counter Badge & Search -->
      <div class="mt-4 space-y-3">
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-foreground">
            Usuarios disponibles
          </span>
          <span
            class="rounded-full px-2.5 py-0.5 text-xs font-semibold"
            :class="
              selectedUserIds.length >= 3
                ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400'
                : 'bg-primary/10 text-primary'
            "
          >
            {{ selectedUserIds.length }} / 3 seleccionados
          </span>
        </div>

        <div class="relative">
          <Search class="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Buscar por nombre, apellido, correo o documento..."
            class="w-full rounded-lg border border-input bg-background pl-9 pr-4 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            @input="onSearchEligibleInput(cooperativaId ?? 0, searchQuery)"
          />
        </div>
      </div>

      <!-- Error alert -->
      <div
        v-if="error"
        class="mt-3 rounded-lg border border-destructive/20 bg-destructive/10 p-3 text-xs text-destructive"
      >
        {{ error }}
      </div>

      <!-- Users List -->
      <div class="mt-4 flex-1 overflow-y-auto space-y-2 pr-1 max-h-72 min-h-[160px]">
        <div v-if="isLoading" class="flex h-32 items-center justify-center text-muted-foreground">
          <Loader2 class="h-6 w-6 animate-spin mr-2" />
          <span class="text-xs">Cargando usuarios...</span>
        </div>

        <div
          v-else-if="eligibleUsers.length === 0"
          class="flex h-32 flex-col items-center justify-center text-center text-xs text-muted-foreground"
        >
          <Users class="h-8 w-8 text-muted-foreground/50 mb-1" />
          <p>No se encontraron usuarios elegibles.</p>
          <p class="text-[11px]">Deben estar activos, con rol Administrador de cooperativa y sin otra cooperativa.</p>
        </div>

        <div
          v-else
          v-for="user in eligibleUsers"
          :key="user.id"
          class="flex items-center justify-between rounded-lg border p-3 transition-colors"
          :class="[
            selectedUserIds.includes(user.id)
              ? 'border-primary/50 bg-primary/5'
              : 'border-border bg-card hover:bg-muted/30',
            isSelectionDisabled(user.id) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
          ]"
          :data-testid="`user-item-${user.id}`"
          @click="!isSelectionDisabled(user.id) && toggleUserSelection(user.id)"
        >
          <div class="flex items-center gap-3">
            <div
              class="flex h-5 w-5 shrink-0 items-center justify-center rounded border transition-colors"
              :class="
                selectedUserIds.includes(user.id)
                  ? 'border-primary bg-primary text-primary-foreground'
                  : 'border-input bg-background'
              "
            >
              <Check v-if="selectedUserIds.includes(user.id)" class="h-3.5 w-3.5" />
            </div>

            <div>
              <p class="text-sm font-medium text-foreground leading-tight">
                {{ user.first_name }} {{ user.last_name }}
              </p>
              <p class="text-xs text-muted-foreground">
                {{ user.email }} • Doc: {{ user.document_number }}
              </p>
            </div>
          </div>

          <span
            v-if="user.is_already_assigned"
            class="text-[11px] font-medium text-emerald-600 dark:text-emerald-400"
          >
            Asignado
          </span>
        </div>
      </div>

      <!-- Footer Buttons -->
      <div class="mt-6 flex items-center justify-end gap-3 border-t border-border pt-4">
        <Button variant="outline" size="sm" @click="emit('close')">
          Cancelar
        </Button>
        <Button
          size="sm"
          :disabled="isSaving"
          class="gap-1.5"
          @click="handleSave"
        >
          <Loader2 v-if="isSaving" class="h-4 w-4 animate-spin" />
          Guardar personal
        </Button>
      </div>
    </div>
  </div>
</template>
