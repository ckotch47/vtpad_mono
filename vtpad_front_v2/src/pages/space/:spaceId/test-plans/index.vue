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
    <v-row>
      <v-col cols="12">
        <page-header-component title="Test Plans" />
      </v-col>
    </v-row>
    <test-plans-list-component />
  </v-container>
</template>

<script setup>
import TestPlansListComponent from "@/components/test-plans/testPlansListComponent.vue";
import PageHeaderComponent from "@/components/common/pageHeaderComponent.vue";
</script>
