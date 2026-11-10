import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  UsersService,
  type UserPaginationResponse,
} from '@/services/users.service'
import type { User, UserRole } from '@/services/auth.service'

export const useUsersStore = defineStore('users', () => {
  const users = ref<User[]>([])
  const total = ref(0)
  const page = ref(1)
  const size = ref(10)
  const pages = ref(0)
  const searchQuery = ref('')
  const includeInactive = ref(true) // Mostramos inactivos para poder reactivarlos
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const successMessage = ref<string | null>(null)

  let debounceTimer: ReturnType<typeof setTimeout> | null = null

  async function fetchUsers(): Promise<UserPaginationResponse | null> {
    isLoading.value = true
    error.value = null
    try {
      const response = await UsersService.getUsers({
        page: page.value,
        size: size.value,
        search: searchQuery.value,
        include_inactive: includeInactive.value,
      })
      users.value = response.items
      total.value = response.total
      pages.value = response.pages
      page.value = response.page
      return response
    } catch (err: unknown) {
      const apiErr = err as { message?: string }
      error.value = apiErr.message || 'Error al cargar la lista de usuarios'
      users.value = []
      total.value = 0
      pages.value = 0
      return null
    } finally {
      isLoading.value = false
    }
  }

  function onSearchInput(query: string, delay: number = 300) {
    searchQuery.value = query
    page.value = 1 // Reset page on new search
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }
    debounceTimer = setTimeout(() => {
      fetchUsers()
    }, delay)
  }

  function setPage(newPage: number) {
    if (newPage >= 1 && (pages.value === 0 || newPage <= pages.value)) {
      page.value = newPage
      fetchUsers()
    }
  }

  function toggleIncludeInactive(value: boolean) {
    includeInactive.value = value
    page.value = 1
    fetchUsers()
  }

  async function changeRoles(userId: number, roles: UserRole[]): Promise<boolean> {
    isLoading.value = true
    error.value = null
    try {
      const updated = await UsersService.updateRoles(userId, roles)
      const index = users.value.findIndex((u) => u.id === userId)
      if (index !== -1) {
        users.value[index] = updated
      }
      successMessage.value = 'Roles actualizados satisfactoriamente'
      return true
    } catch (err: unknown) {
      const apiErr = err as { message?: string }
      error.value = apiErr.message || 'Error al actualizar roles'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function changeStatus(userId: number, isActive: boolean): Promise<boolean> {
    isLoading.value = true
    error.value = null
    try {
      const updated = await UsersService.updateStatus(userId, isActive)
      const index = users.value.findIndex((u) => u.id === userId)
      if (index !== -1) {
        users.value[index] = updated
      }
      successMessage.value = isActive
        ? 'Usuario habilitado satisfactoriamente'
        : 'Usuario dado de baja exitosamente'
      return true
    } catch (err: unknown) {
      const apiErr = err as { message?: string }
      error.value = apiErr.message || 'Error al modificar estado del usuario'
      return false
    } finally {
      isLoading.value = false
    }
  }

  function clearMessages() {
    error.value = null
    successMessage.value = null
  }

  return {
    users,
    total,
    page,
    size,
    pages,
    searchQuery,
    includeInactive,
    isLoading,
    error,
    successMessage,
    fetchUsers,
    onSearchInput,
    setPage,
    toggleIncludeInactive,
    changeRoles,
    changeStatus,
    clearMessages,
  }
})

