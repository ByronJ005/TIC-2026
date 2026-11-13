import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import CooperativasView from '@/views/CooperativasView.vue'
import CooperativaCard from '@/components/cooperativas/CooperativaCard.vue'
import CooperativaTable from '@/components/cooperativas/CooperativaTable.vue'
import CooperativaAdministratorsModal from '@/components/cooperativas/CooperativaAdministratorsModal.vue'
import { useCooperativasStore } from '@/stores/cooperativas.store'
import { CooperativasService, type Cooperativa, type EligibleAdmin } from '@/services/cooperativas.service'
import { triggerCooperativaInactiva } from '@/services/api-client'

const mockRouterPush = vi.fn<() => void>()
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockRouterPush,
  }),
}))

function createSampleCooperativa(id: number, name: string, ruc: string, isActive: boolean = true): Cooperativa {
  return {
    id,
    name,
    ruc,
    address: 'Terminal Terrestre Oficina 1',
    phone: '0987654321',
    email: 'contacto@coop.ec',
    logo_url: null,
    is_active: isActive,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    administradores: [
      {
        id: 10,
        first_name: 'Juan',
        last_name: 'Pérez',
        email: 'juan@coop.ec',
        document_number: '1104609829',
        is_active: true,
      },
    ],
  }
}

describe('CooperativasView Component Unit Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('CP-54: Alternates view mode between cards and table', async () => {
    const coop1 = createSampleCooperativa(1, 'Cooperativa Loja', '1190001234001', true)
    const coop2 = createSampleCooperativa(2, 'Cooperativa Cariamanga', '1190005678001', false)

    vi.spyOn(CooperativasService, 'getCooperativas').mockResolvedValue({
      items: [coop1, coop2],
      total: 2,
      page: 1,
      size: 10,
      total_pages: 1,
    })

    const wrapper = mount(CooperativasView, {
      global: {
        stubs: {
          CooperativaFormDialog: true,
        },
      },
    })

    const store = useCooperativasStore()
    // Wait for onMounted fetch
    await vi.waitFor(() => {
      expect(wrapper.findAllComponents(CooperativaCard).length).toBe(2)
    })

    // Default view mode is cards
    expect(store.viewMode).toBe('cards')
    expect(wrapper.find('[data-testid="cards-container"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="table-container"]').exists()).toBe(false)

    // Click table view button
    const tableBtn = wrapper.find('[data-testid="view-table-button"]')
    expect(tableBtn.exists()).toBe(true)
    await tableBtn.trigger('click')

    expect(store.viewMode).toBe('table')
    expect(wrapper.find('[data-testid="cards-container"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="table-container"]').exists()).toBe(true)
    expect(wrapper.findAllComponents(CooperativaTable).length).toBe(1)

    // Click cards view button
    const cardsBtn = wrapper.find('[data-testid="view-cards-button"]')
    await cardsBtn.trigger('click')

    expect(store.viewMode).toBe('cards')
    expect(wrapper.find('[data-testid="cards-container"]').exists()).toBe(true)
  })

  it('Displays active and deactivated state badges correctly in card', () => {
    const activeCoop = createSampleCooperativa(1, 'Coop Activa', '1190001234001', true)
    const deactCoop = createSampleCooperativa(2, 'Coop Inactiva', '1190005678001', false)

    const activeWrapper = mount(CooperativaCard, {
      props: { cooperativa: activeCoop },
    })
    expect(activeWrapper.text()).toContain('Activa')
    expect(activeWrapper.text()).toContain('Desactivar')

    const deactWrapper = mount(CooperativaCard, {
      props: { cooperativa: deactCoop },
    })
    expect(deactWrapper.text()).toContain('Desactivada')
    expect(deactWrapper.text()).toContain('Activar')
  })

  it('Opens confirmation modal when toggle status is requested', async () => {
    const coop1 = createSampleCooperativa(1, 'Cooperativa Loja', '1190001234001', true)
    vi.spyOn(CooperativasService, 'getCooperativas').mockResolvedValue({
      items: [coop1],
      total: 1,
      page: 1,
      size: 10,
      total_pages: 1,
    })

    const wrapper = mount(CooperativasView, {
      global: {
        stubs: {
          CooperativaFormDialog: true,
        },
      },
    })

    await vi.waitFor(() => {
      expect(wrapper.findComponent(CooperativaCard).exists()).toBe(true)
    })

    const card = wrapper.findComponent(CooperativaCard)
    // Trigger toggle status from card
    await card.vm.$emit('toggleStatus', coop1)

    expect(wrapper.find('[data-testid="status-confirm-modal"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Desactivar Cooperativa')
    expect(wrapper.text()).toContain('Cooperativa Loja')
  })

  it('CP-60: Handles 409 COOPERATIVA_INACTIVA callback redirecting to dashboard', () => {
    const alertMock = vi.spyOn(window, 'alert').mockImplementation(() => {})

    mount(CooperativasView, {
      global: {
        stubs: {
          CooperativaFormDialog: true,
        },
      },
    })

    triggerCooperativaInactiva('La cooperativa ha sido desactivada en otra sesión.')

    expect(mockRouterPush).toHaveBeenCalledWith({ name: 'dashboard' })
    expect(alertMock).toHaveBeenCalledWith('La cooperativa ha sido desactivada en otra sesión.')
  })

  it('CP-61 - CP-63: Modal enforces max 3 administrators and disables excess selection', async () => {
    const eligibleAdmins: EligibleAdmin[] = [
      { id: 1, first_name: 'Admin', last_name: 'Uno', email: 'uno@coop.ec', document_number: '1104609801', is_already_assigned: false },
      { id: 2, first_name: 'Admin', last_name: 'Dos', email: 'dos@coop.ec', document_number: '1104609802', is_already_assigned: false },
      { id: 3, first_name: 'Admin', last_name: 'Tres', email: 'tres@coop.ec', document_number: '1104609803', is_already_assigned: false },
      { id: 4, first_name: 'Admin', last_name: 'Cuatro', email: 'cuatro@coop.ec', document_number: '1104609804', is_already_assigned: false },
    ]

    vi.spyOn(CooperativasService, 'getEligibleAdministrators').mockResolvedValue(eligibleAdmins)
    vi.spyOn(CooperativasService, 'getAdministradores').mockResolvedValue([])

    const modalWrapper = mount(CooperativaAdministratorsModal, {
      props: {
        cooperativaId: 10,
        isOpen: true,
      },
    })

    await vi.waitFor(() => {
      expect(modalWrapper.text()).toContain('Admin Uno')
    })

    // Click on the first 3 items to select them
    const userRows = modalWrapper.findAll('.cursor-pointer')
    expect(userRows.length).toBe(4)

    await userRows[0]!.trigger('click')
    await userRows[1]!.trigger('click')
    await userRows[2]!.trigger('click')

    expect(modalWrapper.text()).toContain('3 / 3 seleccionados')

    // 4th user item should now have opacity-50 and cursor-not-allowed
    const fourthUser = modalWrapper.find('[data-testid="user-item-4"]')
    expect(fourthUser.exists()).toBe(true)
    expect(fourthUser.classes()).toContain('cursor-not-allowed')
    expect(fourthUser.classes()).toContain('opacity-50')
  })
})
