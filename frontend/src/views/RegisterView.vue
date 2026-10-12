<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/auth.store'
import { useFormValidation } from '@/composables/useFormValidation'
import type { ApiError } from '@/services/api-client'
import type { DocumentType } from '@/services/auth.service'

const router = useRouter()
const authStore = useAuthStore()
const {
  validateRequired,
  validateDocument,
  validateName,
  validateEmail,
  validatePassword,
  normalizeEmail,
} = useFormValidation()

const form = reactive({
  document_type: 'CEDULA' as DocumentType,
  document_number: '',
  first_name: '',
  last_name: '',
  email: '',
  password: '',
})

const errors = reactive({
  document_type: '',
  document_number: '',
  first_name: '',
  last_name: '',
  email: '',
  password: '',
})

const generalError = ref('')
const successMessage = ref('')
const isLoading = ref(false)

function validateForm(): boolean {
  let isValid = true

  // Required checks
  const docTypeVal = validateRequired(form.document_type)
  errors.document_type = docTypeVal.errorMessage
  if (!docTypeVal.isValid) isValid = false

  // Document number validation
  const docVal = validateDocument(form.document_type, form.document_number)
  errors.document_number = docVal.errorMessage
  if (!docVal.isValid) isValid = false

  // Names validation
  const fnVal = validateName(form.first_name)
  errors.first_name = fnVal.errorMessage
  if (!fnVal.isValid) isValid = false

  const lnVal = validateName(form.last_name)
  errors.last_name = lnVal.errorMessage
  if (!lnVal.isValid) isValid = false

  // Email validation
  const emailVal = validateEmail(form.email)
  errors.email = emailVal.errorMessage
  if (!emailVal.isValid) isValid = false

  // Password validation
  const pwdVal = validatePassword(form.password)
  errors.password = pwdVal.errorMessage
  if (!pwdVal.isValid) isValid = false

  return isValid
}

async function handleRegister() {
  generalError.value = ''
  successMessage.value = ''

  if (!validateForm()) return

  isLoading.value = true
  try {
    await authStore.register({
      document_type: form.document_type,
      document_number: form.document_number.trim(),
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      email: normalizeEmail(form.email),
      password: form.password,
    })

    successMessage.value = 'Cuenta creada satisfactoriamente'

    // Redirect to login after 2 seconds
    setTimeout(() => {
      router.push({ name: 'login' })
    }, 2000)
  } catch (err: unknown) {
    const apiErr = err as ApiError
    generalError.value =
      apiErr.message || 'Ocurrió un error al registrar la cuenta'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4 sm:p-6 bg-gradient-to-br from-background via-muted/40 to-background">
    <div class="w-full max-w-lg bg-card text-card-foreground rounded-2xl border border-border shadow-xl p-6 sm:p-8 space-y-6">
      <!-- Header -->
      <div class="text-center space-y-2">
        <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-primary text-primary-foreground shadow-md mb-2 font-bold text-xl">
          BY
        </div>
        <h1 class="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
          Crear cuenta en BoletoYa
        </h1>
        <p class="text-sm text-muted-foreground">
          Completa tus datos para comprar y reservar tus boletos
        </p>
      </div>

      <!-- Success Notification -->
      <div
        v-if="successMessage"
        class="p-4 rounded-xl text-sm font-medium bg-emerald-500/15 text-emerald-800 dark:text-emerald-200 border border-emerald-500/30 flex items-center gap-3 animate-in fade-in"
        role="status"
      >
        <span class="text-lg">✅</span>
        <div>
          <p class="font-semibold">{{ successMessage }}</p>
          <p class="text-xs opacity-90">Redirigiendo a inicio de sesión...</p>
        </div>
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

      <!-- Register Form -->
      <form @submit.prevent="handleRegister" class="space-y-4" novalidate>
        <!-- Document Type and Number Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div class="space-y-1.5">
            <label for="doc-type" class="block text-sm font-medium text-foreground">
              Tipo de doc.
            </label>
            <select
              id="doc-type"
              v-model="form.document_type"
              class="w-full px-3.5 py-2.5 rounded-xl bg-background border border-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition shadow-sm"
              :class="{ 'border-destructive': errors.document_type }"
            >
              <option value="CEDULA">Cédula</option>
              <option value="PASAPORTE">Pasaporte</option>
            </select>
          </div>

          <div class="sm:col-span-2 space-y-1.5">
            <label for="doc-number" class="block text-sm font-medium text-foreground">
              Número de documento
            </label>
            <input
              id="doc-number"
              v-model="form.document_number"
              type="text"
              :placeholder="form.document_type === 'CEDULA' ? 'Ej. 1710034065' : 'Ej. PASS123456'"
              class="w-full px-3.5 py-2.5 rounded-xl bg-background border border-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition shadow-sm"
              :class="{ 'border-destructive focus:ring-destructive': errors.document_number }"
            />
            <p v-if="errors.document_number" class="text-xs text-destructive font-medium">
              {{ errors.document_number }}
            </p>
          </div>
        </div>

        <!-- First & Last Name Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div class="space-y-1.5">
            <label for="first-name" class="block text-sm font-medium text-foreground">
              Nombres
            </label>
            <input
              id="first-name"
              v-model="form.first_name"
              type="text"
              placeholder="Ej. Juan Carlos"
              class="w-full px-3.5 py-2.5 rounded-xl bg-background border border-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition shadow-sm"
              :class="{ 'border-destructive focus:ring-destructive': errors.first_name }"
            />
            <p v-if="errors.first_name" class="text-xs text-destructive font-medium">
              {{ errors.first_name }}
            </p>
          </div>

          <div class="space-y-1.5">
            <label for="last-name" class="block text-sm font-medium text-foreground">
              Apellidos
            </label>
            <input
              id="last-name"
              v-model="form.last_name"
              type="text"
              placeholder="Ej. Pérez Gómez"
              class="w-full px-3.5 py-2.5 rounded-xl bg-background border border-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition shadow-sm"
              :class="{ 'border-destructive focus:ring-destructive': errors.last_name }"
            />
            <p v-if="errors.last_name" class="text-xs text-destructive font-medium">
              {{ errors.last_name }}
            </p>
          </div>
        </div>

        <!-- Email -->
        <div class="space-y-1.5">
          <label for="reg-email" class="block text-sm font-medium text-foreground">
            Correo electrónico
          </label>
          <input
            id="reg-email"
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
          <label for="reg-password" class="block text-sm font-medium text-foreground">
            Contraseña
          </label>
          <input
            id="reg-password"
            v-model="form.password"
            type="password"
            autocomplete="new-password"
            placeholder="Mínimo 8 caracteres (mayúscula, minúscula, número)"
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
          class="w-full py-2.5 rounded-xl font-semibold shadow-md transition mt-2"
          :disabled="isLoading || Boolean(successMessage)"
        >
          <span v-if="isLoading">Procesando...</span>
          <span v-else>Crear cuenta</span>
        </Button>
      </form>

      <!-- Footer / Login Link -->
      <div class="pt-2 text-center text-sm text-muted-foreground">
        ¿Ya tienes una cuenta?
        <router-link
          :to="{ name: 'login' }"
          class="font-semibold text-primary hover:underline ml-1"
        >
          Inicia sesión
        </router-link>
      </div>
    </div>
  </div>
</template>
