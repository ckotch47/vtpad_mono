<template>
  <v-badge
    v-if="unreadCount > 0"
    :content="unreadCount"
    color="error"
    offset-x="-8"
    offset-y="8"
  >
    <v-btn
      color="grey-lighten-1"
      icon="mdi-bell-ring"
      variant="plain"
      to="/profile/notification"
      aria-label="Notifications"
    />
  </v-badge>
  <v-btn
    v-else
    color="grey-lighten-1"
    icon="mdi-bell-ring"
    variant="plain"
    to="/profile/notification"
    aria-label="Notifications"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { notificationService } from '@/services'
import { toast } from 'vue3-toastify'
import { EventSource } from 'extended-eventsource'

const props = defineProps({
  count: Number,
  userId: String
})

const unreadCount = ref(0)
const audio = ref(new Audio('/ring.mp3'))

function getNotificationCount() {
  notificationService.unreadCount().then(res => {
    if (res.data) {
      unreadCount.value = res.data
    }
  })
}

function sseNotification() {
  const eventSource = new EventSource('/api/v1/notification/stream', {
    headers: {
      Authorization: 'Bearer ' + localStorage.getItem('auth_token')
    }
  })
  subscribeEvents(eventSource)
}

function subscribeEvents(eventSource) {
  eventSource.addEventListener('UPDATE', async e => {
    const res = JSON.parse(e.data)
    if (res.short_name) {
      showToast(`UPDATE ${res.short_name}`)
    }
  }, { once: false })

  eventSource.addEventListener('ASSIGN', async e => {
    const res = JSON.parse(e.data)
    if (res.short_name) {
      showToast(`You assigned ${res.short_name}`)
    }
  }, { once: false })

  eventSource.addEventListener('COMMENT', async e => {
    const res = JSON.parse(e.data)
    if (res.short_name) {
      showToast(`New comment in ${res.short_name}`)
    }
  }, { once: false })
}

function showToast(text) {
  unreadCount.value++
  audio.value.play()
  toast.info(`${text}`, {
    autoClose: 9000
  })
}

onMounted(() => {
  sseNotification()
  getNotificationCount()
})
</script>

<style scoped>
</style>
