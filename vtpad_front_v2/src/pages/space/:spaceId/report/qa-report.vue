<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <report-qa-space-component />
  </v-container>
</template>

<script>

import ReportQaSpaceComponent from "@/components/reports/reportQaSpaceComponent.vue";

export default {
  name: "qa-reportPage",
  components: {ReportQaSpaceComponent},

}
</script>
<route>
{
meta: {
layout: "spacesReport",
tabValue: "qa-report"
}
}
</route>
<style  lang="scss">
.data-picker--compact{
  .v-picker-title{
    display: none;
  }
  .v-picker__header{
    display: none;
  }
}
</style>
