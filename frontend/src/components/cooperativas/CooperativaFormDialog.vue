<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import {
  Building2,
  FileImage,
  Loader2,
  Upload,
  UserMinus,
  Users,
  X,
} from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { useCooperativaForm } from '@/composables/useCooperativaForm'
import { useCooperativaAdministrators } from '@/composables/useCooperativaAdministrators'
import CooperativaAdministratorsModal from './CooperativaAdministratorsModal.vue'
import {
  resolveLogoUrl,
  type Cooperativa,
  type CooperativaCreatePayload,
  type CooperativaUpdatePayload,
  type EligibleAdmin,
} from '@/services/cooperativas.service'

const props = defineProps<{
  isOpen: boolean
  cooperativa: Cooperativa | null
  isSubmitting?: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (
    e: 'submit',
    payload: {
      data: CooperativaCreatePayload | CooperativaUpdatePayload
      file: File | null
      id?: number
      adminUserIds?: number[]
    },
  ): void
  (e: 'refresh'): void
}>()

const {
  form,
  errors,
  isEditMode,
  validateField,
  validateAll,
  getCreatePayload,
  getUpdatePayload,
  setLogoFile,
} = useCooperativaForm(() => props.cooperativa)

const {
  currentAdmins,
  loadAdministrators,
  removeAdministrator,
} = useCooperativaAdministrators()

const isAdminsModalOpen = ref(false)
const selectedAdminsForCreate = ref<EligibleAdmin[]>([])
const logoPreview = ref<string | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

const displayedAdmins = computed(() =>
  isEditMode.value ? currentAdmins.value : selectedAdminsForCreate.value,
)

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      form.name = props.cooperativa?.name || ''
      form.ruc = props.cooperativa?.ruc || ''
      form.address = props.cooperativa?.address || ''
      form.phone = props.cooperativa?.phone || ''
      form.email = props.cooperativa?.email || ''
      form.logo_url = props.cooperativa?.logo_url || ''
      form.logo_file = null
      logoPreview.value = resolveLogoUrl(props.cooperativa?.logo_url) || null
      selectedAdminsForCreate.value = []
      Object.keys(errors).forEach((k) => (errors[k] = ''))

      if (props.cooperativa?.id) {
        loadAdministrators(props.cooperativa.id)
      }
    }
  },
  { immediate: true },
)

watch(
  () => form.logo_url,
  (newUrl) => {
    if (!form.logo_file) {
      logoPreview.value = resolveLogoUrl(newUrl) || null
    }
  },
)

function onFileSelected(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0] || null
  if (file) {
    if (file.size > 2 * 1024 * 1024) {
      errors.logo = 'El archivo no puede exceder los 2 MB'
      return
    }
    errors.logo = ''
    setLogoFile(file)
    logoPreview.value = URL.createObjectURL(file)
  }
}

function handleAdminsSaved(payload?: { userIds: number[]; users: EligibleAdmin[] }) {
  if (isEditMode.value && props.cooperativa?.id) {
    loadAdministrators(props.cooperativa.id)
    emit('refresh')
  } else if (payload?.users) {
    selectedAdminsForCreate.value = payload.users
  }
}

async function handleRemoveAdmin(userId: number) {
  if (isEditMode.value && props.cooperativa?.id) {
    const success = await removeAdministrator(props.cooperativa.id, userId)
    if (success) {
      emit('refresh')
    }
  } else {
    selectedAdminsForCreate.value = selectedAdminsForCreate.value.filter((u) => u.id !== userId)
  }
}

function handleSubmit() {
  if (!validateAll()) return

  if (isEditMode.value && props.cooperativa) {
    emit('submit', {
      data: getUpdatePayload(),
      file: form.logo_file,
      id: props.cooperativa.id,
    })
  } else {
    emit('submit', {
      data: getCreatePayload(),
      file: form.logo_file,
      adminUserIds: selectedAdminsForCreate.value.map((u) => u.id),
    })
  }
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-40 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4 overflow-y-auto"
    data-testid="cooperativa-form-dialog"
  >
    <div
      class="my-8 flex max-h-[90vh] w-full max-w-2xl flex-col rounded-xl border border-border bg-card shadow-2xl overflow-hidden"
    >
      <!-- Header -->
      <div class="flex items-center justify-between border-b border-border px-6 py-4">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Building2 class="h-5 w-5" />
          </div>
          <div>
            <h2 class="text-lg font-semibold text-foreground">
              {{ isEditMode ? 'Editar Cooperativa' : 'Nueva Cooperativa' }}
            </h2>
            <p class="text-xs text-muted-foreground">
              {{
                isEditMode
                  ? 'Modifica los datos y gestiona el personal'
                  : 'Registra una cooperativa afiliada al terminal'
              }}
            </p>
          </div>
        </div>
        <Button variant="ghost" size="icon" class="h-8 w-8 rounded-full" @click="emit('close')">
          <X class="h-4 w-4" />
        </Button>
      </div>

      <!-- Form Body -->
      <div class="flex-1 overflow-y-auto p-6 space-y-5">
        <!-- Nombre y RUC -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-medium text-foreground mb-1">
              Nombre de la Cooperativa <span class="text-destructive">*</span>
            </label>
            <input
              type="text"
              v-model="form.name"
              placeholder="Ej. Cooperativa Loja"
              class="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              :class="{ 'border-destructive ring-destructive/20': errors.name }"
              @blur="validateField('name')"
              data-testid="coop-name-input"
            />
            <p v-if="errors.name" class="mt-1 text-xs text-destructive" data-testid="coop-name-error">
              {{ errors.name }}
            </p>
          </div>

          <div>
            <label class="block text-xs font-medium text-foreground mb-1">
              RUC (13 dígitos) <span class="text-destructive">*</span>
            </label>
            <input
              type="text"
              v-model="form.ruc"
              placeholder="1104609829001"
              maxlength="13"
              class="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              :class="[
                { 'border-destructive ring-destructive/20': errors.ruc },
                isEditMode ? 'opacity-60 bg-muted cursor-not-allowed' : '',
              ]"
              :disabled="isEditMode"
              @blur="validateField('ruc')"
              data-testid="coop-ruc-input"
            />
            <p v-if="errors.ruc" class="mt-1 text-xs text-destructive" data-testid="coop-ruc-error">
              {{ errors.ruc }}
            </p>
            <p v-if="isEditMode" class="mt-1 text-[11px] text-muted-foreground">
              El RUC no puede modificarse una vez registrado.
            </p>
          </div>
        </div>

        <!-- Dirección -->
        <div>
          <label class="block text-xs font-medium text-foreground mb-1">
            Dirección de Oficina en Terminal
          </label>
          <input
            type="text"
            v-model="form.address"
            placeholder="Oficina #4, Planta Baja"
            class="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            :class="{ 'border-destructive ring-destructive/20': errors.address }"
            @blur="validateField('address')"
          />
          <p v-if="errors.address" class="mt-1 text-xs text-destructive">
            {{ errors.address }}
          </p>
        </div>

        <!-- Teléfono y Correo -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-medium text-foreground mb-1">
              Teléfono de Contacto
            </label>
            <input
              type="text"
              v-model="form.phone"
              placeholder="0987654321"
              maxlength="10"
              class="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              :class="{ 'border-destructive ring-destructive/20': errors.phone }"
              @blur="validateField('phone')"
            />
            <p v-if="errors.phone" class="mt-1 text-xs text-destructive">
              {{ errors.phone }}
            </p>
          </div>

          <div>
            <label class="block text-xs font-medium text-foreground mb-1">
              Correo Institucional
            </label>
            <input
              type="email"
              v-model="form.email"
              placeholder="contacto@cooperativa.ec"
              class="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              :class="{ 'border-destructive ring-destructive/20': errors.email }"
              @blur="validateField('email')"
            />
            <p v-if="errors.email" class="mt-1 text-xs text-destructive">
              {{ errors.email }}
            </p>
          </div>
        </div>

        <!-- Logo (URL o Subida) -->
        <div class="space-y-2 rounded-lg border border-border p-4 bg-muted/10">
          <label class="block text-xs font-semibold text-foreground">
            Logo de la Cooperativa (Opcional)
          </label>

          <div class="flex flex-col sm:flex-row items-center gap-4">
            <!-- Preview Box -->
            <div
              class="flex h-16 w-16 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-border bg-muted/30"
            >
              <img
                v-if="logoPreview"
                :src="logoPreview"
                alt="Vista previa logo"
                class="h-full w-full object-cover"
              />
              <FileImage v-else class="h-8 w-8 text-muted-foreground/60" />
            </div>

            <!-- Upload / URL Options -->
            <div class="flex-1 w-full space-y-2">
              <input
                type="text"
                v-model="form.logo_url"
                :placeholder="
                  isEditMode
                    ? 'https://ejemplo.com/logo.png o /static/logos/...'
                    : 'https://ejemplo.com/logo.png'
                "
                class="w-full rounded-lg border border-input bg-background px-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                @blur="validateField('logo_url')"
              />
              <div class="flex items-center gap-2">
                <input
                  type="file"
                  ref="fileInputRef"
                  accept="image/png,image/jpeg,image/webp"
                  class="hidden"
                  @change="onFileSelected"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  class="gap-1.5 text-xs"
                  @click="fileInputRef?.click()"
                >
                  <Upload class="h-3.5 w-3.5" />
                  Subir imagen (PNG, JPG, WEBP - máx 2 MB)
                </Button>
                <span v-if="form.logo_file" class="text-xs text-muted-foreground truncate max-w-xs">
                  {{ form.logo_file.name }}
                </span>
              </div>
            </div>
          </div>
          <p v-if="errors.logo" class="text-xs text-destructive">
            {{ errors.logo }}
          </p>
        </div>

        <!-- Sección Personal de cooperativa (disponible en registro y edición) -->
        <div class="space-y-3 rounded-lg border border-border p-4 bg-muted/20">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm font-semibold text-foreground flex items-center gap-2">
                <Users class="h-4 w-4 text-primary" />
                Personal de cooperativa
              </h3>
              <p class="text-xs text-muted-foreground">
                Hasta 3 administradores de cooperativa vinculados {{ isEditMode ? '' : '(opcional)' }}
              </p>
            </div>
            <Button
              type="button"
              variant="outline"
              size="sm"
              class="gap-1.5 text-xs"
              @click="isAdminsModalOpen = true"
              data-testid="manage-admins-button"
            >
              <Users class="h-3.5 w-3.5" />
              Gestionar administradores
            </Button>
          </div>

          <!-- Administradores asignados actualmente o seleccionados para crear -->
          <div v-if="displayedAdmins.length === 0" class="text-xs text-muted-foreground italic py-2">
            No hay administradores asignados actualmente.
          </div>
          <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
            <div
              v-for="admin in displayedAdmins"
              :key="admin.id"
              class="flex items-center justify-between rounded-lg border border-border bg-card px-3 py-2 text-xs shadow-2xs"
            >
              <div>
                <p class="font-medium text-foreground">
                  {{ admin.first_name }} {{ admin.last_name }}
                </p>
                <p class="text-muted-foreground text-[11px]">{{ admin.email }}</p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                class="h-7 w-7 text-muted-foreground hover:text-destructive"
                title="Desvincular administrador"
                @click="handleRemoveAdmin(admin.id)"
              >
                <UserMinus class="h-3.5 w-3.5" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-end gap-3 border-t border-border px-6 py-4 bg-muted/20">
        <Button variant="outline" size="sm" @click="emit('close')">
          Cancelar
        </Button>
        <Button
          size="sm"
          :disabled="isSubmitting"
          class="gap-1.5"
          @click="handleSubmit"
          data-testid="submit-cooperativa-button"
        >
          <Loader2 v-if="isSubmitting" class="h-4 w-4 animate-spin" />
          {{ isEditMode ? 'Guardar cambios' : 'Registrar cooperativa' }}
        </Button>
      </div>
    </div>

    <!-- Modal de asignación de administradores -->
    <CooperativaAdministratorsModal
      v-if="isAdminsModalOpen"
      :is-open="isAdminsModalOpen"
      :cooperativa-id="cooperativa?.id ?? 0"
      :initial-selected-user-ids="isEditMode ? currentAdmins.map((a) => a.id) : selectedAdminsForCreate.map((a) => a.id)"
      @close="isAdminsModalOpen = false"
      @saved="handleAdminsSaved"
    />
  </div>
</template>
