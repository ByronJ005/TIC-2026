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

  it('S3-01: /forgot-password and /reset-password are reachable without a session', async () => {
    localStorage.removeItem(AUTH_TOKEN_KEY)

    await router.push('/forgot-password')
    expect(router.currentRoute.value.name).toBe('forgot-password')

    await router.push('/reset-password?token=abc')
    expect(router.currentRoute.value.name).toBe('reset-password')
    expect(router.currentRoute.value.query.token).toBe('abc')
  })

  it('S3-02: authenticated users are redirected from recovery routes to /dashboard', async () => {
    localStorage.setItem(AUTH_TOKEN_KEY, 'valid-test-token')

    await router.push('/forgot-password')
    expect(router.currentRoute.value.name).toBe('dashboard')

    await router.push('/reset-password?token=abc')
    expect(router.currentRoute.value.name).toBe('dashboard')
  })

  it('S3-03: /dashboard/perfil requires a session and is available for any user', async () => {
    localStorage.removeItem(AUTH_TOKEN_KEY)
    await router.push('/dashboard/perfil')
    expect(router.currentRoute.value.name).toBe('login')

    localStorage.setItem(AUTH_TOKEN_KEY, 'valid-test-token')
    localStorage.setItem(
      AUTH_USER_KEY,
      JSON.stringify({ id: 1, roles: ['ADMIN_GENERAL', 'PASAJERO'] }),
    )
    await router.push('/dashboard/perfil')
    expect(router.currentRoute.value.name).toBe('perfil')
  })
})
