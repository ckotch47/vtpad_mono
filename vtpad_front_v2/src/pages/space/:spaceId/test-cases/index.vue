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
    <v-row>
      <v-col cols="12">
        <page-header-component title="Test Cases" />
        <test-cases-list-component />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import TestCasesListComponent from "@/components/test-cases/testCasesListComponent.vue";
</script>
