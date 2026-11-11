import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ProfileView from '@/views/ProfileView.vue'
import { ProfileService } from '@/services/profile.service'
import { ERROR_MANDATORY_FIELDS_EMPTY, toIsoDate } from '@/composables/useFormValidation'
import type { User } from '@/services/auth.service'
import { useAuthStore } from '@/stores/auth.store'

const user: User = {
  id: 1,
  document_type: 'CEDULA',
  document_number: '1710034065',
  first_name: 'Ana',
  last_name: 'Gomez',
  email: 'ana@example.com',
  roles: ['PASAJERO'],
  is_active: true,
  phone: '0991234567',
  address: 'Calle Falsa 123',
  birth_date: '1990-05-20',
  created_at: '',
  updated_at: '',
}

async function mountView() {
  const authStore = useAuthStore()
  authStore.user = user
  const wrapper = mount(ProfileView)
  await flushPromises()
  return wrapper
}

describe('ProfileView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it('shows current data and disables email and document', async () => {
    const wrapper = await mountView()

    expect((wrapper.find('#profile-first-name').element as HTMLInputElement).value).toBe('Ana')
    expect((wrapper.find('#profile-phone').element as HTMLInputElement).value).toBe('0991234567')
    expect(wrapper.find('#profile-email').attributes('disabled')).toBeDefined()
    expect(wrapper.find('#profile-document').attributes('disabled')).toBeDefined()
  })

  it('sets the birth date max attribute to today and min to 1900-01-01', async () => {
    const wrapper = await mountView()
    const birthDateInput = wrapper.find('#profile-birth-date')

    expect(birthDateInput.attributes('max')).toBe(toIsoDate(new Date()))
    expect(birthDateInput.attributes('min')).toBe('1900-01-01')
  })

  it('CP-42: empty first name shows the mandatory message and restores previous data', async () => {
    const spy = vi.spyOn(ProfileService, 'updateProfile')
    const wrapper = await mountView()

    await wrapper.find('#profile-first-name').setValue('   ')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.text()).toContain(ERROR_MANDATORY_FIELDS_EMPTY)
    expect((wrapper.find('#profile-first-name').element as HTMLInputElement).value).toBe('Ana')
    expect(spy).not.toHaveBeenCalled()
  })

  it('CP-37: shows the success notification after updating', async () => {
    vi.spyOn(ProfileService, 'updateProfile').mockResolvedValue({
      user: { ...user, first_name: 'Anita' },
      message: 'Perfil actualizado exitosamente',
      access_token: null,
      token_type: null,
    })
    const wrapper = await mountView()

    await wrapper.find('#profile-first-name').setValue('Anita')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('Perfil actualizado exitosamente')
  })

  it('shows the field error under the phone input and does not call the API', async () => {
    const spy = vi.spyOn(ProfileService, 'updateProfile')
    const wrapper = await mountView()

    await wrapper.find('#profile-phone').setValue('123')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.text()).toContain('El número de celular debe tener exactamente 10 dígitos')
    expect(spy).not.toHaveBeenCalled()
  })

  it('requires the current password when a new password is typed', async () => {
    const spy = vi.spyOn(ProfileService, 'updateProfile')
    const wrapper = await mountView()

    await wrapper.find('#profile-new-password').setValue('NewPass456')
    await wrapper.find('#profile-confirm-password').setValue('NewPass456')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.text()).toContain('Debe ingresar su contraseña actual para cambiarla')
    expect(spy).not.toHaveBeenCalled()
  })

  it('disables the submit button while saving', async () => {
    let resolveRequest: (value: Awaited<ReturnType<typeof ProfileService.updateProfile>>) => void =
      () => {}
    vi.spyOn(ProfileService, 'updateProfile').mockReturnValue(
      new Promise((resolve) => {
        resolveRequest = resolve
      }),
    )
    const wrapper = await mountView()

    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()

    resolveRequest({ user, message: 'Perfil actualizado exitosamente', access_token: null, token_type: null })
    await flushPromises()
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeUndefined()
  })
})

