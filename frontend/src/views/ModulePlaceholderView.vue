<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Layers } from '@lucide/vue'

const route = useRoute()

const moduleTitle = computed(() => {
  return (route.meta?.title as string)?.replace(' - BoletoYa', '') || 'Módulo'
})

const moduleDescription = computed(() => {
  return (
    (route.meta?.description as string) ||
    'Este módulo está planificado para implementaciones posteriores.'
  )
})
</script>

<template>
  <div class="space-y-6">
    <div class="rounded-2xl border border-border bg-card p-8 sm:p-12 text-center shadow-xs">
      <div class="mx-auto w-16 h-16 rounded-2xl bg-primary/10 text-primary flex items-center justify-center mb-4">
        <Layers class="w-8 h-8" />
      </div>
      <h2 class="text-2xl font-bold tracking-tight text-foreground">
        {{ moduleTitle }}
      </h2>
      <p class="mt-2 text-sm text-muted-foreground max-w-md mx-auto">
        {{ moduleDescription }}
      </p>
      <div class="mt-6 inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-muted text-muted-foreground border border-border">
        <span>En construcción</span>
      </div>
    </div>
  </div>
</template>

