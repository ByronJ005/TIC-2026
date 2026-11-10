<script setup lang="ts">
import { ShieldCheck, User } from '@lucide/vue'
import { useAuthStore } from '@/stores/auth.store'

const authStore = useAuthStore()
</script>

<template>
  <div class="space-y-6">
    <!-- Welcome Hero Banner -->
    <div class="rounded-2xl bg-gradient-to-r from-primary/15 via-accent/15 to-secondary/15 border border-border p-6 sm:p-8 shadow-xs">
      <div class="max-w-2xl space-y-2">
        <span class="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-primary text-primary-foreground shadow-xs">
          Sesión Activa
        </span>
        <h2 class="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
          ¡Bienvenido/a, {{ authStore.user?.first_name }} {{ authStore.user?.last_name }}!
        </h2>
        <p class="text-sm text-muted-foreground">
          Has iniciado sesión exitosamente en el sistema de transporte BoletoYa. Utiliza el menú lateral para acceder a los módulos autorizados según tus roles.
        </p>
      </div>
    </div>

    <!-- Account Details Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Profile Card -->
      <div class="rounded-2xl bg-card border border-border p-6 shadow-xs space-y-4">
        <h3 class="text-lg font-bold flex items-center gap-2 text-foreground">
          <User class="w-5 h-5 text-primary" />
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
            <dt class="text-xs text-muted-foreground font-medium">Roles asignados</dt>
            <dd class="font-semibold mt-0.5 text-primary flex flex-wrap gap-1">
              <span
                v-for="r in authStore.user?.roles"
                :key="r"
                class="inline-block px-2 py-0.5 rounded-md text-xs bg-primary/10 text-primary border border-primary/20"
              >
                {{ r }}
              </span>
            </dd>
          </div>
        </dl>
      </div>

      <!-- System Status Card -->
      <div class="rounded-2xl bg-card border border-border p-6 shadow-xs space-y-4">
        <h3 class="text-lg font-bold flex items-center gap-2 text-foreground">
          <ShieldCheck class="w-5 h-5 text-primary" />
          <span>Seguridad y Permisos</span>
        </h3>
        <p class="text-sm text-muted-foreground">
          Tu cuenta opera bajo control de acceso basado en roles (RBAC). El menú lateral refleja en tiempo real los módulos habilitados para tus credenciales activas.
        </p>

        <div class="p-4 rounded-xl bg-primary/10 border border-primary/20 space-y-2 text-xs">
          <p class="font-semibold text-primary">Estado de submódulos:</p>
          <ul class="list-disc list-inside space-y-1 text-muted-foreground">
            <li>Submódulo 01: Autenticación JWT y control de sesiones activas</li>
            <li>Submódulo 02: Gestión de usuarios, roles múltiples y borrado lógico</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

