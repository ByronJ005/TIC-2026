import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import UsersView from '@/views/UsersView.vue'
import { useAuthStore } from '@/stores/auth.store'
import { useUsersStore } from '@/stores/users.store'
import { UsersService } from '@/services/users.service'
import type { User } from '@/services/auth.service'

function createSampleUser(id: number, email: string): User {
  return {
    id,
    document_type: 'CEDULA',
    document_number: `171003406${id}`,
    first_name: `Nombre${id}`,
    last_name: `Apellido${id}`,
    email,
    roles: ['PASAJERO'],
    is_active: true,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  }
}

describe('UsersView Component & Store Unit Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('V-06: Disables action buttons on the currently logged-in user row', async () => {
    const authStore = useAuthStore()
    const usersStore = useUsersStore()

    const loggedInUser = createSampleUser(1, 'current.admin@example.com')
    loggedInUser.roles = ['ADMIN_GENERAL', 'PASAJERO']
    authStore.user = loggedInUser

    const otherUser = createSampleUser(2, 'other.user@example.com')
    usersStore.users = [loggedInUser, otherUser]
    usersStore.total = 2
    usersStore.pages = 1

    const wrapper = mount(UsersView, {
      global: {
        stubs: {
          Teleport: true,
        },
      },
    })

    const rows = wrapper.findAll('tbody tr')
    expect(rows.length).toBe(2)

    // First row is the logged in user -> action buttons must be disabled
    const firstRow = rows[0]!
    const firstRowButtons = firstRow.findAll('button')
    firstRowButtons.forEach((btn) => {
      expect(btn.attributes('disabled')).toBeDefined()
    })

    // Second row is another user -> action buttons must NOT be disabled
    const secondRow = rows[1]!
    const secondRowButtons = secondRow.findAll('button')
    secondRowButtons.forEach((btn) => {
      expect(btn.attributes('disabled')).toBeUndefined()
    })
  })

  it('V-08: Checkbox for PASAJERO remains checked and disabled in role modal', async () => {
    const authStore = useAuthStore()
    const usersStore = useUsersStore()

    authStore.user = createSampleUser(1, 'admin@example.com')
    authStore.user.roles = ['ADMIN_GENERAL', 'PASAJERO']

    const targetUser = createSampleUser(2, 'target@example.com')
    usersStore.users = [targetUser]

    const wrapper = mount(UsersView, {
      global: {
        stubs: {
          Teleport: true, // Inlines teleported content into wrapper DOM
        },
      },
    })

    // Click "Asignar rol" on the target user
    const firstRow = wrapper.findAll('tbody tr')[0]!
    const assignBtn = firstRow.findAll('button')[0]!
    await assignBtn.trigger('click')

    // Find the Pasajero checkbox inside the inlined modal
    const pasajeroCheckbox = wrapper.find('#role-checkbox-PASAJERO')
    expect(pasajeroCheckbox.exists()).toBe(true)
    expect(pasajeroCheckbox.attributes('disabled')).toBeDefined()
    expect((pasajeroCheckbox.element as HTMLInputElement).checked).toBe(true)
  })

  it('V-04: onSearchInput resets page to 1 and triggers UsersService.getUsers after debounce', async () => {
    const usersStore = useUsersStore()
    const spy = vi.spyOn(UsersService, 'getUsers').mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      size: 10,
      pages: 0,
    })

    usersStore.page = 5
    usersStore.onSearchInput('carlos', 20)

    expect(usersStore.page).toBe(1)
    expect(usersStore.searchQuery).toBe('carlos')

    await new Promise((resolve) => setTimeout(resolve, 60))
    expect(spy).toHaveBeenCalled()
    spy.mockRestore()
  })
})
