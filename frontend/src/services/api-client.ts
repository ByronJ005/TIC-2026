export interface ApiError {
  status: number
  message: string
  detail?: unknown
}

const API_BASE_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const AUTH_TOKEN_KEY = 'auth_token'
export const AUTH_USER_KEY = 'auth_user'

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

interface RequestOptions {
  headers?: Record<string, string>
  body?: unknown
  params?: Record<string, string | number | boolean>
}

let onUnauthorizedCallback: ((message: string) => void) | null = null
let onCooperativaInactivaCallback: ((message: string) => void) | null = null

export function setUnauthorizedHandler(callback: (message: string) => void) {
  onUnauthorizedCallback = callback
}

export function setCooperativaInactivaHandler(callback: (message: string) => void) {
  onCooperativaInactivaCallback = callback
}

export function triggerCooperativaInactiva(message: string) {
  if (onCooperativaInactivaCallback) {
    onCooperativaInactivaCallback(message)
  }
}

export async function apiClient<T>(
  endpoint: string,
  method: HttpMethod = 'GET',
  options: RequestOptions = {},
): Promise<T> {
  const token = localStorage.getItem(AUTH_TOKEN_KEY)

  const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData

  const headers: Record<string, string> = {
    Accept: 'application/json',
    ...options.headers,
  }

  if (!isFormData) {
    headers['Content-Type'] = 'application/json'
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  let url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`

  if (options.params) {
    const searchParams = new URLSearchParams()
    Object.entries(options.params).forEach(([key, val]) => {
      if (val !== undefined && val !== null) {
        searchParams.append(key, String(val))
      }
    })
    const queryString = searchParams.toString()
    if (queryString) {
      url += `?${queryString}`
    }
  }

  const fetchOptions: RequestInit = {
    method,
    headers,
  }

  if (options.body && method !== 'GET') {
    fetchOptions.body = isFormData ? (options.body as FormData) : JSON.stringify(options.body)
  }

  let response: Response
  try {
    response = await fetch(url, fetchOptions)
  } catch {
    throw {
      status: 0,
      message: 'No se pudo conectar con el servidor. Verifica tu conexión.',
    } as ApiError
  }

  // Handle 401 Unauthorized
  if (response.status === 401) {
    // Clear credentials
    localStorage.removeItem(AUTH_TOKEN_KEY)
    localStorage.removeItem(AUTH_USER_KEY)

    const isAuthEndpoint =
      endpoint.includes('/login') || endpoint.includes('/register')
    if (!isAuthEndpoint && onUnauthorizedCallback) {
      onUnauthorizedCallback('Sesión expirada')
    }

    let detail: unknown = 'Sesión expirada o no autorizada'
    try {
      const data = (await response.json()) as { detail?: unknown }
      detail = data.detail || detail
    } catch {
      // ignore json parse error
    }

    throw {
      status: 401,
      message: typeof detail === 'string' ? detail : 'Sesión expirada o no autorizada',
      detail,
    } as ApiError
  }

  // Handle 409 Conflict (e.g. COOPERATIVA_INACTIVA)
  if (response.status === 409) {
    let detail: unknown = null
    let code: string | null = null
    let message = 'La cooperativa ha sido desactivada'
    try {
      const data = (await response.json()) as { detail?: { code?: string; message?: string } | string }
      detail = data.detail
      if (typeof detail === 'object' && detail !== null && 'code' in detail) {
        code = (detail as { code?: string }).code || null
        message = (detail as { message?: string }).message || message
      } else if (typeof detail === 'string') {
        message = detail
      }
    } catch {
      // ignore
    }

    if (code === 'COOPERATIVA_INACTIVA' || message.includes('desactivada')) {
      if (onCooperativaInactivaCallback) {
        onCooperativaInactivaCallback(message)
      }
    }

    throw {
      status: 409,
      message,
      detail,
    } as ApiError
  }

  // Handle other HTTP errors
  if (!response.ok) {
    let errorMessage = `Error HTTP ${response.status}`
    let errorDetail: unknown = null

    try {
      const errorData = (await response.json()) as {
        detail?: unknown
        message?: string
      }
      errorDetail = errorData.detail
      if (typeof errorData.detail === 'string') {
        errorMessage = errorData.detail
      } else if (Array.isArray(errorData.detail)) {
        // Pydantic validation errors
        errorMessage = (errorData.detail as Array<{ msg: string }>)
          .map((d) => d.msg)
          .join(', ')
      } else if (errorData.message) {
        errorMessage = errorData.message
      }
    } catch {
      errorMessage = response.statusText || errorMessage
    }

    throw {
      status: response.status,
      message: errorMessage,
      detail: errorDetail,
    } as ApiError
  }

  // Empty response body (e.g., 204 No Content)
  if (response.status === 204) {
    return {} as T
  }

  return (await response.json()) as T
}
