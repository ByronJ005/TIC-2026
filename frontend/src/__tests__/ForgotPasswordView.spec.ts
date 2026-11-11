import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import ForgotPasswordView from '@/views/ForgotPasswordView.vue'
import { PasswordRecoveryService } from '@/services/password-recovery.service'
import { ERROR_EMAIL_REQUIRED, ERROR_INVALID_EMAIL } from '@/composables/useFormValidation'

const PROCESSED_MESSAGE =
  'Hemos procesado tu solicitud. Si el correo corresponde a una cuenta activa, recibirás un enlace en los próximos minutos.'
const NOT_REGISTERED_MESSAGE =
  'El correo ingresado no corresponde a una cuenta registrada en el sistema'

async function mountView() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/login', name: 'login', component: { template: '<div />' } },
      { path: '/forgot-password', name: 'forgot-password', component: ForgotPasswordView },
    ],
  })
  await router.push('/forgot-password')
  await router.isReady()
  return mount(ForgotPasswordView, { global: { plugins: [router] } })
}

describe('ForgotPasswordView', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('CP-36: blank or spaces-only email shows the required message without calling the API', async () => {
    const spy = vi.spyOn(PasswordRecoveryService, 'forgotPassword')
    const wrapper = await mountView()

    await wrapper.find('#forgot-email').setValue('   ')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.text()).toContain(ERROR_EMAIL_REQUIRED)
    expect(spy).not.toHaveBeenCalled()
  })

  it('shows the invalid format message for an email without @', async () => {
    const spy = vi.spyOn(PasswordRecoveryService, 'forgotPassword')
    const wrapper = await mountView()

    await wrapper.find('#forgot-email').setValue('sin-arroba')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.text()).toContain(ERROR_INVALID_EMAIL)
    expect(spy).not.toHaveBeenCalled()
  })

  it('CP-33: sends the normalized email and shows the processed message', async () => {
    const spy = vi
      .spyOn(PasswordRecoveryService, 'forgotPassword')
      .mockResolvedValue({ message: PROCESSED_MESSAGE })
    const wrapper = await mountView()

    await wrapper.find('#forgot-email').setValue('  Ana@Example.COM ')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(spy).toHaveBeenCalledWith('ana@example.com')
    expect(wrapper.text()).toContain(PROCESSED_MESSAGE)
  })

  it('CP-35: shows the unregistered email error from the server', async () => {
    vi.spyOn(PasswordRecoveryService, 'forgotPassword').mockRejectedValue({
      status: 404,
      message: NOT_REGISTERED_MESSAGE,
    })
    const wrapper = await mountView()

    await wrapper.find('#forgot-email').setValue('nadie@example.com')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain(NOT_REGISTERED_MESSAGE)
    expect(wrapper.text()).not.toContain(PROCESSED_MESSAGE)
  })

  it('disables the submit button while the request is in flight', async () => {
    let resolveRequest: (value: { message: string }) => void = () => {}
    vi.spyOn(PasswordRecoveryService, 'forgotPassword').mockReturnValue(
      new Promise((resolve) => {
        resolveRequest = resolve
      }),
    )
    const wrapper = await mountView()

    await wrapper.find('#forgot-email').setValue('ana@example.com')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()

    resolveRequest({ message: PROCESSED_MESSAGE })
    await flushPromises()
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeUndefined()
  })

  it('shows a connection error message when the server cannot be reached', async () => {
    vi.spyOn(PasswordRecoveryService, 'forgotPassword').mockRejectedValue({
      status: 0,
      message: 'No se pudo conectar con el servidor. Verifica tu conexión.',
    })
    const wrapper = await mountView()

    await wrapper.find('#forgot-email').setValue('ana@example.com')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('No se pudo conectar con el servidor')
  })

  it('offers a link back to the login screen', async () => {
    const wrapper = await mountView()

    expect(wrapper.find('a[href="/login"]').exists()).toBe(true)
  })
})

