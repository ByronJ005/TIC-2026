import { defineComponent } from 'vue'
import { createPinia } from 'pinia'
import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import RouteFormDialog from '@/components/rutas/RouteFormDialog.vue'
import GeneralRoutesTable from '@/components/rutas/GeneralRoutesTable.vue'
import RutasGeneralesView from '@/views/RutasGeneralesView.vue'
import RutasCooperativaView from '@/views/RutasCooperativaView.vue'
import { useRouteSubmission } from '@/composables/useRouteSubmission'
import * as routesApi from '@/services/rutas.service'
import type { RouteDetail } from '@/services/rutas.service'

vi.mock('@/stores/auth.store', () => ({
  useAuthStore: () => ({ user: { cooperativa_id: 7 } }),
}))

const route: RouteDetail = {
  id: 10, cooperativa_id: null, origin_id: 1, destination_id: 2,
  origin_name: 'Loja', destination_name: 'Cuenca', name: 'Loja - Cuenca',
  distance_km: 210, estimated_time_minutes: 240, is_active: true,
  created_at: '', updated_at: '', stops: [], has_associations: false,
}
const LocalityStub = defineComponent({
  name: 'LocalityCombobox', props: ['error'], emits: ['selected'],
  template: '<div>{{ error }}</div>',
})

beforeEach(() => {
  vi.spyOn(routesApi, 'getGeneralRoutes').mockResolvedValue({
    items: [route], total: 1, page: 1, size: 10, total_pages: 1,
  })
  vi.spyOn(routesApi, 'getSpecificRoutesSupervision').mockResolvedValue([])
  vi.spyOn(routesApi, 'getAdoptedGeneralRoutes').mockResolvedValue([])
  vi.spyOn(routesApi, 'getSpecificRoutes').mockResolvedValue([route])
  vi.spyOn(routesApi, 'getRouteDetail').mockResolvedValue(route)
})

afterEach(() => vi.restoreAllMocks())

describe.each([
  { scope: 'general', view: RutasGeneralesView, create: 'createGeneralRoute', update: 'updateGeneralRoute', button: 'new-general-route-btn' },
  { scope: 'cooperativa', view: RutasCooperativaView, create: 'createSpecificRoute', update: 'updateSpecificRoute', button: 'new-specific-route-btn' },
] as const)('Route submission in $scope view', ({ scope, view, create, update, button }) => {
  function mountView() {
    return mount(view, {
      global: {
        plugins: [createPinia()],
        stubs: { LocalityCombobox: LocalityStub, GeneralRoutesTable: true, RouteDetailDialog: true, GeneralRoutesPickerModal: true },
      },
    })
  }

  it('keeps the form and inputs after rejection, then closes after a successful retry', async () => {
    const save = vi.spyOn(routesApi, create)
      .mockRejectedValueOnce({ status: 409, message: 'Ya existe una ruta con este origen y destino' })
      .mockResolvedValueOnce(route)
    const wrapper = mountView()
    await flushPromises()
    await wrapper.get(`[data-test="${button}"]`).trigger('click')
    const form = wrapper.getComponent(RouteFormDialog)
    const localities = form.findAllComponents(LocalityStub)
    localities[0]!.vm.$emit('selected', { id: 1, name: 'Loja' })
    localities[1]!.vm.$emit('selected', { id: 2, name: 'Cuenca' })
    await form.get('[data-test="distance-km-input"]').setValue('210')
    await form.get('[data-test="time-hours-input"]').setValue('4')
    await form.get('[data-test="save-route-btn"]').trigger('click')
    await flushPromises()
    expect(form.props('isOpen')).toBe(true)
    expect(form.get('[role="alert"]').text()).toContain('Ya existe una ruta')
    expect((form.get('[data-test="distance-km-input"]').element as HTMLInputElement).value).toBe('210')
    expect((form.get('[data-test="time-hours-input"]').element as HTMLInputElement).value).toBe('4')
    expect(form.get('[data-test="save-route-btn"]').attributes('disabled')).toBeUndefined()
    await form.get('[data-test="save-route-btn"]').trigger('click')
    await flushPromises()
    expect(save).toHaveBeenCalledTimes(2)
    expect(save.mock.calls[0]).toEqual(save.mock.calls[1])
    expect(form.props('isOpen')).toBe(false)
    await wrapper.get(`[data-test="${button}"]`).trigger('click')
    expect(form.find('[role="alert"]').exists()).toBe(false)
    wrapper.unmount()
  })

  it('shows API validation errors when editing and preserves the modified data', async () => {
    const save = vi.spyOn(routesApi, update).mockRejectedValue({ status: 422, message: 'Revise la distancia ingresada' })
    const wrapper = mountView()
    await flushPromises()
    if (scope === 'general') {
      wrapper.getComponent(GeneralRoutesTable).vm.$emit('edit', route)
    } else {
      await wrapper.get('[data-test="edit-specific-route-btn"]').trigger('click')
    }
    await flushPromises()
    const form = wrapper.getComponent(RouteFormDialog)
    await form.get('[data-test="distance-km-input"]').setValue('211')
    await form.get('[data-test="save-route-btn"]').trigger('click')
    await flushPromises()
    expect(save).toHaveBeenCalledWith(10, expect.objectContaining({ distance_km: 211 }))
    expect(form.props('isOpen')).toBe(true)
    expect(form.get('[role="alert"]').text()).toContain('Revise la distancia ingresada')
    expect((form.get('[data-test="distance-km-input"]').element as HTMLInputElement).value).toBe('211')
    wrapper.unmount()
  })
})

describe('Submission error handling', () => {
  it.each([
    [{ status: 0, message: 'Connection refused' }, 'No se pudo conectar con el servidor. Verifica tu conexión.'],
    [{ status: 500, message: 'SQL exception' }, 'No se pudo guardar la ruta. Inténtelo nuevamente.'],
    [new Error('Technical failure'), 'No se pudo guardar la ruta. Inténtelo nuevamente.'],
  ])('provides a user-facing message for %j', async (error, message) => {
    const submission = useRouteSubmission()
    expect(await submission.submitRoute(() => Promise.reject(error))).toBe(false)
    expect(submission.submitError.value).toBe(message)
    expect(submission.isSubmitting.value).toBe(false)
  })

  it('prevents duplicate submissions while saving', async () => {
    const submission = useRouteSubmission()
    let finish!: () => void
    const save = vi.fn<() => Promise<void>>(() => new Promise<void>(resolve => { finish = resolve }))
    const pending = submission.submitRoute(save)
    expect(submission.isSubmitting.value).toBe(true)
    expect(await submission.submitRoute(save)).toBe(false)
    expect(save).toHaveBeenCalledTimes(1)
    finish()
    expect(await pending).toBe(true)
    expect(submission.isSubmitting.value).toBe(false)
  })

  it('does not offer a second create when only the list refresh fails', async () => {
    const save = vi.spyOn(routesApi, 'createGeneralRoute').mockResolvedValue(route)
    const wrapper = mount(RutasGeneralesView, {
      global: {
        plugins: [createPinia()],
        stubs: { RouteFormDialog: true, GeneralRoutesTable: true, RouteDetailDialog: true },
      },
    })
    await flushPromises()
    vi.mocked(routesApi.getGeneralRoutes).mockRejectedValueOnce({ status: 500 })
    await wrapper.get('[data-test="new-general-route-btn"]').trigger('click')
    const form = wrapper.getComponent(RouteFormDialog)
    form.vm.$emit('submit', { origin_id: 1, destination_id: 2, distance_km: 210, estimated_time_minutes: 240 })
    await flushPromises()
    expect(save).toHaveBeenCalledTimes(1)
    expect(form.props('isOpen')).toBe(false)
    expect(wrapper.text()).toContain('La ruta se guardó, pero no se pudo actualizar el listado')
    wrapper.unmount()
  })
})
