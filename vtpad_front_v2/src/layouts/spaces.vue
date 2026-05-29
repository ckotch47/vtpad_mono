<template>
  <v-app>
    <v-tabs
      fixed-tabs
      align-tabs="start"
      color="primary"
      v-model="tab"
      class="rounded-0_custom"
    >
      <v-tab :to="`/space/${spaceId}/dashboard`" value="dashboard">Dashboard</v-tab>
      <v-tab :to="`/space/${spaceId}/test-suites`" value="test-suites">Test Suites</v-tab>
      <v-tab :to="`/space/${spaceId}/test-cases`" value="test-cases">Test Cases</v-tab>
      <v-tab :to="`/space/${spaceId}/test-runs`" value="test-runs">Test Runs</v-tab>
      <v-tab :to="`/space/${spaceId}/test-plans`" value="test-plans">Test Plans</v-tab>
      <v-tab :to="`/space/${spaceId}/tech-docs`" value="tech-docs">Tech Docs</v-tab>
      <v-tab :to="`/space/${spaceId}/bugs`" value="bugs">Bugs</v-tab>
    </v-tabs>

    <router-view :key="route.params.spaceId" />
  </v-app>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const spaceId = ref(route.params?.spaceId)
const tab = ref(route.meta?.tabValue)

watch(() => route.params?.spaceId, (val) => { spaceId.value = val })
watch(() => route.meta?.tabValue, (val) => { tab.value = val })
</script>

<style scoped>
.rounded-0_custom :deep(.v-tab) {
  text-transform: none;
}
</style>
