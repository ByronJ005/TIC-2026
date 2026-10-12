import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import {
  AUTH_TOKEN_KEY,
  AUTH_USER_KEY,
  setUnauthorizedHandler,
} from '@/services/api-client'
import {
  AuthService,
  type LoginCredentials,
  type RegisterData,
  type User,
} from '@/services/auth.service'
import router from '@/router'

function getSavedUser(): User | null {
  if (typeof localStorage === 'undefined') return null
  const savedUser = localStorage.getItem(AUTH_USER_KEY)
  if (savedUser) {
    try {
      return JSON.parse(savedUser) as User
    } catch {
      return null
    }
  }
  return null
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(
    typeof localStorage !== 'undefined'
      ? localStorage.getItem(AUTH_TOKEN_KEY)
      : null,
  )
  const user = ref<User | null>(getSavedUser())

  const sessionExpiredMessage = ref<string | null>(null)
  const isInitializing = ref(false)

  const isAuthenticated = computed(() => Boolean(token.value))

  function setToken(newToken: string | null) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem(AUTH_TOKEN_KEY, newToken)
    } else {
      localStorage.removeItem(AUTH_TOKEN_KEY)
    }
  }

  function setUser(newUser: User | null) {
    user.value = newUser
    if (newUser) {
      localStorage.setItem(AUTH_USER_KEY, JSON.stringify(newUser))
    } else {
      localStorage.removeItem(AUTH_USER_KEY)
    }
  }

  async function register(data: RegisterData): Promise<User> {
    const createdUser = await AuthService.register(data)
    return createdUser
  }

  async function login(credentials: LoginCredentials): Promise<void> {
    sessionExpiredMessage.value = null
    const response = await AuthService.login(credentials)
    setToken(response.access_token)

    try {
      const profile = await AuthService.getProfile()
      setUser(profile)
    } catch {
      // If fetching profile fails immediately, user is set on next request
    }
  }

  async function logout(silent: boolean = false): Promise<void> {
    if (token.value && !silent) {
      try {
        await AuthService.logout()
      } catch {
        // Ignore API errors on logout (graceful)
      }
    }

    setToken(null)
    setUser(null)

    if (router.currentRoute.value.meta.requiresAuth) {
      router.push({ name: 'login' })
    }
  }

  async function checkAuth(): Promise<boolean> {
    if (!token.value) {
      setUser(null)
      return false
    }

    try {
      isInitializing.value = true
      const profile = await AuthService.getProfile()
      setUser(profile)
      return true
    } catch {
      setToken(null)
      setUser(null)
      return false
    } finally {
      isInitializing.value = false
    }
  }

  // Multi-tab synchronization
  function initMultiTabSync() {
    if (typeof window !== 'undefined') {
      window.addEventListener('storage', (event) => {
        if (event.key === AUTH_TOKEN_KEY) {
          if (!event.newValue && token.value) {
            // Token was removed in another tab -> logout locally
            token.value = null
            user.value = null
            sessionExpiredMessage.value = 'Sesión expirada'
            if (router.currentRoute.value.meta.requiresAuth) {
              router.push({
                name: 'login',
                query: { message: 'session_expired' },
              })
            }
          } else if (event.newValue && event.newValue !== token.value) {
            // Token was updated in another tab
            token.value = event.newValue
            checkAuth()
          }
        }
      })
    }
  }

  // Handle automatic 401s from API client
  setUnauthorizedHandler((message) => {
    token.value = null
    user.value = null
    sessionExpiredMessage.value = message
    if (router.currentRoute.value.name !== 'login') {
      router.push({ name: 'login', query: { message: 'session_expired' } })
    }
  })

  // Initialize multi-tab listener
  initMultiTabSync()

  return {
    token,
    user,
    isAuthenticated,
    isInitializing,
    sessionExpiredMessage,
    register,
    login,
    logout,
    checkAuth,
    setToken,
    setUser,
  }
})
