import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import RouteFormDialog from '@/components/rutas/RouteFormDialog.vue'
import RouteTimeInput from '@/components/rutas/RouteTimeInput.vue'
import RouteStopsEditor from '@/components/rutas/RouteStopsEditor.vue'
import { useRouteForm } from '@/composables/useRouteForm'
import {
  ERROR_DESTINATION_REQUIRED,
  ERROR_DISTANCE_REQUIRED,
  ERROR_ORIGIN_REQUIRED,
  ERROR_ROUTE_ORIGIN_DESTINATION_SAME,
  ERROR_ROUTE_STOP_EQUALS_ORIGIN_OR_DESTINATION,
  ERROR_TIME_REQUIRED,
} from '@/composables/useFormValidation'

const LocalityStub = defineComponent({
  name: 'LocalityCombobox',
  props: ['error'],
  emits: ['selected'],
  template: '<div>{{ error }}</div>',
})

function mountForm() {
  return mount(RouteFormDialog, {
    props: { isOpen: true, route: null },
    global: { stubs: { LocalityCombobox: LocalityStub } },
  })
}

describe('Route form regression coverage', () => {
  it('shows each required field on save without emitting a submission', async () => {
    const wrapper = mountForm()
    await wrapper.get('[data-test="save-route-btn"]').trigger('click')
    for (const message of [ERROR_ORIGIN_REQUIRED, ERROR_DESTINATION_REQUIRED, ERROR_DISTANCE_REQUIRED, ERROR_TIME_REQUIRED]) {
      expect(wrapper.text()).toContain(message)
    }
    expect(wrapper.emitted('submit')).toBeUndefined()
  })

  it('clears field errors while editing and submits the validated payload', async () => {
    const wrapper = mountForm()
    await wrapper.get('[data-test="save-route-btn"]').trigger('click')
    const selectors = wrapper.findAllComponents(LocalityStub)
    selectors[0]!.vm.$emit('selected', { id: 1, name: 'Loja' })
    selectors[1]!.vm.$emit('selected', { id: 2, name: 'Catamayo' })
    await wrapper.get('[data-test="distance-km-input"]').setValue('36.5')
    await wrapper.get('[data-test="time-hours-input"]').setValue('1')
    await wrapper.get('[data-test="time-minutes-input"]').setValue('15')
    expect(wrapper.text()).not.toContain(ERROR_ORIGIN_REQUIRED)
    expect(wrapper.text()).not.toContain(ERROR_DESTINATION_REQUIRED)
    expect(wrapper.text()).not.toContain(ERROR_DISTANCE_REQUIRED)
    expect(wrapper.getComponent(RouteTimeInput).props('error')).toBeFalsy()
    await wrapper.get('[data-test="save-route-btn"]').trigger('click')
    expect(wrapper.emitted('submit')).toEqual([[{
      origin_id: 1, destination_id: 2, distance_km: 36.5,
      estimated_time_minutes: 75, name_suffix: null, description: null, stops: [],
    }]])
  })

  it('reorders intermediate stops using the buttons and submits sequential orders', async () => {
    const wrapper = mountForm()
    const selectors = wrapper.findAllComponents(LocalityStub)
    selectors[0]!.vm.$emit('selected', { id: 1, name: 'Loja' })
    selectors[1]!.vm.$emit('selected', { id: 2, name: 'Cuenca' })
    await wrapper.get('[data-test="distance-km-input"]').setValue('210')
    await wrapper.get('[data-test="time-hours-input"]').setValue('4')
    await wrapper.get('[aria-label="Solo las de origen y destino"]').trigger('click')
    const editor = wrapper.getComponent(RouteStopsEditor)
    editor.getComponent(LocalityStub).vm.$emit('selected', { id: 3, name: 'Saraguro' })
    editor.getComponent(LocalityStub).vm.$emit('selected', { id: 4, name: 'Oña' })
    await wrapper.vm.$nextTick()
    await wrapper.findAll('[title="Mover arriba"]')[1]!.trigger('click')
    expect(editor.props('stops').map(stop => stop.locality_id)).toEqual([4, 3])
    await wrapper.findAll('[title="Mover abajo"]')[0]!.trigger('click')
    expect(editor.props('stops').map(stop => stop.stop_order)).toEqual([1, 2])
    await wrapper.get('[data-test="save-route-btn"]').trigger('click')
    expect(wrapper.emitted('submit')?.[0]?.[0]).toMatchObject({
      stops: [{ locality_id: 3, stop_order: 1 }, { locality_id: 4, stop_order: 2 }],
    })
  })

  it('revalidates dependent errors when the origin changes', () => {
    const form = useRouteForm()
    form.originId.value = 1
    form.destinationId.value = 1
    form.validateField('destination_id')
    expect(form.errors.value.destination_id).toBe(ERROR_ROUTE_ORIGIN_DESTINATION_SAME)
    form.onlyOriginDest.value = false
    form.addStop(3, 'Saraguro')
    form.originId.value = 3
    form.validateField('origin_id')
    expect(form.errors.value.destination_id).toBeUndefined()
    expect(form.errors.value.stops).toBe(ERROR_ROUTE_STOP_EQUALS_ORIGIN_OR_DESTINATION)
    form.originId.value = 2
    form.validateField('origin_id')
    expect(form.errors.value.stops).toBeUndefined()
  })

  it('ignores out-of-bounds reordering and preserves sequential orders after removal', () => {
    const form = useRouteForm()
    form.addStop(3, 'Saraguro')
    form.addStop(4, 'Oña')
    form.moveStopUp(0)
    form.moveStopDown(1)
    form.moveStopUp(-1)
    form.moveStopDown(10)
    expect(form.stops.value.map(stop => stop.locality_id)).toEqual([3, 4])
    form.moveStopUp(1)
    form.removeStop(0)
    expect(form.stops.value).toEqual([{ locality_id: 3, locality_name: 'Saraguro', stop_order: 1 }])
  })
})
