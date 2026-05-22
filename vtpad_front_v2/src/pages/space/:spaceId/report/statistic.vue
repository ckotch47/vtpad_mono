<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <statistic-page-component />
  </v-container>
</template>

<script>
import StatisticPageComponent from "@/components/reports/statisticPage/statisticPageComponent.vue";

export default {
  name: "statisticPage",
  components: {StatisticPageComponent}
}
</script>
<route>
{
meta: {
layout: "spacesReport",
tabValue: "statistic"
}
}
</route>
<style scoped>

</style>
