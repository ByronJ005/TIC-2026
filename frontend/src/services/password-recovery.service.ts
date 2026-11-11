import { apiClient } from './api-client'

export interface MessageResponse {
  message: string
}

export const PasswordRecoveryService = {
  forgotPassword(email: string): Promise<MessageResponse> {
    return apiClient<MessageResponse>('/auth/forgot-password', 'POST', {
      body: { email },
    })
  },

  resetPassword(token: string, newPassword: string): Promise<MessageResponse> {
    return apiClient<MessageResponse>('/auth/reset-password', 'POST', {
      body: { token, new_password: newPassword },
    })
  },
}

