<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <profile-main-component />
  </v-container>
</template>

<script setup>
import ProfileMainComponent from '@/components/profile/profileMainComponent.vue'
</script>
<route>
{
  meta: {
    layout: "profile",
    tabValue: "profile"
  }
}
</route>
