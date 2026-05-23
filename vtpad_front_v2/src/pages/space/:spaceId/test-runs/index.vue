<route>
{
  meta: {
    layout: "spaces",
    tabValue: "test-runs"
  }
}
</route>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Test Runs</h1>
        <test-runs-list-component />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import TestRunsListComponent from "@/components/test-runs/testRunsListComponent.vue";
</script>
