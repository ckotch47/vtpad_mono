<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <statistic-page-component />
  </v-container>
</template>

<script setup>
import StatisticPageComponent from '@/components/reports/statisticPage/statisticPageComponent.vue'
</script>
<route>
{
meta: {
layout: "spacesReport",
tabValue: "statistic"
}
}
</route>
