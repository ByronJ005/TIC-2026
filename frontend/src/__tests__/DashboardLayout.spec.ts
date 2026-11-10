import { beforeEach, describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import DashboardLayout from '@/views/DashboardLayout.vue'
import { useAuthStore } from '@/stores/auth.store'
import type { User, UserRole } from '@/services/auth.service'
import router from '@/router'

function createMockUser(roles: UserRole[]): User {
  return {
    id: 1,
    document_type: 'CEDULA',
    document_number: '1710034065',
    first_name: 'Test',
    last_name: 'User',
    email: 'test@example.com',
    roles,
    is_active: true,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  }
}

describe('DashboardLayout Module Navigation RBAC (RF-05)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('V-11: renders only Reservas and Perfil for exclusive PASAJERO role in nav sidebar', async () => {
    const authStore = useAuthStore()
    authStore.user = createMockUser(['PASAJERO'])

    const wrapper = mount(DashboardLayout, {
      global: {
        plugins: [router],
        stubs: {
          RouterView: true,
          Teleport: true,
        },
      },
    })

    const navText = wrapper.find('aside nav').text()
    expect(navText).toContain('Reservas')
    expect(navText).toContain('Perfil')
    expect(navText).not.toContain('Usuarios')
    expect(navText).not.toContain('Cooperativas')
    expect(navText).not.toContain('Rutas generales')
    expect(navText).not.toContain('Buses')
  })

  it('V-12: renders Usuarios, Cooperativas, Rutas generales and Precios generales for ADMIN_GENERAL in nav sidebar', async () => {
    const authStore = useAuthStore()
    authStore.user = createMockUser(['ADMIN_GENERAL'])

    const wrapper = mount(DashboardLayout, {
      global: {
        plugins: [router],
        stubs: {
          RouterView: true,
          Teleport: true,
        },
      },
    })

    const navText = wrapper.find('aside nav').text()
    expect(navText).toContain('Usuarios')
    expect(navText).toContain('Cooperativas')
    expect(navText).toContain('Rutas generales')
    expect(navText).toContain('Precios generales')
    expect(navText).not.toContain('Buses')
    expect(navText).not.toContain('Turnos')
    expect(navText).not.toContain('Reservas')
  })

  it('V-13: renders exact mathematical union for combined roles [ADMIN_COOPERATIVA, PASAJERO]', async () => {
    const authStore = useAuthStore()
    authStore.user = createMockUser(['ADMIN_COOPERATIVA', 'PASAJERO'])

    const wrapper = mount(DashboardLayout, {
      global: {
        plugins: [router],
        stubs: {
          RouterView: true,
          Teleport: true,
        },
      },
    })

    const navText = wrapper.find('aside nav').text()
    // ADMIN_COOPERATIVA modules
    expect(navText).toContain('Rutas de cooperativa')
    expect(navText).toContain('Buses')
    expect(navText).toContain('Turnos')
    expect(navText).toContain('Tarifas específicas')
    // PASAJERO modules
    expect(navText).toContain('Reservas')
    expect(navText).toContain('Perfil')
    // Should NOT contain ADMIN_GENERAL modules
    expect(navText).not.toContain('Usuarios')
    expect(navText).not.toContain('Cooperativas')
    expect(navText).not.toContain('Precios generales')
  })

  it('V-14: renders only Reservas and NOT Informes for SECRETARIA_COOPERATIVA in nav sidebar', async () => {
    const authStore = useAuthStore()
    authStore.user = createMockUser(['SECRETARIA_COOPERATIVA'])

    const wrapper = mount(DashboardLayout, {
      global: {
        plugins: [router],
        stubs: {
          RouterView: true,
          Teleport: true,
        },
      },
    })

    const navText = wrapper.find('aside nav').text()
    expect(navText).toContain('Reservas')
    expect(navText).not.toContain('Informes')
    expect(navText).not.toContain('Usuarios')
    expect(navText).not.toContain('Buses')
  })

  it('V-15: handles empty or undefined roles gracefully without throwing errors', async () => {
    const authStore = useAuthStore()
    authStore.user = createMockUser([])

    const wrapper = mount(DashboardLayout, {
      global: {
        plugins: [router],
        stubs: {
          RouterView: true,
          Teleport: true,
        },
      },
    })

    const navText = wrapper.find('aside nav').text()
    expect(navText).toContain('Sin módulos asignados')
  })

  it('V-19: toggles desktop sidebar width between expanded (w-64) and collapsed (w-20)', async () => {
    const authStore = useAuthStore()
    authStore.user = createMockUser(['ADMIN_GENERAL'])

    const wrapper = mount(DashboardLayout, {
      global: {
        plugins: [router],
        stubs: {
          RouterView: true,
          Teleport: true,
        },
      },
    })

    const aside = wrapper.find('aside')
    expect(aside.classes()).toContain('w-64')
    expect(aside.classes()).not.toContain('w-20')
    expect(wrapper.find('aside nav').text()).toContain('Usuarios')

    // Click toggle button to collapse
    const toggleBtn = wrapper.find('[data-test="toggle-collapse-btn"]')
    await toggleBtn.trigger('click')

    expect(aside.classes()).toContain('w-20')
    expect(aside.classes()).not.toContain('w-64')
    // In collapsed mode, text labels are hidden
    expect(wrapper.find('aside nav').text()).not.toContain('Usuarios')

    // Click toggle button to expand again
    await toggleBtn.trigger('click')
    expect(aside.classes()).toContain('w-64')
    expect(wrapper.find('aside nav').text()).toContain('Usuarios')
  })

  it('V-20: toggles mobile navigation drawer and closes upon clicking close button', async () => {
    const authStore = useAuthStore()
    authStore.user = createMockUser(['ADMIN_GENERAL'])

    const wrapper = mount(DashboardLayout, {
      global: {
        plugins: [router],
        stubs: {
          RouterView: true,
          Teleport: true,
        },
      },
    })

    // Initially mobile drawer is not open
    expect(wrapper.find('[data-test="mobile-drawer"]').exists()).toBe(false)

    // Open mobile menu
    const menuBtn = wrapper.find('[data-test="mobile-menu-btn"]')
    await menuBtn.trigger('click')
    expect(wrapper.find('[data-test="mobile-drawer"]').exists()).toBe(true)

    // Close mobile menu via close button
    const closeBtn = wrapper.find('[data-test="close-mobile-menu-btn"]')
    await closeBtn.trigger('click')
    expect(wrapper.find('[data-test="mobile-drawer"]').exists()).toBe(false)
  })
})
