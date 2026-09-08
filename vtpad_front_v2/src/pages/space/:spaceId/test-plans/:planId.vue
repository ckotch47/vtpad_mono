<route>
{
  meta: {
    layout: "spaces",
    tabValue: "test-plans"
  }
}
</route>

<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <test-plan-detail-component />
  </v-container>
</template>

<script setup>
import TestPlanDetailComponent from "@/components/test-plans/detail/testPlanDetailComponent.vue";
</script>
