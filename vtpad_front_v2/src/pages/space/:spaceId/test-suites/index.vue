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
    <v-row>
      <v-col cols="12">
        <page-header-component title="Test Suites" />
        <test-suites-list-component />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import TestSuitesListComponent from "@/components/test-suites/testSuitesListComponent.vue";
</script>
