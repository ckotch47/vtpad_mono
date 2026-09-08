<route>
{
  meta: {
    layout: "spaces",
    tabValue: "test-suites"
  }
}
</route>

<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <test-suite-detail-component />
  </v-container>
</template>

<script setup>
import TestSuiteDetailComponent from "@/components/test-suites/detail/testSuiteDetailComponent.vue";
</script>
