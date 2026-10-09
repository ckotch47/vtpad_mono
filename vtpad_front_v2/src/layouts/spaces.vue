<template>
  <v-app class="space-layout">
    <router-view :key="route.params.spaceId" />
  </v-app>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<style scoped>
/* Keep standard Space pages centred despite the legacy .custom-container reset. */
.space-layout :deep(.v-container.custom-container.max-width-1500) {
  margin-inline: auto !important;
}
</style>
