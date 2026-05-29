<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <api-token-list-component />
  </v-container>
</template>

<script setup>
import ApiTokenListComponent from '@/components/profile/apiTokenListComponent.vue'
</script>
<route>
{
  meta: {
    layout: "profile",
    tabValue: "api-tokens"
  }
}
</route>
