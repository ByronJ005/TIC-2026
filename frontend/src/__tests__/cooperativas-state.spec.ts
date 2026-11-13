import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useCooperativasStore } from '@/stores/cooperativas.store'
import { useCooperativaForm } from '@/composables/useCooperativaForm'
import { useCooperativaAdministrators } from '@/composables/useCooperativaAdministrators'
import { CooperativasService } from '@/services/cooperativas.service'

describe('Cooperativas Store & Composables', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  describe('useCooperativasStore', () => {
    it('initializes with default values and allows toggling viewMode', () => {
      const store = useCooperativasStore()
      expect(store.viewMode).toBe('cards')
      store.toggleViewMode()
      expect(store.viewMode).toBe('table')
      store.toggleViewMode()
      expect(store.viewMode).toBe('cards')
    })

    it('fetches cooperativas and sets state', async () => {
      const mockData = {
        items: [
          {
            id: 1,
            name: 'Coop Loja',
            ruc: '1104609829001',
            is_active: true,
            administradores: [],
            created_at: '2026-01-01T00:00:00Z',
            updated_at: '2026-01-01T00:00:00Z',
          },
        ],
        total: 1,
        page: 1,
        size: 12,
        total_pages: 1,
      }
      vi.spyOn(CooperativasService, 'getCooperativas').mockResolvedValue(mockData)

      const store = useCooperativasStore()
      await store.fetchCooperativas()
      expect(store.cooperativas.length).toBe(1)
      expect(store.cooperativas[0]?.name).toBe('Coop Loja')
      expect(store.total).toBe(1)
    })
  })

  describe('useCooperativaForm', () => {
    it('validates required name and RUC in create mode', () => {
      const { form, validateAll, errors } = useCooperativaForm()
      expect(validateAll()).toBe(false)
      expect(errors.name).toBeTruthy()
      expect(errors.ruc).toBeTruthy()

      form.name = 'Cooperativa Loja'
      form.ruc = '1104609829001'
      expect(validateAll()).toBe(true)
    })

    it('ignores RUC validation in edit mode', () => {
      const initialCoop = {
        id: 1,
        name: 'Coop Loja',
        ruc: '1104609829001',
        is_active: true,
        administradores: [],
        created_at: '',
        updated_at: '',
      }
      const { form, validateAll, isEditMode } = useCooperativaForm(initialCoop)
      expect(isEditMode.value).toBe(true)
      form.ruc = '' // even if empty, edit mode does not validate RUC
      expect(validateAll()).toBe(true)
    })
  })

  describe('useCooperativaAdministrators', () => {
    it('enforces maximum 3 users selection and disables remaining', () => {
      const { selectedUserIds, toggleUserSelection, isSelectionDisabled } =
        useCooperativaAdministrators()

      toggleUserSelection(1)
      toggleUserSelection(2)
      toggleUserSelection(3)
      expect(selectedUserIds.value).toEqual([1, 2, 3])

      // 4th selection is ignored because limit is 3
      toggleUserSelection(4)
      expect(selectedUserIds.value).toEqual([1, 2, 3])

      // isSelectionDisabled returns true for unselected user 4
      expect(isSelectionDisabled(4)).toBe(true)
      // but false for already selected user 2
      expect(isSelectionDisabled(2)).toBe(false)

      // unselecting user 2 allows selecting user 4
      toggleUserSelection(2)
      expect(isSelectionDisabled(4)).toBe(false)
      toggleUserSelection(4)
      expect(selectedUserIds.value).toEqual([1, 3, 4])
    })
  })
})
