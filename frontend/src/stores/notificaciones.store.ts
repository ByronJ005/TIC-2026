import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  type AppNotification,
  getNotifications as getNotificationsApi,
  markAllNotificationsAsRead as markAllNotificationsAsReadApi,
} from '@/services/notificaciones.service'

export const useNotificacionesStore = defineStore('notificaciones', () => {
  const notifications = ref<AppNotification[]>([])
  const unreadCount = ref(0)
  const total = ref(0)
  const page = ref(1)
  const hasMore = ref(false)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchInitialNotifications() {
    isLoading.value = true
    error.value = null
    try {
      page.value = 1
      const res = await getNotificationsApi(1, 5)
      notifications.value = res.items
      unreadCount.value = res.unread_count
      total.value = res.total
      hasMore.value = res.has_more
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Error al cargar notificaciones'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchMoreNotifications() {
    if (!hasMore.value || isLoading.value) return
    isLoading.value = true
    error.value = null
    try {
      const nextPage = page.value + 1
      const res = await getNotificationsApi(nextPage, 5)
      notifications.value.push(...res.items)
      unreadCount.value = res.unread_count
      total.value = res.total
      hasMore.value = res.has_more
      page.value = nextPage
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Error al cargar más notificaciones'
    } finally {
      isLoading.value = false
    }
  }

  async function markAllAsRead() {
    try {
      await markAllNotificationsAsReadApi()
      unreadCount.value = 0
      notifications.value.forEach((n) => {
        n.is_read = true
      })
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Error al marcar notificaciones como leídas'
    }
  }

  return {
    notifications,
    unreadCount,
    total,
    page,
    hasMore,
    isLoading,
    error,
    fetchInitialNotifications,
    fetchMoreNotifications,
    markAllAsRead,
  }
})
