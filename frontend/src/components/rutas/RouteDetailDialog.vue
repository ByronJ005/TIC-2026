<script setup lang="ts">
import { computed } from 'vue'
import {
  CheckCircle2,
  MapPin,
  Navigation,
  Route as RouteIcon,
  X,
  XCircle,
} from '@lucide/vue'
import { Button } from '@/components/ui/button'
import type { RouteDetail } from '@/services/rutas.service'

const props = defineProps<{
  isOpen: boolean
  route: RouteDetail | null
  isLoading?: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const formattedTime = computed(() => {
  if (!props.route?.estimated_time_minutes) return '0 min'
  const total = props.route.estimated_time_minutes
  const h = Math.floor(total / 60)
  const m = total % 60
  if (h > 0 && m > 0) return `${h}h ${m}m`
  if (h > 0) return `${h}h`
  return `${m}m`
})

const orderedStops = computed(() => {
  if (!props.route?.stops) return []
  return [...props.route.stops].sort((a, b) => a.stop_order - b.stop_order)
})
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 overflow-y-auto animate-in fade-in-50 duration-200"
    data-test="route-detail-dialog"
  >
    <div
      class="relative w-full max-w-xl rounded-2xl border border-border bg-card shadow-2xl my-8 overflow-hidden"
      @click.stop
    >
      <!-- Dialog Header -->
      <div class="flex items-center justify-between border-b border-border px-6 py-4 bg-muted/20">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <RouteIcon class="w-5 h-5" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-base font-bold text-foreground">
                {{ route?.name || 'Detalle de la ruta' }}
              </h2>
              <!-- Status Badge -->
              <span
                v-if="route"
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold"
                :class="
                  route.is_active
                    ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                    : 'bg-muted text-muted-foreground border border-border'
                "
              >
                <CheckCircle2 v-if="route.is_active" class="w-3 h-3" />
                <XCircle v-else class="w-3 h-3" />
                {{ route.is_active ? 'Activa' : 'Inactiva' }}
              </span>
            </div>
            <p class="text-xs text-muted-foreground">
              {{ route?.cooperativa_id ? 'Ruta específica de cooperativa' : 'Ruta general del sistema' }}
            </p>
          </div>
        </div>

        <button
          type="button"
          class="rounded-xl p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors cursor-pointer"
          title="Cerrar"
          @click="emit('close')"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Dialog Body -->
      <div v-if="route" class="p-6 space-y-5 max-h-[75vh] overflow-y-auto">
        <!-- Origin & Destination Banner -->
        <div class="flex items-center justify-between p-4 rounded-xl border border-border bg-muted/20">
          <div class="flex items-center gap-3">
            <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-background border border-border text-primary font-bold">
              <MapPin class="w-4 h-4" />
            </div>
            <div>
              <span class="text-[10px] uppercase font-semibold text-muted-foreground tracking-wider">Origen</span>
              <p class="font-bold text-sm text-foreground">{{ route.origin_name }}</p>
            </div>
          </div>

          <div class="flex flex-col items-center px-4">
            <span class="text-[11px] font-mono text-muted-foreground font-medium">{{ route.distance_km }} km</span>
            <div class="w-16 h-0.5 bg-border my-1 relative">
              <div class="w-2 h-2 rounded-full bg-primary absolute right-0 -top-[3px]"></div>
            </div>
            <span class="text-[11px] font-mono text-muted-foreground font-medium">{{ formattedTime }}</span>
          </div>

          <div class="flex items-center gap-3">
            <div class="text-right">
              <span class="text-[10px] uppercase font-semibold text-muted-foreground tracking-wider">Destino</span>
              <p class="font-bold text-sm text-foreground">{{ route.destination_name }}</p>
            </div>
            <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-background border border-border text-primary font-bold">
              <Navigation class="w-4 h-4" />
            </div>
          </div>
        </div>

        <!-- Metrics cards -->
        <div class="grid grid-cols-2 gap-3 text-xs">
          <div class="p-3 rounded-xl border border-border bg-card">
            <span class="text-muted-foreground font-medium">Distancia total</span>
            <p class="text-base font-bold text-foreground mt-0.5">{{ route.distance_km }} km</p>
          </div>
          <div class="p-3 rounded-xl border border-border bg-card">
            <span class="text-muted-foreground font-medium">Tiempo estimado</span>
            <p class="text-base font-bold text-foreground mt-0.5">{{ formattedTime }}</p>
          </div>
        </div>

        <!-- Intermediate Stops -->
        <div class="space-y-2">
          <span class="block text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Paradas intermedias
          </span>

          <div v-if="orderedStops.length > 0" class="space-y-1.5">
            <div
              v-for="stop in orderedStops"
              :key="stop.locality_id"
              class="flex items-center gap-3 p-2.5 rounded-xl border border-border bg-muted/10 text-xs"
            >
              <span class="flex items-center justify-center w-5 h-5 rounded-md bg-primary/10 text-primary font-bold">
                {{ stop.stop_order }}
              </span>
              <span class="font-medium text-foreground">{{ stop.locality_name }}</span>
            </div>
          </div>

          <div
            v-else
            class="p-3 rounded-xl border border-dashed border-border bg-muted/5 text-xs text-muted-foreground text-center"
          >
            Directa (sin paradas intermedias)
          </div>
        </div>

        <!-- Description -->
        <div v-if="route.description" class="space-y-1">
          <span class="block text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Descripción
          </span>
          <p class="text-xs text-foreground bg-muted/20 p-3 rounded-xl border border-border leading-relaxed">
            {{ route.description }}
          </p>
        </div>

      </div>

      <!-- Dialog Footer -->
      <div class="flex items-center justify-end border-t border-border px-6 py-4 bg-muted/10">
        <Button
          type="button"
          class="rounded-xl cursor-pointer"
          @click="emit('close')"
        >
          Cerrar
        </Button>
      </div>
    </div>
  </div>
</template>
