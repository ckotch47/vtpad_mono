<template>
  <v-app>
    <v-tabs
      fixed-tabs
      align-tabs="start"
      color="primary"
      v-model="tab"
      class="rounded-0_custom"
    >
      <v-tab :to="`/space/${spaceId}/report/statistic`" value="statistic">Statistic</v-tab>
      <v-tab :to="`/space/${spaceId}/report/qa-report`" value="qa-report">QA</v-tab>
      <v-tab :to="`/space/${spaceId}/report/aqa-report`" value="aqa-report">AQA</v-tab>
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

watch(() => route.params?.spaceId, (val) => {
  spaceId.value = val
})
watch(() => route.meta?.tabValue, (val) => {
  tab.value = val
})
</script>

<style scoped>
.rounded-0_custom :deep(.v-tab) {
  text-transform: none;
}
</style>
