import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import ResetPasswordView from '@/views/ResetPasswordView.vue'
import { PasswordRecoveryService } from '@/services/password-recovery.service'
import {
  ERROR_INVALID_PASSWORD,
  ERROR_PASSWORD_CONFIRMATION_MISMATCH,
  ERROR_REQUIRED_FIELD,
} from '@/composables/useFormValidation'

const INVALID_LINK_MESSAGE = 'El enlace de restablecimiento es inválido o ha expirado'

async function mountView(url: string) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/login', name: 'login', component: { template: '<div />' } },
      { path: '/forgot-password', name: 'forgot-password', component: { template: '<div />' } },
      { path: '/reset-password', name: 'reset-password', component: ResetPasswordView },
    ],
  })
  await router.push(url)
  await router.isReady()
  return mount(ResetPasswordView, { global: { plugins: [router] } })
}

async function submitPasswords(
  wrapper: Awaited<ReturnType<typeof mountView>>,
  password: string,
  confirmation: string,
) {
  await wrapper.find('#reset-new-password').setValue(password)
  await wrapper.find('#reset-confirm-password').setValue(confirmation)
  await wrapper.find('form').trigger('submit')
  await flushPromises()
}

describe('ResetPasswordView', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('shows the invalid link state when there is no token in the URL', async () => {
    const wrapper = await mountView('/reset-password')

    expect(wrapper.text()).toContain(INVALID_LINK_MESSAGE)
    expect(wrapper.find('form').exists()).toBe(false)
    expect(wrapper.find('a[href="/forgot-password"]').exists()).toBe(true)
  })

  it('shows the invalid link state for an empty token parameter', async () => {
    const wrapper = await mountView('/reset-password?token=')

    expect(wrapper.find('form').exists()).toBe(false)
  })

  it('shows the form when a token is present', async () => {
    const wrapper = await mountView('/reset-password?token=abc123')

    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('rejects a password with invalid format without calling the API', async () => {
    const spy = vi.spyOn(PasswordRecoveryService, 'resetPassword')
    const wrapper = await mountView('/reset-password?token=abc123')

    await submitPasswords(wrapper, 'corta1A', 'corta1A')

    expect(wrapper.text()).toContain(ERROR_INVALID_PASSWORD)
    expect(spy).not.toHaveBeenCalled()
  })

  it('rejects an empty password with the required message', async () => {
    const spy = vi.spyOn(PasswordRecoveryService, 'resetPassword')
    const wrapper = await mountView('/reset-password?token=abc123')

    await submitPasswords(wrapper, '   ', '   ')

    expect(wrapper.text()).toContain(ERROR_REQUIRED_FIELD)
    expect(spy).not.toHaveBeenCalled()
  })

  it('rejects a confirmation that does not match', async () => {
    const spy = vi.spyOn(PasswordRecoveryService, 'resetPassword')
    const wrapper = await mountView('/reset-password?token=abc123')

    await submitPasswords(wrapper, 'NewPass456', 'NewPass457')

    expect(wrapper.text()).toContain(ERROR_PASSWORD_CONFIRMATION_MISMATCH)
    expect(spy).not.toHaveBeenCalled()
  })

  it('CP-34: sends token and new password, then shows success and a login link', async () => {
    const spy = vi
      .spyOn(PasswordRecoveryService, 'resetPassword')
      .mockResolvedValue({ message: 'Contraseña restablecida exitosamente' })
    const wrapper = await mountView('/reset-password?token=abc123')

    await submitPasswords(wrapper, 'NewPass456', 'NewPass456')

    expect(spy).toHaveBeenCalledWith('abc123', 'NewPass456')
    expect(wrapper.text()).toContain('Contraseña restablecida exitosamente')
    expect(wrapper.find('form').exists()).toBe(false)
    expect(wrapper.find('a[href="/login"]').exists()).toBe(true)
  })

  it('switches to the invalid link state when the server says the link expired or was used', async () => {
    vi.spyOn(PasswordRecoveryService, 'resetPassword').mockRejectedValue({
      status: 400,
      message: INVALID_LINK_MESSAGE,
    })
    const wrapper = await mountView('/reset-password?token=expired')

    await submitPasswords(wrapper, 'NewPass456', 'NewPass456')

    expect(wrapper.text()).toContain(INVALID_LINK_MESSAGE)
    expect(wrapper.find('form').exists()).toBe(false)
    expect(wrapper.find('a[href="/forgot-password"]').exists()).toBe(true)
  })

  it('keeps the form when the server fails for another reason', async () => {
    vi.spyOn(PasswordRecoveryService, 'resetPassword').mockRejectedValue({
      status: 500,
      message: 'Error HTTP 500',
    })
    const wrapper = await mountView('/reset-password?token=abc123')

    await submitPasswords(wrapper, 'NewPass456', 'NewPass456')

    expect(wrapper.find('form').exists()).toBe(true)
    expect(wrapper.text()).toContain('Error HTTP 500')
  })
})

