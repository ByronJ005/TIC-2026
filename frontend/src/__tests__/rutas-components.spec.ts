import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import RouteTimeInput from '@/components/rutas/RouteTimeInput.vue'
import RouteStopsEditor from '@/components/rutas/RouteStopsEditor.vue'
import RouteFormDialog from '@/components/rutas/RouteFormDialog.vue'
import NotificationBell from '@/components/notifications/NotificationBell.vue'
import RutasCooperativaView from '@/views/RutasCooperativaView.vue'
import { useAuthStore } from '@/stores/auth.store'
import { useRutasStore } from '@/stores/rutas.store'
import * as notifService from '@/services/notificaciones.service'
import type { RouteDetail } from '@/services/rutas.service'

describe('Rutas Components Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('RouteTimeInput (CP-72)', () => {
    it('renders hours and minutes and emits updates', async () => {
      const wrapper = mount(RouteTimeInput, {
        props: {
          hours: '2',
          minutes: '30',
        },
      })

      const hoursInput = wrapper.find('[data-test="time-hours-input"]')
      const minutesInput = wrapper.find('[data-test="time-minutes-input"]')

      expect(hoursInput.exists()).toBe(true)
      expect(minutesInput.exists()).toBe(true)

      await hoursInput.setValue('3')
      expect(wrapper.emitted('update:hours')?.[0]).toEqual(['3'])

      await minutesInput.setValue('45')
      expect(wrapper.emitted('update:minutes')?.[0]).toEqual(['45'])
    })

    it('blocks non-numeric keys on keydown (CP-72)', async () => {
      const wrapper = mount(RouteTimeInput, {
        props: {
          hours: '1',
          minutes: '0',
        },
      })

      const hoursInput = wrapper.find('[data-test="time-hours-input"]')

      const letterEvent = new KeyboardEvent('keydown', { key: 'a', cancelable: true })
      hoursInput.element.dispatchEvent(letterEvent)
      expect(letterEvent.defaultPrevented).toBe(true)

      const symbolEvent = new KeyboardEvent('keydown', { key: '-', cancelable: true })
      hoursInput.element.dispatchEvent(symbolEvent)
      expect(symbolEvent.defaultPrevented).toBe(true)

      const digitEvent = new KeyboardEvent('keydown', { key: '5', cancelable: true })
      hoursInput.element.dispatchEvent(digitEvent)
      expect(digitEvent.defaultPrevented).toBe(false)
    })
  })

  describe('RouteStopsEditor (CP-69, CP-70, CP-71, CP-78)', () => {
    it('has "Solo las de origen y destino" checked by default (CP-78)', () => {
      const wrapper = mount(RouteStopsEditor, {
        props: {
          stops: [],
          originId: 1,
          destinationId: 2,
          onlyOriginDest: true,
        },
      })

      expect(wrapper.text()).toContain('Solo las de origen y destino')
      // Intermediate stops list should not be shown when onlyOriginDest is true
      expect(wrapper.text()).not.toContain('Paradas intermedias ordenadas')
    })

    it('shows stops and order when unchecked (CP-71)', () => {
      const wrapper = mount(RouteStopsEditor, {
        props: {
          stops: [
            { locality_id: 10, stop_order: 1, locality_name: 'Catamayo' },
            { locality_id: 11, stop_order: 2, locality_name: 'San Pedro' },
          ],
          originId: 1,
          destinationId: 2,
          onlyOriginDest: false,
        },
        global: {
          stubs: {
            LocalityCombobox: true,
          },
        },
      })

      expect(wrapper.text()).toContain('Paradas intermedias ordenadas')
      expect(wrapper.text()).toContain('Catamayo')
      expect(wrapper.text()).toContain('San Pedro')
      expect(wrapper.text()).toContain('1')
      expect(wrapper.text()).toContain('2')
    })
  })

  describe('RouteFormDialog (CP-65, CP-79)', () => {
    const sampleRoute: RouteDetail = {
      id: 5,
      cooperativa_id: null,
      origin_id: 1,
      destination_id: 2,
      origin_name: 'Loja',
      destination_name: 'Quito',
      name: 'Loja - Quito Expreso',
      name_suffix: 'Expreso',
      distance_km: '680.00',
      estimated_time_minutes: 660,
      description: 'Ruta nocturna',
      is_active: true,
      stops: [],
      has_associations: true, // Associated with cooperatives or trips
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    }

    it('shows warning and disables origin and destination when has_associations is true (CP-79)', () => {
      const wrapper = mount(RouteFormDialog, {
        props: {
          isOpen: true,
          route: sampleRoute,
        },
        global: {
          stubs: {
            LocalityCombobox: true,
            RouteStopsEditor: true,
            RouteTimeInput: true,
          },
        },
      })

      expect(wrapper.text()).toContain('Origen y Destino no modificables')
      expect(wrapper.text()).toContain('Esta ruta tiene cooperativas, turnos o viajes asociados')
    })
  })

  describe('NotificationBell (CP-99 to CP-102)', () => {
    it('renders bell and opens dropdown with notifications', async () => {
      vi.spyOn(notifService, 'getNotifications').mockResolvedValue({
        items: [
          {
            id: 1,
            user_id: 10,
            title: 'Ruta desactivada',
            message: 'La ruta Loja - Quito ha sido desactivada.',
            is_read: false,
            created_at: '2026-11-21T01:00:00Z',
          },
        ],
        unread_count: 1,
        total: 1,
        page: 1,
        size: 5,
        has_more: false,
      })

      const wrapper = mount(NotificationBell)
      await new Promise((r) => setTimeout(r, 50))

      // Check unread badge
      const badge = wrapper.find('[data-test="notification-badge"]')
      expect(badge.exists()).toBe(true)
      expect(badge.text()).toBe('1')

      // Open popover
      const bellBtn = wrapper.find('[data-test="notification-bell-btn"]')
      await bellBtn.trigger('click')

      expect(wrapper.text()).toContain('Notificaciones')
      expect(wrapper.text()).toContain('La ruta Loja - Quito ha sido desactivada.')
    })

    it('shows empty state when there are no notifications (CP-102)', async () => {
      vi.spyOn(notifService, 'getNotifications').mockResolvedValue({
        items: [],
        unread_count: 0,
        total: 0,
        page: 1,
        size: 5,
        has_more: false,
      })

      const wrapper = mount(NotificationBell)
      await new Promise((r) => setTimeout(r, 50))

      const bellBtn = wrapper.find('[data-test="notification-bell-btn"]')
      await bellBtn.trigger('click')

      expect(wrapper.text()).toContain('No tienes notificaciones')
    })
  })

  describe('RutasCooperativaView (CA-97)', () => {
    it('shows "Sin cooperativa asignada" and hides route sections when user has no cooperativa_id', () => {
      const auth = useAuthStore()
      auth.user = {
        id: 1,
        document_type: 'CEDULA',
        document_number: '1104609829',
        first_name: 'Admin',
        last_name: 'SinCoop',
        email: 'admin@test.ec',
        roles: ['ADMIN_COOPERATIVA'],
        is_active: true,
        cooperativa_id: null,
        created_at: '',
        updated_at: '',
      }

      const wrapper = mount(RutasCooperativaView, {
        global: {
          stubs: {
            GeneralRoutesPickerModal: true,
            RouteFormDialog: true,
            RouteDetailDialog: true,
          },
        },
      })

      expect(wrapper.find('[data-test="no-coop-notice"]').exists()).toBe(true)
      expect(wrapper.find('[data-test="coop-inactive-notice"]').exists()).toBe(false)
      expect(wrapper.find('[data-test="adopted-routes-section"]').exists()).toBe(false)
      expect(wrapper.find('[data-test="specific-routes-section"]').exists()).toBe(false)
      expect(wrapper.text()).not.toContain('Error al cargar rutas de su cooperativa')
    })

    it('shows "Cooperativa desactivada" and hides route sections when cooperative is deactivated', async () => {
      const auth = useAuthStore()
      auth.user = {
        id: 1,
        document_type: 'CEDULA',
        document_number: '1104609829',
        first_name: 'Admin',
        last_name: 'CoopInactiva',
        email: 'admin@test.ec',
        roles: ['ADMIN_COOPERATIVA'],
        is_active: true,
        cooperativa_id: 10,
        cooperativa_name: 'Coop Inactiva',
        created_at: '',
        updated_at: '',
      }

      const rutasStore = useRutasStore()
      rutasStore.isCooperativeInactive = true

      const wrapper = mount(RutasCooperativaView, {
        global: {
          stubs: {
            GeneralRoutesPickerModal: true,
            RouteFormDialog: true,
            RouteDetailDialog: true,
          },
        },
      })

      expect(wrapper.find('[data-test="coop-inactive-notice"]').exists()).toBe(true)
      expect(wrapper.find('[data-test="no-coop-notice"]').exists()).toBe(false)
      expect(wrapper.find('[data-test="adopted-routes-section"]').exists()).toBe(false)
      expect(wrapper.find('[data-test="specific-routes-section"]').exists()).toBe(false)
      expect(wrapper.text()).not.toContain('Error al cargar rutas de su cooperativa')
    })
  })
})
