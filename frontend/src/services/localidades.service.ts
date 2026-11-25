import { apiClient } from './api-client'

export interface Locality {
  id: number
  name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LocalityListResponse {
  items: Locality[]
  total: number
}

export interface LocalityCreate {
  name: string
}

export async function getLocalidades(search: string = ''): Promise<LocalityListResponse> {
  const params: Record<string, string> = {}
  if (search.trim()) {
    params.search = search.trim()
  }
  return apiClient<LocalityListResponse>('/localidades', 'GET', { params })
}

export async function createLocality(data: LocalityCreate): Promise<Locality> {
  return apiClient<Locality>('/localidades', 'POST', { body: data })
}
