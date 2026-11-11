<script setup lang="ts">
import { AlertCircle, Bus, CheckCircle2, KeyRound, Loader2 } from '@lucide/vue'
import { useRoute } from 'vue-router'
import { Button } from '@/components/ui/button'
import { INVALID_RESET_LINK_MESSAGE, useResetPasswordForm } from '@/composables/usePasswordRecovery'

const route = useRoute()
const rawToken = route.query.token
const token = typeof rawToken === 'string' ? rawToken : ''

const {
  newPassword,
  confirmPassword,
  newPasswordError,
  confirmPasswordError,
  generalError,
  successMessage,
  isLoading,
  linkIsInvalid,
  submit,
} = useResetPasswordForm(token)
</script>

<template>
  <div
    class="min-h-screen flex items-center justify-center p-4 sm:p-6 bg-gradient-to-br from-background via-muted/40 to-background"
  >
    <div
      class="w-full max-w-md bg-card text-card-foreground rounded-2xl border border-border shadow-xl p-6 sm:p-8 space-y-6"
    >
      <div class="text-center space-y-2">
        <div
          class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-primary text-primary-foreground shadow-md mb-2"
        >
          <Bus class="w-6 h-6" />
        </div>
        <h1 class="text-2xl font-bold tracking-tight text-foreground">Nueva contraseña</h1>
        <p class="text-sm text-muted-foreground">Elige una nueva contraseña para tu cuenta.</p>
      </div>

      <!-- Invalid, expired or already used link -->
      <div v-if="linkIsInvalid" class="space-y-4">
        <div
          class="p-3.5 rounded-xl text-sm font-medium bg-destructive/15 text-destructive border border-destructive/30 flex items-start gap-2.5"
          role="alert"
        >
          <AlertCircle class="w-4 h-4 shrink-0 mt-0.5" />
          <span>{{ generalError || INVALID_RESET_LINK_MESSAGE }}</span>
        </div>
        <router-link
          :to="{ name: 'forgot-password' }"
          class="block text-center text-sm font-semibold text-primary hover:underline"
        >
          Solicitar un nuevo enlace
        </router-link>
      </div>

      <!-- Success -->
      <div v-else-if="successMessage" class="space-y-4">
        <div
          class="p-3.5 rounded-xl text-sm font-medium bg-primary/10 text-foreground border border-primary/30 flex items-start gap-2.5"
          role="status"
        >
          <CheckCircle2 class="w-4 h-4 shrink-0 mt-0.5 text-primary" />
          <span>{{ successMessage }}</span>
        </div>
        <router-link
          :to="{ name: 'login' }"
          class="block text-center text-sm font-semibold text-primary hover:underline"
        >
          Iniciar sesión
        </router-link>
      </div>

      <!-- Form -->
      <template v-else>
        <div
          v-if="generalError"
          class="p-3.5 rounded-xl text-sm font-medium bg-destructive/15 text-destructive border border-destructive/30 flex items-center gap-2.5"
          role="alert"
        >
          <AlertCircle class="w-4 h-4 shrink-0" />
          <span>{{ generalError }}</span>
        </div>

        <form class="space-y-4" novalidate @submit.prevent="submit">
          <div class="space-y-1.5">
            <label for="reset-new-password" class="block text-sm font-medium text-foreground">
              Nueva contraseña
            </label>
            <div class="relative">
              <KeyRound
                class="w-4 h-4 text-muted-foreground absolute left-3.5 top-1/2 -translate-y-1/2"
              />
              <input
                id="reset-new-password"
                v-model="newPassword"
                type="password"
                autocomplete="new-password"
                placeholder="••••••••"
                class="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-background border border-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition shadow-sm"
                :class="{ 'border-destructive focus:ring-destructive': newPasswordError }"
              />
            </div>
            <p v-if="newPasswordError" class="text-xs text-destructive font-medium">
              {{ newPasswordError }}
            </p>
          </div>

          <div class="space-y-1.5">
            <label for="reset-confirm-password" class="block text-sm font-medium text-foreground">
              Confirmar contraseña
            </label>
            <input
              id="reset-confirm-password"
              v-model="confirmPassword"
              type="password"
              autocomplete="new-password"
              placeholder="••••••••"
              class="w-full px-3.5 py-2.5 rounded-xl bg-background border border-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition shadow-sm"
              :class="{ 'border-destructive focus:ring-destructive': confirmPasswordError }"
            />
            <p v-if="confirmPasswordError" class="text-xs text-destructive font-medium">
              {{ confirmPasswordError }}
            </p>
          </div>

          <Button
            type="submit"
            class="w-full py-2.5 rounded-xl font-semibold shadow-md transition flex items-center justify-center gap-2"
            :disabled="isLoading"
          >
            <Loader2 v-if="isLoading" class="w-4 h-4 animate-spin" />
            <span>{{ isLoading ? 'Guardando...' : 'Restablecer contraseña' }}</span>
          </Button>
        </form>
      </template>
    </div>
  </div>
</template>

