import { apiClient } from './api-client'
import type { User, UserRole } from './auth.service'

export interface UserPaginationResponse {
  items: User[]
  total: number
  page: number
  size: number
  pages: number
}

export interface UsersQueryParams {
  page?: number
  size?: number
  search?: string
  include_inactive?: boolean
}

export class UsersService {
  static async getUsers(params: UsersQueryParams = {}): Promise<UserPaginationResponse> {
    const cleanParams: Record<string, string | number | boolean> = {}
    if (params.page !== undefined) cleanParams.page = params.page
    if (params.size !== undefined) cleanParams.size = params.size
    if (params.search) cleanParams.search = params.search
    if (params.include_inactive !== undefined) cleanParams.include_inactive = params.include_inactive

    return apiClient<UserPaginationResponse>('/usuarios', 'GET', {
      params: cleanParams,
    })
  }

  static async updateRoles(userId: number, roles: UserRole[]): Promise<User> {
    return apiClient<User>(`/usuarios/${userId}/roles`, 'PUT', {
      body: { roles },
    })
  }

  static async updateStatus(userId: number, isActive: boolean): Promise<User> {
    return apiClient<User>(`/usuarios/${userId}/estado`, 'PATCH', {
      body: { is_active: isActive },
    })
  }
}

