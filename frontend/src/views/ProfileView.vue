<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { AlertCircle, CheckCircle2, KeyRound, Loader2, UserRound } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { MIN_BIRTH_DATE, toIsoDate } from '@/composables/useFormValidation'
import { useProfileForm } from '@/composables/useProfileForm'
import { useAuthStore } from '@/stores/auth.store'

const authStore = useAuthStore()
const { form, errors, generalError, successMessage, isSaving, loadFromUser, submit } =
  useProfileForm()

const maxBirthDate = computed(() => toIsoDate(new Date()))
const documentLabel = computed(() =>
  authStore.user?.document_type === 'PASAPORTE' ? 'Pasaporte' : 'Cédula',
)

const inputClass =
  'w-full px-3.5 py-2.5 rounded-xl bg-background border border-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition shadow-sm disabled:opacity-60 disabled:cursor-not-allowed'
const errorInputClass = 'border-destructive focus:ring-destructive'

onMounted(() => {
  loadFromUser(authStore.user)
})
</script>

<template>
  <div class="space-y-6 max-w-3xl">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
        <UserRound class="w-5 h-5" />
      </div>
      <div>
        <h2 class="text-2xl font-bold tracking-tight text-foreground">Perfil</h2>
        <p class="text-sm text-muted-foreground">Actualiza tus datos personales y tu contraseña.</p>
      </div>
    </div>

    <div
      v-if="successMessage"
      class="p-3.5 rounded-xl text-sm font-medium bg-primary/10 text-foreground border border-primary/30 flex items-center gap-2.5"
      role="status"
    >
      <CheckCircle2 class="w-4 h-4 shrink-0 text-primary" />
      <span>{{ successMessage }}</span>
    </div>

    <div
      v-if="generalError"
      class="p-3.5 rounded-xl text-sm font-medium bg-destructive/15 text-destructive border border-destructive/30 flex items-center gap-2.5"
      role="alert"
    >
      <AlertCircle class="w-4 h-4 shrink-0" />
      <span>{{ generalError }}</span>
    </div>

    <form
      class="space-y-6 rounded-2xl border border-border bg-card text-card-foreground p-6 shadow-xs"
      novalidate
      @submit.prevent="submit"
    >
      <!-- Read-only identity data -->
      <div class="grid gap-4 sm:grid-cols-2">
        <div class="space-y-1.5">
          <label for="profile-email" class="block text-sm font-medium text-foreground">
            Correo electrónico
          </label>
          <input
            id="profile-email"
            :value="authStore.user?.email"
            type="email"
            disabled
            :class="inputClass"
          />
        </div>
        <div class="space-y-1.5">
          <label for="profile-document" class="block text-sm font-medium text-foreground">
            {{ documentLabel }}
          </label>
          <input
            id="profile-document"
            :value="authStore.user?.document_number"
            type="text"
            disabled
            :class="inputClass"
          />
        </div>
      </div>

      <!-- Personal data -->
      <div class="grid gap-4 sm:grid-cols-2">
        <div class="space-y-1.5">
          <label for="profile-first-name" class="block text-sm font-medium text-foreground">
            Nombres
          </label>
          <input
            id="profile-first-name"
            v-model="form.first_name"
            type="text"
            autocomplete="given-name"
            :class="[inputClass, errors.first_name && errorInputClass]"
          />
          <p v-if="errors.first_name" class="text-xs text-destructive font-medium">
            {{ errors.first_name }}
          </p>
        </div>

        <div class="space-y-1.5">
          <label for="profile-last-name" class="block text-sm font-medium text-foreground">
            Apellidos
          </label>
          <input
            id="profile-last-name"
            v-model="form.last_name"
            type="text"
            autocomplete="family-name"
            :class="[inputClass, errors.last_name && errorInputClass]"
          />
          <p v-if="errors.last_name" class="text-xs text-destructive font-medium">
            {{ errors.last_name }}
          </p>
        </div>

        <div class="space-y-1.5">
          <label for="profile-phone" class="block text-sm font-medium text-foreground">
            Celular
          </label>
          <input
            id="profile-phone"
            v-model="form.phone"
            type="text"
            inputmode="numeric"
            autocomplete="tel"
            placeholder="0991234567"
            :class="[inputClass, errors.phone && errorInputClass]"
          />
          <p v-if="errors.phone" class="text-xs text-destructive font-medium">
            {{ errors.phone }}
          </p>
        </div>

        <div class="space-y-1.5">
          <label for="profile-birth-date" class="block text-sm font-medium text-foreground">
            Fecha de nacimiento
          </label>
          <input
            id="profile-birth-date"
            v-model="form.birth_date"
            type="date"
            :min="MIN_BIRTH_DATE"
            :max="maxBirthDate"
            :class="[inputClass, errors.birth_date && errorInputClass]"
          />
          <p v-if="errors.birth_date" class="text-xs text-destructive font-medium">
            {{ errors.birth_date }}
          </p>
        </div>

        <div class="space-y-1.5 sm:col-span-2">
          <label for="profile-address" class="block text-sm font-medium text-foreground">
            Dirección
          </label>
          <input
            id="profile-address"
            v-model="form.address"
            type="text"
            autocomplete="street-address"
            :class="[inputClass, errors.address && errorInputClass]"
          />
          <p v-if="errors.address" class="text-xs text-destructive font-medium">
            {{ errors.address }}
          </p>
        </div>
      </div>

      <!-- Password change (optional, all-or-nothing) -->
      <fieldset class="space-y-4 border-t border-border pt-6">
        <legend class="flex items-center gap-2 text-sm font-semibold text-foreground">
          <KeyRound class="w-4 h-4 text-muted-foreground" />
          Cambiar contraseña
        </legend>
        <p class="text-xs text-muted-foreground">
          Déjalos vacíos para conservar tu contraseña actual. Si completas uno, debes completar los
          tres.
        </p>

        <div class="grid gap-4 sm:grid-cols-3">
          <div class="space-y-1.5">
            <label for="profile-current-password" class="block text-sm font-medium text-foreground">
              Contraseña actual
            </label>
            <input
              id="profile-current-password"
              v-model="form.current_password"
              type="password"
              autocomplete="current-password"
              :class="[inputClass, errors.current_password && errorInputClass]"
            />
            <p v-if="errors.current_password" class="text-xs text-destructive font-medium">
              {{ errors.current_password }}
            </p>
          </div>

          <div class="space-y-1.5">
            <label for="profile-new-password" class="block text-sm font-medium text-foreground">
              Nueva contraseña
            </label>
            <input
              id="profile-new-password"
              v-model="form.new_password"
              type="password"
              autocomplete="new-password"
              :class="[inputClass, errors.new_password && errorInputClass]"
            />
            <p v-if="errors.new_password" class="text-xs text-destructive font-medium">
              {{ errors.new_password }}
            </p>
          </div>

          <div class="space-y-1.5">
            <label for="profile-confirm-password" class="block text-sm font-medium text-foreground">
              Confirmar contraseña
            </label>
            <input
              id="profile-confirm-password"
              v-model="form.confirm_password"
              type="password"
              autocomplete="new-password"
              :class="[inputClass, errors.confirm_password && errorInputClass]"
            />
            <p v-if="errors.confirm_password" class="text-xs text-destructive font-medium">
              {{ errors.confirm_password }}
            </p>
          </div>
        </div>
      </fieldset>

      <div class="flex justify-end">
        <Button
          type="submit"
          class="px-6 py-2.5 rounded-xl font-semibold shadow-md transition flex items-center justify-center gap-2"
          :disabled="isSaving"
        >
          <Loader2 v-if="isSaving" class="w-4 h-4 animate-spin" />
          <span>{{ isSaving ? 'Actualizando...' : 'Actualizar perfil' }}</span>
        </Button>
      </div>
    </form>
  </div>
</template>

