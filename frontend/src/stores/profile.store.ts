import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  ProfileService,
  type ProfileUpdateData,
  type ProfileUpdateResponse,
} from '@/services/profile.service'
import { useAuthStore } from '@/stores/auth.store'

export const useProfileStore = defineStore('profile', () => {
  const isSaving = ref(false)

  async function updateProfile(data: ProfileUpdateData): Promise<ProfileUpdateResponse> {
    const authStore = useAuthStore()
    isSaving.value = true
    try {
      const response = await ProfileService.updateProfile(data)
      // Changing the password revokes other sessions; this fresh token keeps the current one
      if (response.access_token) {
        authStore.setToken(response.access_token)
      }
      authStore.setUser(response.user)
      return response
    } finally {
      isSaving.value = false
    }
  }

  return { isSaving, updateProfile }
})

