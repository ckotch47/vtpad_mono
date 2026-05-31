<template>
  <v-app>
    <v-tabs
      fixed-tabs
      align-tabs="start"
      color="primary"
      v-model="tab"
      class="rounded-0_custom"
    >
      <v-tab :to="`/company/users`" value="users">Users</v-tab>
      <v-tab :to="`/company/spaces`" value="spaces">Spaces</v-tab>
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
