<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Test Suites</h1>
        <test-suites-list-component />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import TestSuitesListComponent from "@/components/test-suites/testSuitesListComponent.vue";
</script>
