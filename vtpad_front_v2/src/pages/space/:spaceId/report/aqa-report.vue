<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <report-aqa-space-component />
  </v-container>
</template>

<script setup>
import ReportAqaSpaceComponent from '@/components/reports/reportTestSpaceComponent.vue'
</script>
<route>
{
meta: {
layout: "spacesReport",
tabValue: "aqa-report"
}
}
</route>
