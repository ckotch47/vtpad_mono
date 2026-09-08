<route>
{
  meta: {
    layout: "spaces",
    tabValue: "test-runs"
  }
}
</route>

<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <test-run-detail-component />
  </v-container>
</template>

<script setup>
import TestRunDetailComponent from "@/components/test-runs/detail/testRunDetailComponent.vue";
</script>
