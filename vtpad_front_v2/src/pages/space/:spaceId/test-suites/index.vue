<route>
{
  meta: {
    layout: "spaces",
    tabValue: "test-suites"
  }
}
</route>

<template>
  <test-suites-workspace-component />
</template>

<script setup>
import TestSuitesWorkspaceComponent from "@/components/test-suites/testSuitesWorkspaceComponent.vue";

defineOptions({ name: "TestSuitesIndexPage" });
</script>
