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
    <v-row>
      <v-col cols="12">
        <page-header-component title="Test Runs" />
        <test-runs-list-component />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import TestRunsListComponent from "@/components/test-runs/testRunsListComponent.vue";
</script>
