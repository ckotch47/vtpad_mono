<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <notification-list-component />
  </v-container>
</template>

<script>
import NotificationListComponent from "@/components/notifications/notificationListComponent.vue";

export default {
  name: "notificationPage",
  components: {NotificationListComponent}
}
</script>

<style scoped>

</style>
