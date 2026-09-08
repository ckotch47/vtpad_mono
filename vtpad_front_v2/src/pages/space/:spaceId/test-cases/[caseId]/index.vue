<route>
{
  meta: {
    layout: "spaces",
    tabValue: "test-cases"
  }
}
</route>

<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <test-case-detail-component />
  </v-container>
</template>

<script setup>
import TestCaseDetailComponent from "@/components/test-cases/detail/testCaseDetailComponent.vue";
</script>
