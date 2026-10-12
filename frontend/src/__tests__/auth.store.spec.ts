import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAuthStore } from '@/stores/auth.store'
import { AuthService, type User } from '@/services/auth.service'
import { AUTH_TOKEN_KEY, AUTH_USER_KEY } from '@/services/api-client'

describe('useAuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it('14.5: login updates token, user, isAuthenticated and persists to localStorage', async () => {
    const mockUser: User = {
      id: 1,
      document_type: 'CEDULA',
      document_number: '1710034065',
      first_name: 'Carlos',
      last_name: 'Mora',
      email: 'carlos@example.com',
      role: 'PASAJERO',
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    vi.spyOn(AuthService, 'login').mockResolvedValue({
      access_token: 'fake-jwt-token-123',
      token_type: 'bearer',
    })
    vi.spyOn(AuthService, 'getProfile').mockResolvedValue(mockUser)

    const store = useAuthStore()
    expect(store.isAuthenticated).toBe(false)

    await store.login({
      email: 'carlos@example.com',
      password: 'Password123',
    })

    expect(store.token).toBe('fake-jwt-token-123')
    expect(store.user).toEqual(mockUser)
    expect(store.isAuthenticated).toBe(true)
    expect(localStorage.getItem(AUTH_TOKEN_KEY)).toBe('fake-jwt-token-123')
    expect(localStorage.getItem(AUTH_USER_KEY)).toContain('carlos@example.com')
  })

  it('14.6: logout clears token, user, isAuthenticated and removes from localStorage', async () => {
    vi.spyOn(AuthService, 'logout').mockResolvedValue({
      message: 'Sesión cerrada satisfactoriamente',
    })

    const store = useAuthStore()
    store.setToken('fake-jwt-token-123')
    store.setUser({
      id: 1,
      document_type: 'CEDULA',
      document_number: '1710034065',
      first_name: 'Carlos',
      last_name: 'Mora',
      email: 'carlos@example.com',
      role: 'PASAJERO',
      is_active: true,
      created_at: '',
      updated_at: '',
    })

    expect(store.isAuthenticated).toBe(true)

    await store.logout()

    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(localStorage.getItem(AUTH_TOKEN_KEY)).toBeNull()
    expect(localStorage.getItem(AUTH_USER_KEY)).toBeNull()
  })
})
