<script setup lang="ts">
import { Building2, Settings } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { resolveLogoUrl, type Cooperativa } from '@/services/cooperativas.service'

defineProps<{
  cooperativas: Cooperativa[]
}>()

const emit = defineEmits<{
  (e: 'edit', cooperativa: Cooperativa): void
  (e: 'toggleStatus', cooperativa: Cooperativa): void
}>()
</script>

<template>
  <div class="overflow-x-auto rounded-xl border border-border bg-card shadow-sm" data-testid="cooperativa-table">
    <table class="w-full text-left text-sm text-foreground">
      <thead class="border-b border-border bg-muted/40 text-xs font-semibold uppercase text-muted-foreground">
        <tr>
          <th scope="col" class="px-5 py-3.5">Cooperativa</th>
          <th scope="col" class="px-5 py-3.5">RUC</th>
          <th scope="col" class="px-5 py-3.5">Contacto</th>
          <th scope="col" class="px-5 py-3.5">Personal Asignado</th>
          <th scope="col" class="px-5 py-3.5">Estado</th>
          <th scope="col" class="px-5 py-3.5 text-right">Acciones</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-border">
        <tr
          v-for="coop in cooperativas"
          :key="coop.id"
          class="transition-colors hover:bg-muted/20"
          :class="{ 'opacity-75': !coop.is_active }"
        >
          <!-- Logo & Name -->
          <td class="px-5 py-4">
            <div class="flex items-center gap-3">
              <div
                class="flex h-10 w-10 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-border bg-muted/30"
              >
                <img
                  v-if="resolveLogoUrl(coop.logo_url)"
                  :src="resolveLogoUrl(coop.logo_url)!"
                  :alt="coop.name"
                  class="h-full w-full object-cover"
                />
                <Building2 v-else class="h-5 w-5 text-muted-foreground" />
              </div>
              <div>
                <p class="font-medium text-foreground">{{ coop.name }}</p>
                <p v-if="coop.address" class="text-xs text-muted-foreground truncate max-w-xs">
                  {{ coop.address }}
                </p>
              </div>
            </div>
          </td>

          <!-- RUC -->
          <td class="px-5 py-4 font-mono text-xs text-muted-foreground">
            {{ coop.ruc }}
          </td>

          <!-- Contact (Phone / Email) -->
          <td class="px-5 py-4 text-xs">
            <p v-if="coop.phone" class="text-foreground">{{ coop.phone }}</p>
            <p v-if="coop.email" class="text-muted-foreground">{{ coop.email }}</p>
            <span v-if="!coop.phone && !coop.email" class="text-muted-foreground italic">
              Sin datos
            </span>
          </td>

          <!-- Admins count and names -->
          <td class="px-5 py-4 text-xs">
            <div class="font-medium text-foreground">
              {{ coop.administradores.length }} / 3
            </div>
            <p
              v-if="coop.administradores.length > 0"
              class="text-muted-foreground truncate max-w-[200px]"
            >
              {{ coop.administradores.map((a) => `${a.first_name} ${a.last_name}`).join(', ') }}
            </p>
            <span v-else class="text-muted-foreground italic">
              Sin administradores
            </span>
          </td>

          <!-- Status -->
          <td class="px-5 py-4">
            <span
              class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium border"
              :class="
                coop.is_active
                  ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20 dark:text-emerald-400'
                  : 'bg-rose-500/10 text-rose-600 border-rose-500/20 dark:text-rose-400'
              "
            >
              {{ coop.is_active ? 'Activa' : 'Desactivada' }}
            </span>
          </td>

          <!-- Actions -->
          <td class="px-5 py-4 text-right">
            <div class="flex items-center justify-end gap-2">
              <Button
                variant="outline"
                size="sm"
                class="gap-1 text-xs"
                @click="emit('edit', coop)"
                data-testid="table-edit-cooperativa-button"
              >
                <Settings class="h-3.5 w-3.5" />
                Configurar
              </Button>

              <Button
                variant="ghost"
                size="sm"
                class="text-xs"
                :class="
                  coop.is_active
                    ? 'text-rose-600 hover:text-rose-700 hover:bg-rose-50 dark:hover:bg-rose-950/20'
                    : 'text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50 dark:hover:bg-emerald-950/20'
                "
                @click="emit('toggleStatus', coop)"
              >
                {{ coop.is_active ? 'Desactivar' : 'Activar' }}
              </Button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

