<script setup lang="ts">
import { CheckCircle2, Eye, Pencil, Power, Route as RouteIcon, XCircle } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import type { Route } from '@/services/rutas.service'

defineProps<{
  routes: Route[]
  isLoading?: boolean
}>()

const emit = defineEmits<{
  (e: 'view', route: Route): void
  (e: 'edit', route: Route): void
  (e: 'toggleStatus', route: Route): void
}>()

function formatTime(minutes: number): string {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  if (h > 0 && m > 0) return `${h}h ${m}m`
  if (h > 0) return `${h}h`
  return `${m}m`
}
</script>

<template>
  <div class="overflow-x-auto rounded-xl border border-border bg-card shadow-xs" data-test="general-routes-table">
    <table class="w-full text-left text-sm text-foreground">
      <thead class="border-b border-border bg-muted/40 text-xs font-semibold uppercase text-muted-foreground">
        <tr>
          <th scope="col" class="px-5 py-3.5">Ruta</th>
          <th scope="col" class="px-5 py-3.5">Trayecto</th>
          <th scope="col" class="px-5 py-3.5">Distancia / Tiempo</th>
          <th scope="col" class="px-5 py-3.5">Estado</th>
          <th scope="col" class="px-5 py-3.5 text-right">Acciones</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-border">
        <tr
          v-for="r in routes"
          :key="r.id"
          class="transition-colors hover:bg-muted/20"
          :class="{ 'opacity-70 bg-muted/10': !r.is_active }"
        >
          <!-- Name -->
          <td class="px-5 py-4 font-semibold text-foreground">
            <div class="flex items-center gap-2.5">
              <div
                class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-border bg-muted/40 text-primary"
              >
                <RouteIcon class="w-4 h-4" />
              </div>
              <span class="truncate max-w-xs">{{ r.name }}</span>
            </div>
          </td>

          <!-- Origin -> Dest -->
          <td class="px-5 py-4 text-xs">
            <div class="flex items-center gap-1.5 font-medium">
              <span>{{ r.origin_name }}</span>
              <span class="text-muted-foreground">→</span>
              <span>{{ r.destination_name }}</span>
            </div>
          </td>

          <!-- Distance / Time -->
          <td class="px-5 py-4 text-xs font-mono text-muted-foreground">
            <div>{{ r.distance_km }} km</div>
            <div class="text-[11px]">{{ formatTime(r.estimated_time_minutes) }}</div>
          </td>

          <!-- Status -->
          <td class="px-5 py-4">
            <span
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold"
              :class="
                r.is_active
                  ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                  : 'bg-muted text-muted-foreground border border-border'
              "
            >
              <CheckCircle2 v-if="r.is_active" class="w-3 h-3" />
              <XCircle v-else class="w-3 h-3" />
              {{ r.is_active ? 'Activa' : 'Inactiva' }}
            </span>
          </td>

          <!-- Actions -->
          <td class="px-5 py-4 text-right">
            <div class="flex items-center justify-end gap-1.5">
              <!-- View Detail -->
              <Button
                variant="ghost"
                size="icon"
                class="h-8 w-8 rounded-lg text-muted-foreground hover:text-foreground cursor-pointer"
                title="Ver detalle"
                data-test="view-route-btn"
                @click="emit('view', r)"
              >
                <Eye class="w-4 h-4" />
              </Button>

              <!-- Edit -->
              <Button
                variant="ghost"
                size="icon"
                class="h-8 w-8 rounded-lg text-muted-foreground hover:text-foreground cursor-pointer"
                title="Editar ruta"
                data-test="edit-route-btn"
                @click="emit('edit', r)"
              >
                <Pencil class="w-4 h-4" />
              </Button>

              <!-- Toggle Active -->
              <Button
                variant="ghost"
                size="icon"
                class="h-8 w-8 rounded-lg cursor-pointer"
                :class="
                  r.is_active
                    ? 'text-muted-foreground hover:text-destructive hover:bg-destructive/10'
                    : 'text-emerald-600 hover:bg-emerald-500/10'
                "
                :title="r.is_active ? 'Desactivar ruta' : 'Activar ruta'"
                data-test="toggle-status-btn"
                @click="emit('toggleStatus', r)"
              >
                <Power class="w-4 h-4" />
              </Button>
            </div>
          </td>
        </tr>

        <tr v-if="routes.length === 0">
          <td colspan="5" class="px-5 py-8 text-center text-sm text-muted-foreground">
            No se encontraron rutas generales que coincidan con los criterios.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
