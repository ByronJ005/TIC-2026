<script setup lang="ts">
import { AlertCircle, ArrowLeft, Bus, CheckCircle2, Loader2, Mail } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { useForgotPasswordForm } from '@/composables/usePasswordRecovery'

const { email, emailError, generalError, successMessage, isLoading, submit } =
  useForgotPasswordForm()
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
        <h1 class="text-2xl font-bold tracking-tight text-foreground">Recuperar contraseña</h1>
        <p class="text-sm text-muted-foreground">
          Ingresa tu correo electrónico y te enviaremos un enlace para restablecerla.
        </p>
      </div>

      <div
        v-if="successMessage"
        class="p-3.5 rounded-xl text-sm font-medium bg-primary/10 text-foreground border border-primary/30 flex items-start gap-2.5"
        role="status"
      >
        <CheckCircle2 class="w-4 h-4 shrink-0 mt-0.5 text-primary" />
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

      <form class="space-y-4" novalidate @submit.prevent="submit">
        <div class="space-y-1.5">
          <label for="forgot-email" class="block text-sm font-medium text-foreground">
            Correo electrónico
          </label>
          <div class="relative">
            <Mail
              class="w-4 h-4 text-muted-foreground absolute left-3.5 top-1/2 -translate-y-1/2"
            />
            <input
              id="forgot-email"
              v-model="email"
              type="email"
              autocomplete="email"
              placeholder="ejemplo@correo.com"
              class="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-background border border-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition shadow-sm"
              :class="{ 'border-destructive focus:ring-destructive': emailError }"
            />
          </div>
          <p v-if="emailError" class="text-xs text-destructive font-medium">
            {{ emailError }}
          </p>
        </div>

        <Button
          type="submit"
          class="w-full py-2.5 rounded-xl font-semibold shadow-md transition flex items-center justify-center gap-2"
          :disabled="isLoading"
        >
          <Loader2 v-if="isLoading" class="w-4 h-4 animate-spin" />
          <span>{{ isLoading ? 'Enviando...' : 'Enviar enlace' }}</span>
        </Button>
      </form>

      <div class="pt-2 text-center text-sm">
        <router-link
          :to="{ name: 'login' }"
          class="inline-flex items-center gap-1.5 font-semibold text-primary hover:underline"
        >
          <ArrowLeft class="w-4 h-4" />
          Volver a iniciar sesión
        </router-link>
      </div>
    </div>
  </div>
</template>

