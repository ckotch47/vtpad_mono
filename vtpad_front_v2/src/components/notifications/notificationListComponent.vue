<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>
  <div v-if="!loader" class="d-flex justify-end my-2">
    <v-btn :prepend-icon="'mdi-notification-clear-all'" :text="'Read all'" variant="outlined" @click="readAllNotification" />
  </div>

  <div v-if="!loader">
    <v-alert v-if="loadError" type="error" variant="tonal" density="compact" class="mb-3" role="alert">
      {{ items.length ? 'Notifications could not be refreshed. Existing notifications are still shown.' : 'Notifications could not be loaded.' }}
      <v-btn size="small" variant="text" @click="getNotification(offset > 0)">Retry</v-btn>
    </v-alert>

    <v-list v-if="items">
      <v-list-item
      v-for="item in items"
      :key="item.id"
      :to="completedRunRoute(item) || undefined"
      :prepend-icon="!item.read ? 'mdi-vector-point' : 'mdi'"
      class="notification-list--item"
      @click="readNotification(item.id)"
      >
        <notification-list-item-update-component v-if="item.event === 'UPDATE'" :elem="item" />
        <notification-list-item-comment-component v-if="item.event === 'COMMENT'" :elem="item" />
        <notification-list-item-assign-component v-if="item.event === 'ASSIGN'" :elem="item" />
        <notification-list-item-run-completed-component v-if="item.event === 'RUN_COMPLETED'" :elem="item" />
      </v-list-item>
    </v-list>

    <v-btn
      v-if="isInfiniteScroll"
      ref="infinityScrollBtn"
      v-element-visibility="nextData"
      color="primary"
      width="100%"
      class="ma-4"
      text="Show more"
      @click="nextData"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { vElementVisibility } from '@vueuse/components'
import { notificationService } from '@/services'
import NotificationListItemAssignComponent from '@/components/notifications/listItem/notificationListItemAssignComponent.vue'
import NotificationListItemCommentComponent from '@/components/notifications/listItem/notificationListItemCommentComponent.vue'
import NotificationListItemUpdateComponent from '@/components/notifications/listItem/notificationListItemUpdateComponent.vue'
import NotificationListItemRunCompletedComponent from '@/components/notifications/listItem/notificationListItemRunCompletedComponent.vue'

const loader = ref(true)
const items = ref([])
const isInfiniteScroll = ref(false)
const loadError = ref(false)
const pageItems = ref(20)
const limit = ref(20)
const offset = ref(0)
const infinityScrollBtn = ref(null)

function readAllNotification() {
  notificationService.markAllRead().then(() => {
    items.value = items.value.map(item => ({ ...item, read: true }))
    window.dispatchEvent(new Event('vtpad:notification-count-refresh'))
    offset.value = 0
    getNotification()
  })
}

function completedRunRoute(item) {
  if (item.event !== 'RUN_COMPLETED') return null
  const route = item.data?.route
  if (typeof route !== 'string') return null

  const match = route.match(/^\/space\/([0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})\/test-runs\/([0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})$/i)
  return match ? route : null
}

function getNotification(append = false) {
  loader.value = items.value.length === 0
  loadError.value = false
  notificationService.list({
    limit: limit.value,
    skip: offset.value
  }).then(res => {
    if (res.data.length === 0 || res.data.length < pageItems.value) {
      isInfiniteScroll.value = false
    } else {
      isInfiniteScroll.value = true
    }
    if (res.data) {
      if (append) {
        items.value = items.value.concat(res.data)
      } else {
        items.value = res.data
      }
    }
  }).catch(() => {
    loadError.value = true
  }).finally(() => {
    loader.value = false
  })
}

function readNotification(event) {
  notificationService.markRead(event).then(res => {
    if (res.status && res.status === 200) {
      const item = items.value.find(value => value.id === event)
      if (item && !item.read) {
        item.read = true
        window.dispatchEvent(new Event('vtpad:notification-count-refresh'))
      }
    }
  })
}

function nextData() {
  offset.value += pageItems.value
  getNotification(true)
}

onMounted(getNotification)
</script>

<style lang="scss">
.notification-list--item {
  a {
    color: rgb(var(--v-theme-primary));
  }
}
</style>
