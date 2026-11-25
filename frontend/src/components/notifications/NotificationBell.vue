<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { Bell, CheckCheck, Loader2 } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { useNotificacionesStore } from '@/stores/notificaciones.store'

const store = useNotificacionesStore()
const isOpen = ref(false)
const popoverRef = ref<HTMLElement | null>(null)

function togglePopover() {
  isOpen.value = !isOpen.value
  if (isOpen.value && store.notifications.length === 0) {
    store.fetchInitialNotifications()
  }
}

function closePopover(e: MouseEvent) {
  if (popoverRef.value && !popoverRef.value.contains(e.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  store.fetchInitialNotifications()
  document.addEventListener('click', closePopover)
})

onUnmounted(() => {
  document.removeEventListener('click', closePopover)
})

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  try {
    const d = new Date(dateStr)
    return d.toLocaleString('es-EC', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return dateStr
  }
}
</script>

<template>
  <div ref="popoverRef" class="relative inline-block text-left">
    <!-- Bell Button -->
    <Button
      variant="ghost"
      size="icon"
      class="relative rounded-xl text-muted-foreground hover:text-foreground hover:bg-muted cursor-pointer h-9 w-9"
      title="Notificaciones"
      aria-label="Abrir centro de notificaciones"
      data-test="notification-bell-btn"
      @click.stop="togglePopover"
    >
      <Bell class="w-5 h-5" />
      <span
        v-if="store.unreadCount > 0"
        data-test="notification-badge"
        class="absolute -top-1 -right-1 flex h-4 min-w-[16px] px-1 items-center justify-center rounded-full bg-destructive text-[10px] font-bold text-destructive-foreground animate-pulse"
      >
        {{ store.unreadCount > 99 ? '99+' : store.unreadCount }}
      </span>
    </Button>

    <!-- Popover Panel -->
    <div
      v-if="isOpen"
      data-test="notification-popover"
      class="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl bg-card border border-border shadow-xl z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-150"
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-4 py-3 border-b border-border bg-muted/30">
        <div class="flex items-center gap-2">
          <Bell class="w-4 h-4 text-primary" />
          <h3 class="font-semibold text-sm text-foreground">Notificaciones</h3>
          <span
            v-if="store.unreadCount > 0"
            class="text-xs px-1.5 py-0.5 rounded-full bg-primary/10 text-primary font-medium"
          >
            {{ store.unreadCount }} sin leer
          </span>
        </div>
        <Button
          v-if="store.unreadCount > 0"
          variant="ghost"
          size="sm"
          data-test="mark-all-read-btn"
          class="h-7 text-xs gap-1 text-muted-foreground hover:text-foreground cursor-pointer px-2"
          @click="store.markAllAsRead"
        >
          <CheckCheck class="w-3.5 h-3.5 text-primary" />
          <span>Marcar todas como leídas</span>
        </Button>
      </div>

      <!-- Notifications List -->
      <div class="max-h-80 overflow-y-auto divide-y divide-border">
        <!-- Empty State (CP-99) -->
        <div
          v-if="store.notifications.length === 0 && !store.isLoading"
          data-test="notification-empty"
          class="py-8 text-center text-sm text-muted-foreground px-4"
        >
          <Bell class="w-8 h-8 text-muted-foreground/40 mx-auto mb-2" />
          <p class="font-medium text-foreground">No tienes notificaciones</p>
          <p class="text-xs text-muted-foreground mt-0.5">Te avisaremos sobre eventos relevantes del terminal.</p>
        </div>

        <!-- Notification Items (CP-100) -->
        <div
          v-for="item in store.notifications"
          :key="item.id"
          data-test="notification-item"
          class="p-3.5 text-sm transition-colors hover:bg-muted/40 flex items-start gap-2.5"
          :class="[!item.is_read ? 'bg-primary/5' : 'bg-transparent']"
        >
          <span
            class="w-2 h-2 rounded-full mt-1.5 shrink-0"
            :class="[!item.is_read ? 'bg-primary' : 'bg-transparent']"
          ></span>
          <div class="flex-1 min-w-0">
            <h4 class="font-semibold text-xs text-foreground truncate">{{ item.title }}</h4>
            <p class="text-xs text-muted-foreground mt-0.5 leading-relaxed break-words">{{ item.message }}</p>
            <span class="text-[10px] text-muted-foreground/80 mt-1 block">{{ formatDate(item.created_at) }}</span>
          </div>
        </div>

        <div v-if="store.isLoading" class="py-4 text-center text-xs text-muted-foreground flex items-center justify-center gap-2">
          <Loader2 class="w-4 h-4 animate-spin text-primary" />
          <span>Cargando notificaciones...</span>
        </div>
      </div>

      <!-- Footer / Cargar Más (CP-101) -->
      <div v-if="store.hasMore" class="p-2 border-t border-border bg-muted/20 text-center">
        <Button
          variant="ghost"
          size="sm"
          data-test="load-more-notifs-btn"
          class="w-full h-8 text-xs text-primary hover:text-primary hover:bg-primary/10 cursor-pointer"
          :disabled="store.isLoading"
          @click="store.fetchMoreNotifications"
        >
          <span>Cargar más</span>
        </Button>
      </div>
    </div>
  </div>
</template>
