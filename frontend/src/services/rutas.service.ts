import { apiClient } from './api-client'

export interface RouteStopInput {
  locality_id: number
  stop_order: number
}

export interface RouteStop {
  id: number
  route_id: number
  locality_id: number
  stop_order: number
  locality_name?: string
}

export interface Route {
  id: number
  cooperativa_id: number | null
  origin_id: number
  destination_id: number
  origin_name?: string
  destination_name?: string
  name: string
  name_suffix?: string | null
  distance_km: number | string
  estimated_time_minutes: number
  description?: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface RouteDetail extends Route {
  stops: RouteStop[]
  has_associations: boolean
  cooperativa_name?: string | null
}

export interface RoutePaginationResponse {
  items: Route[]
  total: number
  page: number
  size: number
  total_pages: number
}

export interface CooperativaRoutesGroup {
  cooperativa_id: number
  cooperativa_name: string
  routes: Route[]
}

export interface CooperativaGeneralRoute {
  id: number
  cooperativa_id: number
  route_id: number
  is_active: boolean
  created_at: string
  updated_at: string
  route: Route
}

export interface RouteCreatePayload {
  origin_id: number
  destination_id: number
  name_suffix?: string | null
  distance_km: number
  estimated_time_minutes: number
  description?: string | null
  stops?: RouteStopInput[]
}

export interface RouteUpdatePayload {
  origin_id?: number
  destination_id?: number
  name_suffix?: string | null
  distance_km?: number
  estimated_time_minutes?: number
  description?: string | null
  stops?: RouteStopInput[]
}

export interface RouteFilters {
  origin_id?: number
  destination_id?: number
  is_active?: boolean
  page?: number
  size?: number
}

// -------------------------------------------------------------
// General Routes (ADMIN_GENERAL)
// -------------------------------------------------------------
export async function getGeneralRoutes(filters: RouteFilters = {}): Promise<RoutePaginationResponse> {
  const params: Record<string, string | number | boolean> = {}
  if (filters.origin_id) params.origin_id = filters.origin_id
  if (filters.destination_id) params.destination_id = filters.destination_id
  if (filters.is_active !== undefined) params.is_active = filters.is_active
  if (filters.page) params.page = filters.page
  if (filters.size) params.size = filters.size

  return apiClient<RoutePaginationResponse>('/rutas-generales', 'GET', { params })
}

export async function createGeneralRoute(data: RouteCreatePayload): Promise<RouteDetail> {
  return apiClient<RouteDetail>('/rutas-generales', 'POST', { body: data })
}

export async function updateGeneralRoute(routeId: number, data: RouteUpdatePayload): Promise<RouteDetail> {
  return apiClient<RouteDetail>(`/rutas-generales/${routeId}`, 'PUT', { body: data })
}

export async function updateGeneralRouteEstado(
  routeId: number,
  isActive: boolean,
  confirm: boolean = false,
): Promise<RouteDetail> {
  return apiClient<RouteDetail>(`/rutas-generales/${routeId}/estado`, 'PATCH', {
    body: { is_active: isActive, confirm },
  })
}

export async function getSpecificRoutesSupervision(): Promise<CooperativaRoutesGroup[]> {
  return apiClient<CooperativaRoutesGroup[]>('/rutas-generales/especificas', 'GET')
}

// Shared detail route endpoint
export async function getRouteDetail(routeId: number): Promise<RouteDetail> {
  return apiClient<RouteDetail>(`/rutas/${routeId}`, 'GET')
}

// -------------------------------------------------------------
// Cooperative Routes (ADMIN_COOPERATIVA)
// -------------------------------------------------------------
export async function getAdoptedGeneralRoutes(): Promise<CooperativaGeneralRoute[]> {
  return apiClient<CooperativaGeneralRoute[]>('/rutas-cooperativa/generales', 'GET')
}

export async function getAvailableGeneralRoutes(): Promise<Route[]> {
  return apiClient<Route[]>('/rutas-cooperativa/generales/disponibles', 'GET')
}

export async function adoptGeneralRoutes(routeIds: number[]): Promise<CooperativaGeneralRoute[]> {
  return apiClient<CooperativaGeneralRoute[]>('/rutas-cooperativa/generales', 'POST', {
    body: { route_ids: routeIds },
  })
}

export async function updateAdoptionEstado(
  adoptionId: number,
  isActive: boolean,
  confirm: boolean = false,
): Promise<CooperativaGeneralRoute> {
  return apiClient<CooperativaGeneralRoute>(`/rutas-cooperativa/generales/${adoptionId}/estado`, 'PATCH', {
    body: { is_active: isActive, confirm },
  })
}

export async function getSpecificRoutes(): Promise<Route[]> {
  return apiClient<Route[]>('/rutas-cooperativa/especificas', 'GET')
}

export async function createSpecificRoute(data: RouteCreatePayload): Promise<RouteDetail> {
  return apiClient<RouteDetail>('/rutas-cooperativa/especificas', 'POST', { body: data })
}

export async function updateSpecificRoute(routeId: number, data: RouteUpdatePayload): Promise<RouteDetail> {
  return apiClient<RouteDetail>(`/rutas-cooperativa/especificas/${routeId}`, 'PUT', { body: data })
}

export async function updateSpecificRouteEstado(
  routeId: number,
  isActive: boolean,
  confirm: boolean = false,
): Promise<RouteDetail> {
  return apiClient<RouteDetail>(`/rutas-cooperativa/especificas/${routeId}/estado`, 'PATCH', {
    body: { is_active: isActive, confirm },
  })
}
