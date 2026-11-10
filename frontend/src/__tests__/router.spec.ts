import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import router from '@/router'
import { AUTH_TOKEN_KEY, AUTH_USER_KEY } from '@/services/api-client'

describe('Router Navigation Guards & Role Protection', () => {
  beforeEach(async () => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('14.7: redirects unauthenticated users from /dashboard to /login', async () => {
    localStorage.removeItem(AUTH_TOKEN_KEY)
    await router.push('/login')
    await router.push('/dashboard')
    expect(router.currentRoute.value.name).toBe('login')
  })

  it('14.7: redirects authenticated users from /login to /dashboard', async () => {
    localStorage.removeItem(AUTH_TOKEN_KEY)
    await router.push('/dashboard')
    localStorage.setItem(AUTH_TOKEN_KEY, 'valid-test-token')
    await router.push('/register')
    expect(router.currentRoute.value.name).toBe('dashboard')

    await router.push('/login')
    expect(router.currentRoute.value.name).toBe('dashboard')
  })

  it('V-16: redirects unauthenticated access to /dashboard/usuarios to /login', async () => {
    localStorage.removeItem(AUTH_TOKEN_KEY)
    await router.push('/dashboard/usuarios')
    expect(router.currentRoute.value.name).toBe('login')
  })

  it('V-17: redirects unauthorized role (PASAJERO) from /dashboard/usuarios to /dashboard', async () => {
    localStorage.setItem(AUTH_TOKEN_KEY, 'valid-test-token')
    localStorage.setItem(
      AUTH_USER_KEY,
      JSON.stringify({ id: 1, roles: ['PASAJERO'] }),
    )

    await router.push('/dashboard/usuarios')
    expect(router.currentRoute.value.name).toBe('dashboard')
  })

  it('V-18: permits authorized role (ADMIN_GENERAL) to access /dashboard/usuarios', async () => {
    localStorage.setItem(AUTH_TOKEN_KEY, 'valid-test-token')
    localStorage.setItem(
      AUTH_USER_KEY,
      JSON.stringify({ id: 1, roles: ['ADMIN_GENERAL', 'PASAJERO'] }),
    )

    await router.push('/dashboard/usuarios')
    expect(router.currentRoute.value.name).toBe('users')
  })
})
