<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <environment-list-component />
  </v-container>
</template>

<script setup>
import EnvironmentListComponent from '@/components/environments/environmentListComponent.vue'
</script>
<route>
{
  meta: {
    layout: "spaces",
    tabValue: "environments"
  }
}
</route>
