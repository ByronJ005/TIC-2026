import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { AUTH_TOKEN_KEY } from '@/services/api-client'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import DashboardView from '@/views/DashboardView.vue'

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
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
    meta: {
      requiresAuth: true,
      title: 'Dashboard - BoletoYa',
    },
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

// Global Navigation Guard for Route Protection
router.beforeEach((to) => {
  const token = localStorage.getItem(AUTH_TOKEN_KEY)
  const isAuthenticated = Boolean(token)

  // Document Title
  if (to.meta.title && typeof document !== 'undefined') {
    document.title = String(to.meta.title)
  }

  // Protected route accessed without session -> Redirect to login
  if (to.meta.requiresAuth && !isAuthenticated) {
    return { name: 'login' }
  }

  // Guest-only route accessed with active session -> Redirect to dashboard
  if (to.meta.guestOnly && isAuthenticated) {
    return { name: 'dashboard' }
  }

  return true
})

export default router
