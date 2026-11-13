import { apiClient } from './api-client'

export interface AdministradorSummary {
  id: number
  first_name: string
  last_name: string
  email: string
  document_number: string
  phone?: string | null
  is_active: boolean
}

export interface Cooperativa {
  id: number
  name: string
  ruc: string
  address?: string | null
  phone?: string | null
  email?: string | null
  logo_url?: string | null
  is_active: boolean
  administradores: AdministradorSummary[]
  created_at: string
  updated_at: string
}

export interface CooperativaPaginationResponse {
  items: Cooperativa[]
  total: number
  page: number
  size: number
  total_pages: number
}

export interface CooperativaQueryParams {
  page?: number
  size?: number
  search?: string
  is_active?: boolean
}

export interface CooperativaCreatePayload {
  name: string
  ruc: string
  address?: string | null
  phone?: string | null
  email?: string | null
  logo_url?: string | null
}

export interface CooperativaUpdatePayload {
  name?: string | null
  address?: string | null
  phone?: string | null
  email?: string | null
  logo_url?: string | null
}

export interface EligibleAdmin {
  id: number
  first_name: string
  last_name: string
  email: string
  document_number: string
  is_already_assigned: boolean
}

export function resolveLogoUrl(url: string | null | undefined): string | null {
  if (!url) return null
  const trimmed = url.trim()
  if (!trimmed) return null
  if (
    trimmed.startsWith('http://') ||
    trimmed.startsWith('https://') ||
    trimmed.startsWith('blob:') ||
    trimmed.startsWith('data:')
  ) {
    return trimmed
  }
  const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
  const backendBase = apiBase.replace(/\/api\/v1\/?$/, '')
  return `${backendBase}${trimmed.startsWith('/') ? '' : '/'}${trimmed}`
}

export class CooperativasService {
  static async getCooperativas(
    params: CooperativaQueryParams = {},
  ): Promise<CooperativaPaginationResponse> {
    const cleanParams: Record<string, string | number | boolean> = {}
    if (params.page !== undefined) cleanParams.page = params.page
    if (params.size !== undefined) cleanParams.size = params.size
    if (params.search) cleanParams.search = params.search
    if (params.is_active !== undefined) cleanParams.is_active = params.is_active

    return apiClient<CooperativaPaginationResponse>('/cooperativas', 'GET', {
      params: cleanParams,
    })
  }

  static async getCooperativaById(id: number): Promise<Cooperativa> {
    return apiClient<Cooperativa>(`/cooperativas/${id}`, 'GET')
  }

  static async createCooperativa(data: CooperativaCreatePayload): Promise<Cooperativa> {
    return apiClient<Cooperativa>('/cooperativas', 'POST', {
      body: data,
    })
  }

  static async updateCooperativa(
    id: number,
    data: CooperativaUpdatePayload,
  ): Promise<Cooperativa> {
    return apiClient<Cooperativa>(`/cooperativas/${id}`, 'PUT', {
      body: data,
    })
  }

  static async updateEstado(id: number, isActive: boolean): Promise<Cooperativa> {
    return apiClient<Cooperativa>(`/cooperativas/${id}/estado`, 'PATCH', {
      body: { is_active: isActive },
    })
  }

  static async uploadLogo(id: number, file: File): Promise<Cooperativa> {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient<Cooperativa>(`/cooperativas/${id}/logo`, 'POST', {
      body: formData,
    })
  }

  static async getAdministradores(id: number): Promise<AdministradorSummary[]> {
    return apiClient<AdministradorSummary[]>(`/cooperativas/${id}/administradores`, 'GET')
  }

  static async getEligibleAdministrators(
    id: number,
    search = '',
  ): Promise<EligibleAdmin[]> {
    const params: Record<string, string> = {}
    if (search.trim()) {
      params.search = search.trim()
    }
    return apiClient<EligibleAdmin[]>(
      `/cooperativas/${id}/administradores/elegibles`,
      'GET',
      { params },
    )
  }

  static async updateAdministradores(
    id: number,
    userIds: number[],
  ): Promise<AdministradorSummary[]> {
    return apiClient<AdministradorSummary[]>(
      `/cooperativas/${id}/administradores`,
      'PUT',
      {
        body: { user_ids: userIds },
      },
    )
  }
}
