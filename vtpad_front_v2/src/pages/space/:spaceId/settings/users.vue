<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <settings-user-component />
  </v-container>
</template>

<script setup>
import SettingsUserComponent from '@/components/settings/settingsUserComponent.vue'
</script>
<route>
{
meta: {
layout: "spacesSettings",
tabValue: "users"
}
}
</route>
