<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  AlertTriangle,
  Building2,
  Bus,
  CalendarClock,
  ChevronLeft,
  ChevronRight,
  CircleDollarSign,
  Coins,
  Home,
  Loader2,
  LogOut,
  Map,
  Menu,
  Route as RouteIcon,
  Ticket,
  User as UserIcon,
  Users,
  X,
} from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/auth.store'
import type { UserRole } from '@/services/auth.service'

interface NavModule {
  id: string
  name: string
  path: string
  icon: unknown
  allowedRoles: UserRole[]
}

const ALL_MODULES: NavModule[] = [
  {
    id: 'usuarios',
    name: 'Usuarios',
    path: '/dashboard/usuarios',
    icon: Users,
    allowedRoles: ['ADMIN_GENERAL'],
  },
  {
    id: 'cooperativas',
    name: 'Cooperativas',
    path: '/dashboard/cooperativas',
    icon: Building2,
    allowedRoles: ['ADMIN_GENERAL'],
  },
  {
    id: 'rutas-generales',
    name: 'Rutas generales',
    path: '/dashboard/rutas-generales',
    icon: Map,
    allowedRoles: ['ADMIN_GENERAL'],
  },
  {
    id: 'precios-generales',
    name: 'Precios generales',
    path: '/dashboard/precios-generales',
    icon: Coins,
    allowedRoles: ['ADMIN_GENERAL'],
  },
  {
    id: 'rutas-cooperativa',
    name: 'Rutas de cooperativa',
    path: '/dashboard/rutas-cooperativa',
    icon: RouteIcon,
    allowedRoles: ['ADMIN_COOPERATIVA'],
  },
  {
    id: 'buses',
    name: 'Buses',
    path: '/dashboard/buses',
    icon: Bus,
    allowedRoles: ['ADMIN_COOPERATIVA'],
  },
  {
    id: 'turnos',
    name: 'Turnos',
    path: '/dashboard/turnos',
    icon: CalendarClock,
    allowedRoles: ['ADMIN_COOPERATIVA'],
  },
  {
    id: 'tarifas',
    name: 'Tarifas específicas',
    path: '/dashboard/tarifas',
    icon: CircleDollarSign,
    allowedRoles: ['ADMIN_COOPERATIVA'],
  },
  {
    id: 'reservas',
    name: 'Reservas',
    path: '/dashboard/reservas',
    icon: Ticket,
    allowedRoles: ['SECRETARIA_COOPERATIVA', 'PASAJERO'],
  },
  {
    id: 'perfil',
    name: 'Perfil',
    path: '/dashboard/perfil',
    icon: UserIcon,
    allowedRoles: ['PASAJERO'],
  },
]

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isLoggingOut = ref(false)
const showLogoutConfirm = ref(false)
const isCollapsed = ref(false)
const isMobileMenuOpen = ref(false)

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
}

function toggleMobileMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

function closeMobileMenu() {
  isMobileMenuOpen.value = false
}

// Auto-close mobile drawer on route navigation
watch(
  () => route.path,
  () => {
    isMobileMenuOpen.value = false
  },
)

onMounted(async () => {
  if (!authStore.user) {
    await authStore.checkAuth()
  }
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    if (isMobileMenuOpen.value) {
      isMobileMenuOpen.value = false
    } else if (showLogoutConfirm.value && !isLoggingOut.value) {
      showLogoutConfirm.value = false
    }
  }
}

function openLogoutModal() {
  showLogoutConfirm.value = true
}

function cancelLogout() {
  showLogoutConfirm.value = false
}

async function handleLogout() {
  isLoggingOut.value = true
  try {
    await authStore.logout()
    showLogoutConfirm.value = false
    router.push({ name: 'login' })
  } catch {
    showLogoutConfirm.value = false
    router.push({ name: 'login' })
  } finally {
    isLoggingOut.value = false
  }
}

// Compute visible modules based on the union of modules allowed for user's roles
const visibleModules = computed(() => {
  const roles = authStore.user?.roles || []
  if (roles.length === 0) return []

  return ALL_MODULES.filter((module) =>
    module.allowedRoles.some((role) => roles.includes(role)),
  )
})
</script>

<template>
  <div class="min-h-screen bg-background text-foreground flex flex-col">
    <!-- Top Header -->
    <header class="border-b border-border bg-card/80 backdrop-blur sticky top-0 z-30 px-4 sm:px-8 py-3.5 flex items-center justify-between shadow-xs">
      <div class="flex items-center gap-3">
        <!-- Hamburger Button Mobile -->
        <Button
          variant="ghost"
          size="icon"
          data-test="mobile-menu-btn"
          class="md:hidden h-9 w-9 rounded-xl text-muted-foreground hover:text-foreground hover:bg-muted cursor-pointer shrink-0"
          aria-label="Abrir menú de navegación"
          @click="toggleMobileMenu"
        >
          <Menu class="w-5 h-5" />
        </Button>

        <RouterLink to="/dashboard" class="flex items-center gap-3 group">
          <div class="w-10 h-10 rounded-xl bg-primary text-primary-foreground flex items-center justify-center font-bold text-lg shadow-xs group-hover:scale-105 transition-transform">
            <Bus class="w-5 h-5" />
          </div>
          <div>
            <h1 class="font-bold text-lg leading-tight tracking-tight">BoletoYa</h1>
            <span class="text-xs text-muted-foreground">Sistema de Transporte</span>
          </div>
        </RouterLink>
      </div>

      <div class="flex items-center gap-3">
        <!-- User Badge & Roles -->
        <div class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-muted text-xs font-medium border border-border">
          <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span class="font-semibold">{{ authStore.user?.first_name }} {{ authStore.user?.last_name }}</span>
          <div class="flex gap-1 ml-1">
            <span
              v-for="r in authStore.user?.roles"
              :key="r"
              class="px-1.5 py-0.5 rounded text-[10px] bg-primary/10 text-primary border border-primary/20 font-semibold"
            >
              {{ r }}
            </span>
          </div>
        </div>

        <!-- Logout Button -->
        <Button
          variant="destructive"
          size="sm"
          class="rounded-xl gap-2 shadow-xs cursor-pointer"
          :disabled="isLoggingOut"
          @click="openLogoutModal"
        >
          <LogOut class="w-4 h-4" />
          <span>Cerrar sesión</span>
        </Button>
      </div>
    </header>

    <div class="flex-1 flex max-w-7xl w-full mx-auto">
      <!-- Sidebar Navigation (Desktop) -->
      <aside
        class="border-r border-border bg-card/40 p-3 shrink-0 hidden md:flex flex-col justify-between transition-all duration-300"
        :class="[isCollapsed ? 'w-20' : 'w-64']"
      >
        <div class="space-y-4">
          <!-- Sidebar Header & Toggle Collapse Button -->
          <div
            class="flex items-center py-1.5"
            :class="[isCollapsed ? 'justify-center px-0' : 'justify-between px-2']"
          >
            <span
              v-if="!isCollapsed"
              class="text-xs font-semibold uppercase tracking-wider text-muted-foreground truncate"
            >
              Módulos autorizados
            </span>
            <Button
              variant="ghost"
              size="icon"
              data-test="toggle-collapse-btn"
              class="h-7 w-7 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted cursor-pointer shrink-0"
              :title="isCollapsed ? 'Expandir barra lateral' : 'Contraer barra lateral'"
              :aria-label="isCollapsed ? 'Expandir barra lateral' : 'Contraer barra lateral'"
              @click="toggleCollapse"
            >
              <ChevronRight v-if="isCollapsed" class="w-4 h-4" />
              <ChevronLeft v-else class="w-4 h-4" />
            </Button>
          </div>

          <nav class="space-y-1">
            <!-- Home Link -->
            <RouterLink
              to="/dashboard"
              exact
              class="flex items-center rounded-xl text-sm font-medium transition-colors"
              :class="[
                isCollapsed ? 'justify-center px-2 py-2.5' : 'gap-3 px-3 py-2.5',
                route.path === '/dashboard'
                  ? 'bg-primary text-primary-foreground shadow-xs font-semibold'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground',
              ]"
              :title="isCollapsed ? 'Inicio' : undefined"
            >
              <Home class="w-4 h-4 shrink-0" />
              <span v-if="!isCollapsed">Inicio</span>
            </RouterLink>

            <!-- Dynamic Module Links -->
            <RouterLink
              v-for="mod in visibleModules"
              :key="mod.id"
              :to="mod.path"
              class="flex items-center rounded-xl text-sm font-medium transition-colors"
              :class="[
                isCollapsed ? 'justify-center px-2 py-2.5' : 'gap-3 px-3 py-2.5',
                route.path.startsWith(mod.path)
                  ? 'bg-primary text-primary-foreground shadow-xs font-semibold'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground',
              ]"
              :title="isCollapsed ? mod.name : undefined"
            >
              <component :is="mod.icon" class="w-4 h-4 shrink-0" />
              <span v-if="!isCollapsed" class="truncate">{{ mod.name }}</span>
            </RouterLink>

            <!-- Fallback when no modules matched -->
            <div
              v-if="visibleModules.length === 0"
              class="px-2 py-4 text-xs text-muted-foreground text-center"
            >
              {{ isCollapsed ? '—' : 'Sin módulos asignados' }}
            </div>
          </nav>
        </div>
      </aside>

      <!-- Main Content Panel -->
      <main class="flex-1 p-4 sm:p-8 min-w-0">
        <RouterView />
      </main>
    </div>

    <!-- Mobile Drawer Overlay -->
    <Teleport to="body">
      <div v-if="isMobileMenuOpen" class="fixed inset-0 z-50 md:hidden flex" data-test="mobile-drawer">
        <!-- Backdrop -->
        <div
          class="fixed inset-0 bg-background/80 backdrop-blur-xs transition-opacity"
          data-test="mobile-drawer-backdrop"
          @click="closeMobileMenu"
        />
        <!-- Drawer Panel -->
        <aside
          class="relative z-50 w-72 max-w-[80vw] h-full bg-card border-r border-border p-4 flex flex-col justify-between shadow-2xl animate-in slide-in-from-left duration-200"
          role="dialog"
          aria-modal="true"
          aria-label="Menú de navegación móvil"
        >
          <div class="space-y-4">
            <!-- Drawer Header -->
            <div class="flex items-center justify-between pb-3 border-b border-border">
              <div class="flex items-center gap-2.5">
                <div class="w-8 h-8 rounded-lg bg-primary text-primary-foreground flex items-center justify-center font-bold shadow-xs">
                  <Bus class="w-4 h-4" />
                </div>
                <div>
                  <h2 class="font-bold text-sm leading-tight tracking-tight">BoletoYa</h2>
                  <span class="text-[10px] text-muted-foreground">Sistema de Transporte</span>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                data-test="close-mobile-menu-btn"
                class="h-8 w-8 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted cursor-pointer"
                aria-label="Cerrar menú"
                @click="closeMobileMenu"
              >
                <X class="w-4 h-4" />
              </Button>
            </div>

            <!-- Navigation Links -->
            <div>
              <div class="px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Módulos autorizados
              </div>
              <nav class="space-y-1 mt-1">
                <!-- Home -->
                <RouterLink
                  to="/dashboard"
                  exact
                  class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors"
                  :class="[
                    route.path === '/dashboard'
                      ? 'bg-primary text-primary-foreground shadow-xs font-semibold'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                  ]"
                  @click="closeMobileMenu"
                >
                  <Home class="w-4 h-4 shrink-0" />
                  <span>Inicio</span>
                </RouterLink>

                <!-- Dynamic Modules -->
                <RouterLink
                  v-for="mod in visibleModules"
                  :key="mod.id"
                  :to="mod.path"
                  class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors"
                  :class="[
                    route.path.startsWith(mod.path)
                      ? 'bg-primary text-primary-foreground shadow-xs font-semibold'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                  ]"
                  @click="closeMobileMenu"
                >
                  <component :is="mod.icon" class="w-4 h-4 shrink-0" />
                  <span class="truncate">{{ mod.name }}</span>
                </RouterLink>

                <div
                  v-if="visibleModules.length === 0"
                  class="px-3 py-4 text-xs text-muted-foreground text-center"
                >
                  Sin módulos asignados
                </div>
              </nav>
            </div>
          </div>

          <!-- Drawer Footer / User Info -->
          <div class="pt-4 border-t border-border space-y-3">
            <div class="flex items-center gap-2 px-2.5 py-2 rounded-xl bg-muted text-xs border border-border">
              <span class="w-2 h-2 rounded-full bg-emerald-500 shrink-0"></span>
              <span class="font-semibold truncate">{{ authStore.user?.first_name }} {{ authStore.user?.last_name }}</span>
            </div>
            <div class="flex flex-wrap gap-1">
              <span
                v-for="r in authStore.user?.roles"
                :key="r"
                class="px-1.5 py-0.5 rounded text-[10px] bg-primary/10 text-primary border border-primary/20 font-semibold"
              >
                {{ r }}
              </span>
            </div>
          </div>
        </aside>
      </div>
    </Teleport>

    <!-- Logout Confirmation Modal Dialog -->
    <Teleport to="body">
      <div
        v-if="showLogoutConfirm"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-xs transition-opacity animate-in fade-in"
        role="dialog"
        aria-modal="true"
        aria-labelledby="logout-dialog-title"
      >
        <div class="w-full max-w-md bg-card text-card-foreground rounded-2xl border border-border shadow-2xl p-6 space-y-5 animate-in zoom-in-95">
          <div class="flex items-start gap-4">
            <div class="w-11 h-11 rounded-xl bg-destructive/15 text-destructive flex items-center justify-center shrink-0">
              <AlertTriangle class="w-6 h-6" />
            </div>
            <div class="space-y-1.5">
              <h3 id="logout-dialog-title" class="text-lg font-bold text-foreground leading-snug">
                ¿Cerrar sesión activa?
              </h3>
              <p class="text-sm text-muted-foreground leading-relaxed">
                Tu sesión se invalidará de forma segura. Tendrás que volver a autenticarte para operar en la plataforma.
              </p>
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 pt-2">
            <Button
              variant="outline"
              class="rounded-xl"
              :disabled="isLoggingOut"
              @click="cancelLogout"
            >
              Cancelar
            </Button>

            <Button
              variant="destructive"
              class="rounded-xl gap-2 shadow-xs cursor-pointer"
              :disabled="isLoggingOut"
              @click="handleLogout"
            >
              <Loader2 v-if="isLoggingOut" class="w-4 h-4 animate-spin" />
              <LogOut v-else class="w-4 h-4" />
              <span>{{ isLoggingOut ? 'Cerrando sesión...' : 'Confirmar salida' }}</span>
            </Button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Footer -->
    <footer class="border-t border-border py-4 text-center text-xs text-muted-foreground mt-auto">
      BoletoYa (PIC) — Gestión de Usuarios, Roles y Permisos
    </footer>
  </div>
</template>
