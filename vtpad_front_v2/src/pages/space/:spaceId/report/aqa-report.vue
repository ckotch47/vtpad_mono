<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <report-aqa-space-component />
  </v-container>
</template>

<script>
import ReportAqaSpaceComponent from "@/components/reports/reportTestSpaceComponent.vue";

export default {
  name: "test-reportPage",
  components: {ReportAqaSpaceComponent}
}
</script>
<route>
{
meta: {
layout: "spacesReport",
tabValue: "aqa-report"
}
}
</route>
<style scoped>

</style>
