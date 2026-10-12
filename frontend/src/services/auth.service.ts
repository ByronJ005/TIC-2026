import { apiClient } from './api-client'

export type DocumentType = 'CEDULA' | 'PASAPORTE'
export type UserRole =
  | 'ADMIN_GENERAL'
  | 'ADMIN_COOPERATIVA'
  | 'SECRETARIA'
  | 'PASAJERO'

export interface User {
  id: number
  document_type: DocumentType
  document_number: string
  first_name: string
  last_name: string
  email: string
  role: UserRole
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface RegisterData {
  document_type: DocumentType
  document_number: string
  first_name: string
  last_name: string
  email: string
  password: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export class AuthService {
  static async register(data: RegisterData): Promise<User> {
    return apiClient<User>('/auth/register', 'POST', { body: data })
  }

  static async login(credentials: LoginCredentials): Promise<TokenResponse> {
    return apiClient<TokenResponse>('/auth/login', 'POST', {
      body: credentials,
    })
  }

  static async logout(): Promise<{ message: string }> {
    return apiClient<{ message: string }>('/auth/logout', 'POST')
  }

  static async getProfile(): Promise<User> {
    return apiClient<User>('/auth/me', 'GET')
  }
}
