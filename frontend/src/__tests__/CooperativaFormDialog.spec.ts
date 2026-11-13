import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import CooperativaFormDialog from '@/components/cooperativas/CooperativaFormDialog.vue'
import { CooperativasService, type Cooperativa } from '@/services/cooperativas.service'

function createSampleCooperativa(id: number = 1): Cooperativa {
  return {
    id,
    name: 'Cooperativa Loja',
    ruc: '1190001234001',
    address: 'Terminal Terrestre Oficina 1',
    phone: '0987654321',
    email: 'contacto@coop.ec',
    logo_url: null,
    is_active: true,
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

describe('CooperativaFormDialog Component Unit Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.spyOn(CooperativasService, 'getAdministradores').mockResolvedValue([])
    vi.spyOn(CooperativasService, 'getEligibleAdministrators').mockResolvedValue([])
  })

  it('Renders create mode with editable RUC and Personal section available', () => {
    const wrapper = mount(CooperativaFormDialog, {
      props: {
        isOpen: true,
        cooperativa: null,
      },
      global: {
        stubs: {
          CooperativaAdministratorsModal: true,
        },
      },
    })

    expect(wrapper.text()).toContain('Nueva Cooperativa')
    const rucInput = wrapper.find('[data-testid="coop-ruc-input"]')
    expect(rucInput.exists()).toBe(true)
    expect(rucInput.attributes('disabled')).toBeUndefined()
    expect(wrapper.find('[data-testid="manage-admins-button"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('(opcional)')
  })

  it('Dynamically updates to edit mode when cooperativa prop changes', async () => {
    const wrapper = mount(CooperativaFormDialog, {
      props: {
        isOpen: true,
        cooperativa: null,
      },
      global: {
        stubs: {
          CooperativaAdministratorsModal: true,
        },
      },
    })

    expect(wrapper.text()).toContain('Nueva Cooperativa')
    expect(wrapper.find('[data-testid="submit-cooperativa-button"]').text()).toBe('Registrar cooperativa')

    const coop = createSampleCooperativa(5)
    await wrapper.setProps({ cooperativa: coop })

    expect(wrapper.text()).toContain('Editar Cooperativa')
    expect(wrapper.find('[data-testid="submit-cooperativa-button"]').text()).toBe('Guardar cambios')
    const rucInput = wrapper.find('[data-testid="coop-ruc-input"]')
    expect(rucInput.attributes('disabled')).toBeDefined()
  })

  it('Renders edit mode with disabled RUC and Personal de cooperativa section', async () => {
    const coop = createSampleCooperativa(5)
    vi.spyOn(CooperativasService, 'getAdministradores').mockResolvedValue([
      {
        id: 10,
        first_name: 'Juan',
        last_name: 'Pérez',
        email: 'juan@coop.ec',
        document_number: '1104609829',
        is_active: true,
      },
    ])

    const wrapper = mount(CooperativaFormDialog, {
      props: {
        isOpen: true,
        cooperativa: coop,
      },
      global: {
        stubs: {
          CooperativaAdministratorsModal: true,
        },
      },
    })

    expect(wrapper.text()).toContain('Editar Cooperativa')
    const rucInput = wrapper.find('[data-testid="coop-ruc-input"]')
    expect(rucInput.attributes('disabled')).toBeDefined()
    expect(wrapper.text()).toContain('El RUC no puede modificarse una vez registrado.')

    expect(wrapper.text()).toContain('Personal de cooperativa')
    expect(wrapper.find('[data-testid="manage-admins-button"]').exists()).toBe(true)

    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('Juan Pérez')
    })
  })

  it('Validates name and prevents submit when empty', async () => {
    const wrapper = mount(CooperativaFormDialog, {
      props: {
        isOpen: true,
        cooperativa: null,
      },
      global: {
        stubs: {
          CooperativaAdministratorsModal: true,
        },
      },
    })

    const submitBtn = wrapper.find('[data-testid="submit-cooperativa-button"]')
    await submitBtn.trigger('click')

    // Expect error messages
    expect(wrapper.text()).toContain('El nombre de la cooperativa no puede quedar vacío')
    expect(wrapper.text()).toContain('El RUC es obligatorio')
    expect(wrapper.emitted('submit')).toBeUndefined()
  })

  it('CP-46 to CP-49: Emits submit event when form is valid', async () => {
    const wrapper = mount(CooperativaFormDialog, {
      props: {
        isOpen: true,
        cooperativa: null,
      },
      global: {
        stubs: {
          CooperativaAdministratorsModal: true,
        },
      },
    })

    const nameInput = wrapper.find('[data-testid="coop-name-input"]')
    const rucInput = wrapper.find('[data-testid="coop-ruc-input"]')

    await nameInput.setValue('Cooperativa Santa 1')
    await rucInput.setValue('1790011216001')

    const submitBtn = wrapper.find('[data-testid="submit-cooperativa-button"]')
    await submitBtn.trigger('click')

    expect(wrapper.emitted('submit')).toBeDefined()
    const submitPayload = wrapper.emitted('submit')?.[0]?.[0] as {
      data: { name: string; ruc: string }
    }
    expect(submitPayload.data.name).toBe('Cooperativa Santa 1')
    expect(submitPayload.data.ruc).toBe('1790011216001')
  })
})
