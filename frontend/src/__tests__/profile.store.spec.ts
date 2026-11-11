import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { AUTH_TOKEN_KEY, AUTH_USER_KEY } from '@/services/api-client'
import type { User } from '@/services/auth.service'
import { ProfileService, type ProfileUpdateData } from '@/services/profile.service'
import { useAuthStore } from '@/stores/auth.store'
import { useProfileStore } from '@/stores/profile.store'

const updatedUser: User = {
  id: 1,
  document_type: 'CEDULA',
  document_number: '1710034065',
  first_name: 'Anita',
  last_name: 'Gomez',
  email: 'ana@example.com',
  roles: ['PASAJERO'],
  is_active: true,
  created_at: '',
  updated_at: '',
}

const payload: ProfileUpdateData = {
  first_name: 'Anita',
  last_name: 'Gomez',
  phone: '',
  address: '',
  birth_date: '',
  current_password: '',
  new_password: '',
  confirm_password: '',
}

describe('useProfileStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it('updates the stored user and keeps the token when the password did not change', async () => {
    vi.spyOn(ProfileService, 'updateProfile').mockResolvedValue({
      user: updatedUser,
      message: 'Perfil actualizado exitosamente',
      access_token: null,
      token_type: null,
    })
    const authStore = useAuthStore()
    authStore.setToken('old-token')

    await useProfileStore().updateProfile(payload)

    expect(authStore.token).toBe('old-token')
    expect(authStore.user?.first_name).toBe('Anita')
    expect(localStorage.getItem(AUTH_USER_KEY)).toContain('Anita')
  })

  it('replaces the token when the backend returns a fresh one', async () => {
    vi.spyOn(ProfileService, 'updateProfile').mockResolvedValue({
      user: updatedUser,
      message: 'Contraseña actualizada exitosamente',
      access_token: 'fresh-token',
      token_type: 'bearer',
    })
    const authStore = useAuthStore()
    authStore.setToken('old-token')

    await useProfileStore().updateProfile(payload)

    expect(authStore.token).toBe('fresh-token')
    expect(localStorage.getItem(AUTH_TOKEN_KEY)).toBe('fresh-token')
  })

  it('toggles isSaving and resets it after a failure, leaving the session untouched', async () => {
    let rejectRequest: (reason: unknown) => void = () => {}
    vi.spyOn(ProfileService, 'updateProfile').mockReturnValue(
      new Promise((_resolve, reject) => {
        rejectRequest = reject
      }),
    )
    const authStore = useAuthStore()
    authStore.setToken('old-token')
    const profileStore = useProfileStore()

    const pending = profileStore.updateProfile(payload)
    expect(profileStore.isSaving).toBe(true)
    rejectRequest({ status: 400, message: 'La contraseña actual es incorrecta' })

    await expect(pending).rejects.toMatchObject({ status: 400 })
    expect(profileStore.isSaving).toBe(false)
    expect(authStore.token).toBe('old-token')
    expect(authStore.user).toBeNull()
  })
})

