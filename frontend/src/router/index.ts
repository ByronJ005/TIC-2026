import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { AUTH_TOKEN_KEY, AUTH_USER_KEY } from '@/services/api-client'
import type { UserRole } from '@/services/auth.service'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import DashboardLayout from '@/views/DashboardLayout.vue'
import DashboardHomeView from '@/views/DashboardHomeView.vue'
import ModulePlaceholderView from '@/views/ModulePlaceholderView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: () => {
      const hasToken = Boolean(localStorage.getItem(AUTH_TOKEN_KEY))
      return hasToken ? { name: 'dashboard' } : { name: 'login' }
    },
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: {
      guestOnly: true,
      title: 'Iniciar Sesión - BoletoYa',
    },
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: {
      guestOnly: true,
      title: 'Registro - BoletoYa',
    },
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: () => import('@/views/ForgotPasswordView.vue'),
    meta: {
      guestOnly: true,
      title: 'Recuperar contraseña - BoletoYa',
    },
  },
  {
    path: '/reset-password',
    name: 'reset-password',
    component: () => import('@/views/ResetPasswordView.vue'),
    meta: {
      guestOnly: true,
      title: 'Nueva contraseña - BoletoYa',
    },
  },
  {
    path: '/dashboard',
    component: DashboardLayout,
    meta: {
      requiresAuth: true,
    },
    children: [
      {
        path: '',
        name: 'dashboard',
        component: DashboardHomeView,
        meta: {
          title: 'Inicio - BoletoYa',
        },
      },
      {
        path: 'usuarios',
        name: 'users',
        component: () => import('@/views/UsersView.vue'),
        meta: {
          title: 'Usuarios - BoletoYa',
          requiresRoles: ['ADMIN_GENERAL'] as UserRole[],
        },
      },
      {
        path: 'cooperativas',
        name: 'cooperativas',
        component: ModulePlaceholderView,
        meta: {
          title: 'Cooperativas - BoletoYa',
          description: 'Gestión de cooperativas afiliadas al terminal terrestre.',
          requiresRoles: ['ADMIN_GENERAL'] as UserRole[],
        },
      },
      {
        path: 'rutas-generales',
        name: 'rutas-generales',
        component: ModulePlaceholderView,
        meta: {
          title: 'Rutas generales - BoletoYa',
          description: 'Administración de rutas interprovinciales y destinos base.',
          requiresRoles: ['ADMIN_GENERAL'] as UserRole[],
        },
      },
      {
        path: 'precios-generales',
        name: 'precios-generales',
        component: ModulePlaceholderView,
        meta: {
          title: 'Precios generales - BoletoYa',
          description: 'Gestión de tarifas y precios base aplicables a todas las cooperativas.',
          requiresRoles: ['ADMIN_GENERAL'] as UserRole[],
        },
      },
      {
        path: 'rutas-cooperativa',
        name: 'rutas-cooperativa',
        component: ModulePlaceholderView,
        meta: {
          title: 'Rutas de cooperativa - BoletoYa',
          description: 'Gestión de rutas asignadas a la cooperativa propia.',
          requiresRoles: ['ADMIN_COOPERATIVA'] as UserRole[],
        },
      },
      {
        path: 'buses',
        name: 'buses',
        component: ModulePlaceholderView,
        meta: {
          title: 'Buses - BoletoYa',
          description: 'Administración de unidades vehiculares y distribución de asientos.',
          requiresRoles: ['ADMIN_COOPERATIVA'] as UserRole[],
        },
      },
      {
        path: 'turnos',
        name: 'turnos',
        component: ModulePlaceholderView,
        meta: {
          title: 'Turnos - BoletoYa',
          description: 'Programación de horarios y asignación de viajes de buses.',
          requiresRoles: ['ADMIN_COOPERATIVA'] as UserRole[],
        },
      },
      {
        path: 'tarifas',
        name: 'tarifas',
        component: ModulePlaceholderView,
        meta: {
          title: 'Tarifas específicas - BoletoYa',
          description: 'Gestión de precios por boleto y descuentos autorizados.',
          requiresRoles: ['ADMIN_COOPERATIVA'] as UserRole[],
        },
      },
      {
        path: 'reservas',
        name: 'reservas',
        component: ModulePlaceholderView,
        meta: {
          title: 'Reservas - BoletoYa',
          description: 'Consulta, reserva de asientos y confirmación de boletos.',
          requiresRoles: ['SECRETARIA_COOPERATIVA', 'PASAJERO'] as UserRole[],
        },
      },
      {
        path: 'perfil',
        name: 'perfil',
        component: () => import('@/views/ProfileView.vue'),
        meta: {
          title: 'Perfil - BoletoYa',
          requiresRoles: ['PASAJERO'] as UserRole[],
        },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: { name: 'login' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

function getCurrentStoredUserRoles(): UserRole[] {
  if (typeof localStorage === 'undefined') return []
  const raw = localStorage.getItem(AUTH_USER_KEY)
  if (!raw) return []
  try {
    const user = JSON.parse(raw)
    return user.roles || (user.role ? [user.role] : [])
  } catch {
    return []
  }
}

// Global Navigation Guard for Route Protection
router.beforeEach((to) => {
  const token = localStorage.getItem(AUTH_TOKEN_KEY)
  const isAuthenticated = Boolean(token)

  // Document Title
  if (to.meta.title && typeof document !== 'undefined') {
    document.title = String(to.meta.title)
  }

  // Protected route accessed without session -> Redirect to login
  if (to.matched.some((record) => record.meta.requiresAuth) && !isAuthenticated) {
    return { name: 'login' }
  }

  // Guest-only route accessed with active session -> Redirect to dashboard
  if (to.meta.guestOnly && isAuthenticated) {
    return { name: 'dashboard' }
  }

  // Role-based protection on child routes
  if (to.meta.requiresRoles && Array.isArray(to.meta.requiresRoles)) {
    const allowed = to.meta.requiresRoles as UserRole[]
    const currentRoles = getCurrentStoredUserRoles()
    const hasPermission = allowed.some((role) => currentRoles.includes(role))

    if (!hasPermission) {
      return { name: 'dashboard' }
    }
  }

  return true
})

export default router
