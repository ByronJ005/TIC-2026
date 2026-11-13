import { reactive, computed } from 'vue'
import {
  validateAddress,
  validateCooperativaName,
  validateEcuadorianRuc,
  validateEmail,
  validatePhone,
} from './useFormValidation'
import type { Cooperativa, CooperativaCreatePayload, CooperativaUpdatePayload } from '@/services/cooperativas.service'

export interface CooperativaFormState {
  name: string
  ruc: string
  address: string
  phone: string
  email: string
  logo_url: string
  logo_file: File | null
}

export function useCooperativaForm(cooperativaSource?: Cooperativa | null | (() => Cooperativa | null)) {
  const isEditMode = computed(() => {
    if (typeof cooperativaSource === 'function') {
      return cooperativaSource() !== null
    }
    return cooperativaSource !== null && cooperativaSource !== undefined
  })

  const form = reactive<CooperativaFormState>({
    name: '',
    ruc: '',
    address: '',
    phone: '',
    email: '',
    logo_url: '',
    logo_file: null,
  })

  // Initialize form if a static cooperativa object was passed
  const initial = typeof cooperativaSource === 'function' ? cooperativaSource() : cooperativaSource
  if (initial) {
    form.name = initial.name || ''
    form.ruc = initial.ruc || ''
    form.address = initial.address || ''
    form.phone = initial.phone || ''
    form.email = initial.email || ''
    form.logo_url = initial.logo_url || ''
  }

  const errors = reactive<Record<string, string>>({
    name: '',
    ruc: '',
    address: '',
    phone: '',
    email: '',
    logo: '',
  })

  function validateField(field: keyof CooperativaFormState): boolean {
    errors[field] = ''

    if (field === 'name') {
      const res = validateCooperativaName(form.name)
      if (!res.isValid) {
        errors.name = res.errorMessage
        return false
      }
    }

    if (field === 'ruc' && !isEditMode.value) {
      const res = validateEcuadorianRuc(form.ruc)
      if (!res.isValid) {
        errors.ruc = res.errorMessage
        return false
      }
    }

    if (field === 'address' && form.address.trim()) {
      const res = validateAddress(form.address)
      if (!res.isValid) {
        errors.address = res.errorMessage
        return false
      }
    }

    if (field === 'phone' && form.phone.trim()) {
      const res = validatePhone(form.phone)
      if (!res.isValid) {
        errors.phone = res.errorMessage
        return false
      }
    }

    if (field === 'email' && form.email.trim()) {
      const res = validateEmail(form.email)
      if (!res.isValid) {
        errors.email = res.errorMessage
        return false
      }
    }

    if (field === 'logo_url' && form.logo_url.trim()) {
      const url = form.logo_url.trim()
      const isAllowed = isEditMode.value
        ? url.startsWith('http://') || url.startsWith('https://') || url.startsWith('/static/') || url.startsWith('/')
        : url.startsWith('http://') || url.startsWith('https://')

      if (!isAllowed) {
        errors.logo = isEditMode.value
          ? 'La URL del logo debe comenzar con http://, https:// o /static/'
          : 'La URL del logo debe comenzar con http:// o https://'
        return false
      }
      if (url.length > 500) {
        errors.logo = 'La URL del logo no puede exceder los 500 caracteres'
        return false
      }
    }

    return true
  }

  function validateAll(): boolean {
    const isNameValid = validateField('name')
    const isRucValid = isEditMode.value ? true : validateField('ruc')
    const isAddressValid = validateField('address')
    const isPhoneValid = validateField('phone')
    const isEmailValid = validateField('email')
    const isLogoValid = validateField('logo_url')

    return isNameValid && isRucValid && isAddressValid && isPhoneValid && isEmailValid && isLogoValid
  }

  function getCreatePayload(): CooperativaCreatePayload {
    return {
      name: form.name.trim(),
      ruc: form.ruc.trim(),
      address: form.address.trim() || null,
      phone: form.phone.trim() || null,
      email: form.email.trim().toLowerCase() || null,
      logo_url: form.logo_url.trim() || null,
    }
  }

  function getUpdatePayload(): CooperativaUpdatePayload {
    return {
      name: form.name.trim(),
      address: form.address.trim() || null,
      phone: form.phone.trim() || null,
      email: form.email.trim().toLowerCase() || null,
      logo_url: form.logo_url.trim() || null,
    }
  }

  function setLogoFile(file: File | null) {
    form.logo_file = file
  }

  return {
    form,
    errors,
    isEditMode,
    validateField,
    validateAll,
    getCreatePayload,
    getUpdatePayload,
    setLogoFile,
  }
}
