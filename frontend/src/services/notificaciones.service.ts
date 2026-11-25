import { apiClient } from './api-client'

export interface AppNotification {
  id: number
  user_id: number
  title: string
  message: string
  is_read: boolean
  created_at: string
}

export interface NotificationListResponse {
  items: AppNotification[]
  total: number
  unread_count: number
  has_more: boolean
  page: number
  size: number
}

export async function getNotifications(page: number = 1, size: number = 5): Promise<NotificationListResponse> {
  return apiClient<NotificationListResponse>('/notificaciones', 'GET', {
    params: { page, size },
  })
}

export async function markAllNotificationsAsRead(): Promise<{ message: string; count: number }> {
  return apiClient<{ message: string; count: number }>('/notificaciones/leidas', 'PATCH')
}
