<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>
  <div v-if="!loader" class="d-flex justify-end my-2">
    <v-btn :prepend-icon="'mdi-notification-clear-all'" :text="'Read all'" variant="outlined" @click="readAllNotification" />
  </div>

  <div v-if="!loader">
    <v-list v-if="items">
      <v-list-item
        v-for="item in items"
        :key="item.id"
        :value="item.id"
        :prepend-icon="!item.read ? 'mdi-vector-point' : 'mdi'"
        class="notification-list--item"
        @click="readNotification(item.id)"
      >
        <notification-list-item-update-component v-if="item.event === 'UPDATE'" :elem="item" />
        <notification-list-item-comment-component v-if="item.event === 'COMMENT'" :elem="item" />
        <notification-list-item-assign-component v-if="item.event === 'ASSIGN'" :elem="item" />
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

const loader = ref(true)
const items = ref([])
const isInfiniteScroll = ref(false)
const pageItems = ref(20)
const limit = ref(20)
const offset = ref(0)
const infinityScrollBtn = ref(null)

function readAllNotification() {
  notificationService.markAllRead().then(() => {
    loader.value = true
    getNotification()
  })
}

function getNotification(append = false) {
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
    loader.value = false
  })
}

function readNotification(event) {
  notificationService.markRead(event).then(res => {
    if (res.status && res.status === 200) {
      items.value.find(value => value.id === event).read = true
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
