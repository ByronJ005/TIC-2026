import { apiClient } from './api-client'
import type { User } from './auth.service'

export interface ProfileUpdateData {
  first_name: string
  last_name: string
  phone: string
  address: string
  birth_date: string
  current_password: string
  new_password: string
  confirm_password: string
}

export interface ProfileUpdateResponse {
  user: User
  message: string
  // Present only when the password changed, to keep the current session alive
  access_token: string | null
  token_type: string | null
}

export const ProfileService = {
  getProfile(): Promise<User> {
    return apiClient<User>('/perfil', 'GET')
  },

  updateProfile(data: ProfileUpdateData): Promise<ProfileUpdateResponse> {
    return apiClient<ProfileUpdateResponse>('/perfil', 'PUT', { body: data })
  },
}

