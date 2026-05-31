<template>
  <v-app>
    <v-tabs
      fixed-tabs
      align-tabs="start"
      color="primary"
      v-model="tab"
      class="rounded-0_custom"
    >
      <v-tab :to="`/profile`" value="profile">Profile</v-tab>
      <v-tab :to="`/profile/notification`" value="notification">Notifications</v-tab>
      <v-tab :to="`/profile/api-tokens`" value="api-tokens">API Tokens</v-tab>
    </v-tabs>
    <router-view />
  </v-app>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const tab = ref(route.meta?.tabValue)

watch(() => route.meta?.tabValue, (val) => {
  tab.value = val
})
</script>

<style scoped>
.rounded-0_custom :deep(.v-tab) {
  text-transform: none;
}
</style>
