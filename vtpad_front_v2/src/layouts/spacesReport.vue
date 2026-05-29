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
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const spaceId = ref(route.params?.spaceId)
const tab = ref(route.meta?.tabValue)
</script>

<style scoped>
</style>
