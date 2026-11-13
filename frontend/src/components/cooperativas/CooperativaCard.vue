<script setup lang="ts">
import { computed } from 'vue'
import { Building2, Mail, MapPin, Phone, Settings, Users } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { resolveLogoUrl, type Cooperativa } from '@/services/cooperativas.service'

const props = defineProps<{
  cooperativa: Cooperativa
}>()

const emit = defineEmits<{
  (e: 'edit', cooperativa: Cooperativa): void
  (e: 'toggleStatus', cooperativa: Cooperativa): void
}>()

const adminCount = computed(() => props.cooperativa.administradores?.length || 0)
</script>

<template>
  <div
    class="flex flex-col justify-between rounded-xl border border-border bg-card p-5 shadow-sm transition-all hover:shadow-md"
    :class="{ 'opacity-85': !cooperativa.is_active }"
    data-testid="cooperativa-card"
  >
    <!-- Header: Logo, Name, Status Badge -->
    <div>
      <div class="flex items-start justify-between gap-3">
        <div class="flex items-center gap-3">
          <div
            class="flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-border bg-muted/30"
          >
            <img
              v-if="resolveLogoUrl(cooperativa.logo_url)"
              :src="resolveLogoUrl(cooperativa.logo_url)!"
              :alt="cooperativa.name"
              class="h-full w-full object-cover"
            />
            <Building2 v-else class="h-6 w-6 text-muted-foreground" />
          </div>
          <div>
            <h3 class="font-semibold text-foreground text-base leading-tight">
              {{ cooperativa.name }}
            </h3>
            <p class="text-xs text-muted-foreground">RUC: {{ cooperativa.ruc }}</p>
          </div>
        </div>

        <span
          class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium border"
          :class="
            cooperativa.is_active
              ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20 dark:text-emerald-400'
              : 'bg-rose-500/10 text-rose-600 border-rose-500/20 dark:text-rose-400'
          "
        >
          {{ cooperativa.is_active ? 'Activa' : 'Desactivada' }}
        </span>
      </div>

      <!-- Info items -->
      <div class="mt-4 space-y-2 text-xs text-muted-foreground">
        <div v-if="cooperativa.address" class="flex items-center gap-2">
          <MapPin class="h-3.5 w-3.5 shrink-0" />
          <span class="truncate">{{ cooperativa.address }}</span>
        </div>
        <div v-if="cooperativa.phone" class="flex items-center gap-2">
          <Phone class="h-3.5 w-3.5 shrink-0" />
          <span>{{ cooperativa.phone }}</span>
        </div>
        <div v-if="cooperativa.email" class="flex items-center gap-2">
          <Mail class="h-3.5 w-3.5 shrink-0" />
          <span class="truncate">{{ cooperativa.email }}</span>
        </div>
        <div class="flex items-center gap-2 pt-1 font-medium text-foreground">
          <Users class="h-3.5 w-3.5 text-primary" />
          <span>
            Personal: {{ adminCount }} / 3
            {{ adminCount === 1 ? 'administrador' : 'administradores' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Actions Footer -->
    <div class="mt-5 flex items-center justify-between border-t border-border pt-4">
      <Button
        variant="outline"
        size="sm"
        class="gap-1.5 text-xs"
        @click="emit('edit', cooperativa)"
        data-testid="edit-cooperativa-button"
      >
        <Settings class="h-3.5 w-3.5" />
        Configurar
      </Button>

      <Button
        variant="ghost"
        size="sm"
        class="text-xs"
        :class="
          cooperativa.is_active
            ? 'text-rose-600 hover:text-rose-700 hover:bg-rose-50 dark:hover:bg-rose-950/20'
            : 'text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50 dark:hover:bg-emerald-950/20'
        "
        @click="emit('toggleStatus', cooperativa)"
      >
        {{ cooperativa.is_active ? 'Desactivar' : 'Activar' }}
      </Button>
    </div>
  </div>
</template>

