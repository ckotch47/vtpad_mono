<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <settings-main-component />
  </v-container>
</template>

<script setup>
import SettingsMainComponent from '@/components/settings/settingsMainComponent.vue'
</script>
<route>
  {
  meta: {
    layout: "spacesSettings",
    tabValue: "index"
  }
}
</route>
