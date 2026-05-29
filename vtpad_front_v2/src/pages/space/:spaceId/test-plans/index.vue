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
    <test-plans-list-component />
  </v-container>
</template>

<script setup>
import TestPlansListComponent from "@/components/test-plans/testPlansListComponent.vue";
</script>
