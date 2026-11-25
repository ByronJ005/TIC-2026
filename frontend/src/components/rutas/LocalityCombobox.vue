<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { Check, ChevronDown, Info, Loader2, MapPin, Plus, Search, X } from '@lucide/vue'
import { useLocalities } from '@/composables/useLocalities'
import type { Locality } from '@/services/localidades.service'

const props = withDefaults(
  defineProps<{
    modelValue: number | null
    modelName?: string
    label?: string
    placeholder?: string
    error?: string
    disabled?: boolean
    excludeId?: number | null
    required?: boolean
  }>(),
  {
    modelValue: null,
    modelName: '',
    label: '',
    placeholder: 'Seleccionar localidad...',
    error: '',
    disabled: false,
    excludeId: null,
    required: false,
  },
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: number | null): void
  (e: 'selected', locality: Locality | null): void
  (e: 'blur'): void
}>()

const {
  localities,
  searchQuery,
  isLoading,
  exactMatch,
  fetchLocalities,
  handleSearchDebounced,
  createNewLocality,
} = useLocalities()

const isOpen = ref(false)
const containerRef = ref<HTMLElement | null>(null)
const selectedName = ref(props.modelName || '')
const isCreating = ref(false)

watch(
  () => props.modelName,
  (val) => {
    if (val !== undefined) {
      selectedName.value = val
    }
  },
)

watch(
  () => props.modelValue,
  (newId) => {
    if (!newId) {
      selectedName.value = ''
    } else if (localities.value.length > 0) {
      const match = localities.value.find((l) => l.id === newId)
      if (match) selectedName.value = match.name
    }
  },
)

const filteredLocalities = computed(() => {
  let list = localities.value
  if (props.excludeId) {
    list = list.filter((l) => l.id !== props.excludeId)
  }
  return list
})

const canCreateNew = computed(() => {
  const q = searchQuery.value.trim()
  if (!q) return false
  // CP-77: if an exact match exists (ignoring case and whitespace), do not show create button
  return exactMatch.value === null
})

function onInputSearch(e: Event) {
  const val = (e.target as HTMLInputElement).value
  searchQuery.value = val
  handleSearchDebounced(val)
  if (!isOpen.value) {
    isOpen.value = true
  }
}

function handleSelect(loc: Locality) {
  selectedName.value = loc.name
  searchQuery.value = ''
  isOpen.value = false
  emit('update:modelValue', loc.id)
  emit('selected', loc)
}

function handleClear(e: Event) {
  e.stopPropagation()
  selectedName.value = ''
  searchQuery.value = ''
  emit('update:modelValue', null)
  emit('selected', null)
}

async function handleCreateAndSelect() {
  const trimmed = searchQuery.value.trim().replace(/\s+/g, ' ')
  if (!trimmed) return
  isCreating.value = true
  try {
    const created = await createNewLocality(trimmed)
    handleSelect(created)
  } finally {
    isCreating.value = false
  }
}

function toggleDropdown() {
  if (props.disabled) return
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    fetchLocalities('')
  }
}

function handleClickOutside(event: MouseEvent) {
  if (containerRef.value && !containerRef.value.contains(event.target as Node)) {
    if (isOpen.value) {
      isOpen.value = false
      emit('blur')
    }
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  fetchLocalities('')
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div ref="containerRef" class="relative w-full text-left" data-test="locality-combobox">
    <label v-if="label" class="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
      {{ label }}
      <span v-if="required" class="text-destructive ml-0.5">*</span>
    </label>

    <div
      class="relative flex items-center w-full rounded-xl border bg-background text-sm transition-colors cursor-pointer select-none"
      :class="[
        error ? 'border-destructive focus-within:ring-destructive/30' : 'border-border focus-within:border-primary focus-within:ring-primary/20',
        disabled ? 'opacity-50 cursor-not-allowed bg-muted/30' : 'hover:border-primary/50',
        isOpen ? 'ring-2 ring-primary/20 border-primary' : '',
      ]"
      @click="toggleDropdown"
    >
      <div class="pl-3 text-muted-foreground shrink-0">
        <MapPin class="w-4 h-4" />
      </div>

      <div class="flex-1 px-2.5 py-2 overflow-hidden text-ellipsis whitespace-nowrap">
        <span v-if="selectedName" class="font-medium text-foreground">
          {{ selectedName }}
        </span>
        <span v-else class="text-muted-foreground">
          {{ placeholder }}
        </span>
      </div>

      <div class="pr-2.5 flex items-center gap-1 shrink-0">
        <button
          v-if="selectedName && !disabled"
          type="button"
          class="p-1 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted cursor-pointer transition-colors"
          title="Limpiar selección"
          @click="handleClear"
        >
          <X class="w-3.5 h-3.5" />
        </button>
        <ChevronDown
          class="w-4 h-4 text-muted-foreground transition-transform duration-200"
          :class="{ 'rotate-180': isOpen }"
        />
      </div>
    </div>

    <!-- Dropdown Panel -->
    <div
      v-if="isOpen && !disabled"
      class="absolute left-0 z-50 mt-1.5 w-full rounded-xl border border-border bg-card p-2 shadow-lg animate-in fade-in-50 zoom-in-95 duration-150"
      @click.stop
    >
      <!-- Search Input inside Dropdown -->
      <div class="relative flex items-center mb-2 px-1">
        <Search class="w-4 h-4 text-muted-foreground absolute left-3" />
        <input
          type="text"
          :value="searchQuery"
          class="w-full pl-8 pr-3 py-1.5 rounded-lg border border-border bg-background text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
          placeholder="Buscar o registrar localidad..."
          @input="onInputSearch"
        />
      </div>

      <!-- Disambiguation hint -->
      <div class="px-2.5 py-1.5 mb-2 mx-1 rounded-lg bg-muted/40 border border-border/80 text-[11px] text-muted-foreground flex items-start gap-1.5 leading-snug">
        <Info class="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
        <span>
          Si existe otra localidad con el mismo nombre, coloque el cantón entre paréntesis (ej: <em>El Tambo (Catamayo)</em> o <em>El Tambo (Cañar)</em>).
        </span>
      </div>

      <!-- Loading Indicator -->
      <div v-if="isLoading" class="flex items-center justify-center py-4 text-muted-foreground text-xs gap-2">
        <Loader2 class="w-4 h-4 animate-spin text-primary" />
        <span>Buscando localidades...</span>
      </div>

      <!-- Localities List -->
      <div v-else class="max-h-52 overflow-y-auto space-y-0.5 pr-0.5">
        <button
          v-for="loc in filteredLocalities"
          :key="loc.id"
          type="button"
          class="w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm text-foreground hover:bg-muted/60 transition-colors text-left cursor-pointer"
          :class="{
            'bg-primary/10 font-medium text-primary': loc.id === modelValue || (exactMatch && loc.id === exactMatch.id),
          }"
          @click="handleSelect(loc)"
        >
          <span class="truncate">{{ loc.name }}</span>
          <Check v-if="loc.id === modelValue" class="w-4 h-4 text-primary shrink-0 ml-2" />
        </button>

        <div
          v-if="filteredLocalities.length === 0 && !canCreateNew"
          class="py-4 text-center text-xs text-muted-foreground"
        >
          No se encontraron localidades
        </div>

        <!-- Option to Create New Locality (CP-77) -->
        <button
          v-if="canCreateNew"
          type="button"
          class="w-full flex items-center gap-2 px-3 py-2.5 mt-1 rounded-lg border border-dashed border-primary/40 bg-primary/5 text-primary text-xs font-semibold hover:bg-primary/10 transition-colors cursor-pointer text-left"
          :disabled="isCreating"
          data-test="create-locality-btn"
          @click="handleCreateAndSelect"
        >
          <Loader2 v-if="isCreating" class="w-3.5 h-3.5 animate-spin shrink-0" />
          <Plus v-else class="w-3.5 h-3.5 shrink-0" />
          <span class="truncate">Registrar y usar "{{ searchQuery.trim() }}"</span>
        </button>
      </div>
    </div>

    <!-- Error message -->
    <p v-if="error" class="text-xs font-medium text-destructive mt-1">
      {{ error }}
    </p>
  </div>
</template>
