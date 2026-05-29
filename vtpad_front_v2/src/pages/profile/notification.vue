<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <notification-list-component />
  </v-container>
</template>

<script setup>
import NotificationListComponent from '@/components/notifications/notificationListComponent.vue'
</script>
<route>
{
  meta: {
    layout: "profile",
    tabValue: "notification"
  }
}
</route>
