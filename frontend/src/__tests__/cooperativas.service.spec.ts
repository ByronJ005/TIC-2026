import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { setCooperativaInactivaHandler } from '@/services/api-client'
import { CooperativasService } from '@/services/cooperativas.service'

describe('CooperativasService and 409 Interceptor', () => {
  const originalFetch = global.fetch

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    global.fetch = originalFetch
  })

  it('calls getCooperativas with correct query parameters', async () => {
    const mockResponse = {
      items: [{ id: 1, name: 'Coop Loja', ruc: '1104609829001', is_active: true, administradores: [] }],
      total: 1,
      page: 1,
      size: 10,
      total_pages: 1,
    }

    global.fetch = vi.fn<typeof fetch>().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockResponse,
    } as Response)

    const res = await CooperativasService.getCooperativas({ page: 1, size: 10, search: 'Loja', is_active: true })
    expect(res.total).toBe(1)
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/cooperativas?page=1&size=10&search=Loja&is_active=true'),
      expect.anything(),
    )
  })

  it('calls createCooperativa with JSON body', async () => {
    const mockCoop = { id: 2, name: 'Coop Sur', ruc: '1790011216001', is_active: true, administradores: [] }

    global.fetch = vi.fn<typeof fetch>().mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => mockCoop,
    } as Response)

    const res = await CooperativasService.createCooperativa({
      name: 'Coop Sur',
      ruc: '1790011216001',
    })
    expect(res.id).toBe(2)
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/cooperativas'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ name: 'Coop Sur', ruc: '1790011216001' }),
      }),
    )
  })

  it('triggers setCooperativaInactivaHandler on 409 COOPERATIVA_INACTIVA', async () => {
    const handler = vi.fn<(msg: string) => void>()
    setCooperativaInactivaHandler(handler)

    global.fetch = vi.fn<typeof fetch>().mockResolvedValue({
      ok: false,
      status: 409,
      json: async () => ({
        detail: {
          code: 'COOPERATIVA_INACTIVA',
          message: 'La cooperativa ha sido desactivada',
        },
      }),
    } as Response)

    await expect(
      CooperativasService.updateCooperativa(1, { name: 'Nuevo' }),
    ).rejects.toMatchObject({ message: 'La cooperativa ha sido desactivada' })

    expect(handler).toHaveBeenCalledWith('La cooperativa ha sido desactivada')
  })
})
