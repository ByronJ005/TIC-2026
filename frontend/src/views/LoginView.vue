<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/auth.store'
import { useFormValidation } from '@/composables/useFormValidation'
import type { ApiError } from '@/services/api-client'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { validateRequired, normalizeEmail } = useFormValidation()

const form = reactive({
  email: '',
  password: '',
})

const errors = reactive({
  email: '',
  password: '',
})

const generalError = ref('')
const isLoading = ref(false)

const sessionExpiredBanner = computed(() => {
  if (route.query.message === 'session_expired' || authStore.sessionExpiredMessage) {
    return authStore.sessionExpiredMessage || 'Sesión expirada. Por favor, inicia sesión de nuevo.'
  }
  return ''
})

onMounted(() => {
  if (authStore.isAuthenticated) {
    router.replace({ name: 'dashboard' })
  }
})

function validateForm(): boolean {
  let isValid = true

  const emailVal = validateRequired(form.email)
  errors.email = emailVal.errorMessage
  if (!emailVal.isValid) isValid = false

  const pwdVal = validateRequired(form.password)
  errors.password = pwdVal.errorMessage
  if (!pwdVal.isValid) isValid = false

  return isValid
}

async function handleLogin() {
  generalError.value = ''
  if (!validateForm()) return

  isLoading.value = true
  try {
    await authStore.login({
      email: normalizeEmail(form.email),
      password: form.password,
    })
    router.push({ name: 'dashboard' })
  } catch (err: unknown) {
    const apiErr = err as ApiError
    generalError.value = apiErr.message || 'Credenciales incorrectas'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4 sm:p-6 bg-gradient-to-br from-background via-muted/40 to-background">
    <div class="w-full max-w-md bg-card text-card-foreground rounded-2xl border border-border shadow-xl p-6 sm:p-8 space-y-6">
      <!-- Header -->
      <div class="text-center space-y-2">
        <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-primary text-primary-foreground shadow-md mb-2 font-bold text-xl">
          BY
        </div>
        <h1 class="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
          BoletoYa
        </h1>
        <p class="text-sm text-muted-foreground">
          Ingresa a tu cuenta para gestionar tus pasajes
        </p>
      </div>

      <!-- Session Expired Alert -->
      <div
        v-if="sessionExpiredBanner"
        class="p-3.5 rounded-xl text-sm font-medium bg-amber-500/15 text-amber-900 dark:text-amber-200 border border-amber-500/30 flex items-center gap-2"
        role="alert"
      >
        <span>⚠️</span>
        <span>{{ sessionExpiredBanner }}</span>
      </div>

      <!-- General Error Alert -->
      <div
        v-if="generalError"
        class="p-3.5 rounded-xl text-sm font-medium bg-destructive/15 text-destructive border border-destructive/30 flex items-center gap-2"
        role="alert"
      >
        <span>❌</span>
        <span>{{ generalError }}</span>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="space-y-4" novalidate>
        <!-- Email -->
        <div class="space-y-1.5">
          <label for="email" class="block text-sm font-medium text-foreground">
            Correo electrónico
          </label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            autocomplete="email"
            placeholder="ejemplo@correo.com"
            class="w-full px-3.5 py-2.5 rounded-xl bg-background border border-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition shadow-sm"
            :class="{ 'border-destructive focus:ring-destructive': errors.email }"
          />
          <p v-if="errors.email" class="text-xs text-destructive font-medium">
            {{ errors.email }}
          </p>
        </div>

        <!-- Password -->
        <div class="space-y-1.5">
          <div class="flex items-center justify-between">
            <label for="password" class="block text-sm font-medium text-foreground">
              Contraseña
            </label>
          </div>
          <input
            id="password"
            v-model="form.password"
            type="password"
            autocomplete="current-password"
            placeholder="••••••••"
            class="w-full px-3.5 py-2.5 rounded-xl bg-background border border-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition shadow-sm"
            :class="{ 'border-destructive focus:ring-destructive': errors.password }"
          />
          <p v-if="errors.password" class="text-xs text-destructive font-medium">
            {{ errors.password }}
          </p>
        </div>

        <!-- Submit Button -->
        <Button
          type="submit"
          class="w-full py-2.5 rounded-xl font-semibold shadow-md transition"
          :disabled="isLoading"
        >
          <span v-if="isLoading">Ingresando...</span>
          <span v-else>Ingresar</span>
        </Button>
      </form>

      <!-- Footer / Register Link -->
      <div class="pt-2 text-center text-sm text-muted-foreground">
        ¿No tienes una cuenta?
        <router-link
          :to="{ name: 'register' }"
          class="font-semibold text-primary hover:underline ml-1"
        >
          Regístrate aquí
        </router-link>
      </div>
    </div>
  </div>
</template>
