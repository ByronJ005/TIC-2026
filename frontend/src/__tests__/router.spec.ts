import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import router from '@/router'
import { AUTH_TOKEN_KEY } from '@/services/api-client'

describe('Router Navigation Guards', () => {
  beforeEach(async () => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('14.7: redirects unauthenticated users from /dashboard to /login', async () => {
    localStorage.removeItem(AUTH_TOKEN_KEY)
    await router.push('/login') // reset current route
    await router.push('/dashboard')
    expect(router.currentRoute.value.name).toBe('login')
  })

  it('14.7: redirects authenticated users from /login to /dashboard', async () => {
    // Start at a route other than /login
    localStorage.removeItem(AUTH_TOKEN_KEY)
    await router.push('/dashboard') // will be at /login
    // Now simulate user having token and trying to navigate to /login from outside
    localStorage.setItem(AUTH_TOKEN_KEY, 'valid-test-token')
    await router.push('/register') // now navigating to guest route
    expect(router.currentRoute.value.name).toBe('dashboard')

    // Navigate to /login from /dashboard
    await router.push('/login')
    expect(router.currentRoute.value.name).toBe('dashboard')
  })

  it('14.7: redirects authenticated users from /register to /dashboard', async () => {
    localStorage.setItem(AUTH_TOKEN_KEY, 'valid-test-token')
    await router.push('/dashboard') // already on dashboard
    await router.push('/register')
    expect(router.currentRoute.value.name).toBe('dashboard')
  })
})
