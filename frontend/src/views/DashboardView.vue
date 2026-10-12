<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/auth.store'

const router = useRouter()
const authStore = useAuthStore()
const isLoggingOut = ref(false)

onMounted(async () => {
  if (!authStore.user) {
    await authStore.checkAuth()
  }
})

async function handleLogout() {
  isLoggingOut.value = true
  try {
    await authStore.logout()
    router.push({ name: 'login' })
  } catch {
    // Graceful fallback to login
    router.push({ name: 'login' })
  } finally {
    isLoggingOut.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-background text-foreground flex flex-col">
    <!-- Navigation Bar -->
    <header class="border-b border-border bg-card/80 backdrop-blur sticky top-0 z-10 px-4 sm:px-8 py-3.5 flex items-center justify-between shadow-xs">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-primary text-primary-foreground flex items-center justify-center font-bold text-lg shadow-sm">
          BY
        </div>
        <div>
          <h1 class="font-bold text-lg leading-tight">BoletoYa</h1>
          <span class="text-xs text-muted-foreground">Portal de Pasajeros</span>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <!-- User Badge -->
        <div class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-muted text-xs font-medium border border-border">
          <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>{{ authStore.user?.first_name || 'Pasajero' }}</span>
          <span class="text-muted-foreground">({{ authStore.user?.role || 'PASAJERO' }})</span>
        </div>

        <!-- Logout Button -->
        <Button
          variant="destructive"
          size="sm"
          class="rounded-xl gap-1.5 shadow-xs"
          :disabled="isLoggingOut"
          @click="handleLogout"
        >
          <span>🚪</span>
          <span>{{ isLoggingOut ? 'Cerrando...' : 'Cerrar sesión' }}</span>
        </Button>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="flex-1 max-w-5xl w-full mx-auto p-4 sm:p-8 space-y-6">
      <!-- Welcome Hero Banner -->
      <div class="rounded-2xl bg-gradient-to-r from-primary/15 via-accent/15 to-secondary/15 border border-border p-6 sm:p-8 shadow-sm">
        <div class="max-w-2xl space-y-2">
          <span class="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-primary text-primary-foreground shadow-xs">
            Sesión Activa
          </span>
          <h2 class="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
            ¡Bienvenido/a, {{ authStore.user?.first_name }} {{ authStore.user?.last_name }}!
          </h2>
          <p class="text-sm text-muted-foreground">
            Has iniciado sesión exitosamente en el sistema de transporte BoletoYa. Aquí podrás consultar rutas, turnos y gestionar tus reservas.
          </p>
        </div>
      </div>

      <!-- Account Details Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Profile Card -->
        <div class="rounded-2xl bg-card border border-border p-6 shadow-sm space-y-4">
          <h3 class="text-lg font-bold flex items-center gap-2">
            <span>👤</span>
            <span>Información del Perfil</span>
          </h3>

          <dl class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            <div class="p-3 rounded-xl bg-muted/50 border border-border/50">
              <dt class="text-xs text-muted-foreground font-medium">Nombres completos</dt>
              <dd class="font-semibold mt-0.5">{{ authStore.user?.first_name }} {{ authStore.user?.last_name }}</dd>
            </div>

            <div class="p-3 rounded-xl bg-muted/50 border border-border/50">
              <dt class="text-xs text-muted-foreground font-medium">Correo electrónico</dt>
              <dd class="font-semibold mt-0.5 truncate">{{ authStore.user?.email }}</dd>
            </div>

            <div class="p-3 rounded-xl bg-muted/50 border border-border/50">
              <dt class="text-xs text-muted-foreground font-medium">Documento</dt>
              <dd class="font-semibold mt-0.5">{{ authStore.user?.document_type }}: {{ authStore.user?.document_number }}</dd>
            </div>

            <div class="p-3 rounded-xl bg-muted/50 border border-border/50">
              <dt class="text-xs text-muted-foreground font-medium">Rol del sistema</dt>
              <dd class="font-semibold mt-0.5 text-primary">{{ authStore.user?.role }}</dd>
            </div>
          </dl>
        </div>

        <!-- System Status Card -->
        <div class="rounded-2xl bg-card border border-border p-6 shadow-sm space-y-4">
          <h3 class="text-lg font-bold flex items-center gap-2">
            <span>🛡️</span>
            <span>Seguridad de Sesión</span>
          </h3>
          <p class="text-sm text-muted-foreground">
            Tu sesión cuenta con protección JWT y validación contra tokens revocados. Al cerrar tu sesión, el token se invalida automáticamente en todas las pestañas.
          </p>

          <div class="p-4 rounded-xl bg-primary/10 border border-primary/20 space-y-2 text-xs">
            <p class="font-semibold text-primary">Estado del submódulo 01:</p>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground">
              <li>Autenticación por email y contraseña activa</li>
              <li>Protección de rutas contra acceso no autorizado</li>
              <li>Cierre de sesión seguro con blacklist</li>
            </ul>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="border-t border-border py-4 text-center text-xs text-muted-foreground">
      BoletoYa (PIC) — Submódulo 01: Autenticación y Seguridad
    </footer>
  </div>
</template>
