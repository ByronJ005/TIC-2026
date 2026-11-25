<script setup lang="ts">
import { Clock } from '@lucide/vue'

defineProps<{
  hours: string
  minutes: string
  error?: string
  disabled?: boolean
  required?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:hours', val: string): void
  (e: 'update:minutes', val: string): void
  (e: 'blur'): void
}>()

function filterNumericKey(e: KeyboardEvent, currentVal: string) {
  // Allow control keys: backspace, tab, enter, delete, arrows, escape
  if (
    ['Backspace', 'Tab', 'Enter', 'Delete', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Escape'].includes(
      e.key,
    ) ||
    // Allow Ctrl/Cmd + A, C, V, X
    (e.ctrlKey || e.metaKey)
  ) {
    return
  }

  // Reject anything that is not a single digit 0-9
  if (!/^\d$/.test(e.key)) {
    e.preventDefault()
    return
  }

  // Limit to at most 2 digits
  const target = e.target as HTMLInputElement
  const hasSelection = (target.selectionEnd ?? 0) - (target.selectionStart ?? 0) > 0
  if (!hasSelection && currentVal.length >= 2) {
    e.preventDefault()
  }
}

function onHoursInput(e: Event) {
  const target = e.target as HTMLInputElement
  const sanitized = target.value.replace(/\D/g, '').slice(0, 2)
  target.value = sanitized
  emit('update:hours', sanitized)
}

function onMinutesInput(e: Event) {
  const target = e.target as HTMLInputElement
  const sanitized = target.value.replace(/\D/g, '').slice(0, 2)
  target.value = sanitized
  emit('update:minutes', sanitized)
}
</script>

<template>
  <div class="w-full text-left" data-test="route-time-input">
    <label class="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
      Tiempo estimado
      <span v-if="required" class="text-destructive ml-0.5">*</span>
    </label>

    <div class="flex items-center gap-3">
      <!-- Hours (max 2 digits) -->
      <div class="flex-1 relative flex items-center">
        <input
          type="text"
          inputmode="numeric"
          pattern="[0-9]*"
          maxlength="2"
          :value="hours"
          :disabled="disabled"
          placeholder="0"
          class="w-full pl-3 pr-14 py-2 rounded-xl border bg-background text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-colors disabled:opacity-50 disabled:bg-muted/30"
          :class="error ? 'border-destructive' : 'border-border'"
          data-test="time-hours-input"
          @keydown="filterNumericKey($event, hours)"
          @input="onHoursInput"
          @blur="$emit('blur')"
        />
        <span class="absolute right-3 text-xs font-medium text-muted-foreground pointer-events-none select-none">
          hrs
        </span>
      </div>

      <span class="text-muted-foreground font-semibold">:</span>

      <!-- Minutes (max 2 digits) -->
      <div class="flex-1 relative flex items-center">
        <input
          type="text"
          inputmode="numeric"
          pattern="[0-9]*"
          maxlength="2"
          :value="minutes"
          :disabled="disabled"
          placeholder="0"
          class="w-full pl-3 pr-14 py-2 rounded-xl border bg-background text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-colors disabled:opacity-50 disabled:bg-muted/30"
          :class="error ? 'border-destructive' : 'border-border'"
          data-test="time-minutes-input"
          @keydown="filterNumericKey($event, minutes)"
          @input="onMinutesInput"
          @blur="$emit('blur')"
        />
        <span class="absolute right-3 text-xs font-medium text-muted-foreground pointer-events-none select-none">
          min
        </span>
      </div>

      <div class="hidden sm:flex items-center text-muted-foreground shrink-0">
        <Clock class="w-4 h-4" />
      </div>
    </div>

    <!-- Error message -->
    <p v-if="error" class="text-xs font-medium text-destructive mt-1">
      {{ error }}
    </p>
  </div>
</template>
