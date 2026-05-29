<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <custom-field-list-component />
  </v-container>
</template>

<script setup>
import CustomFieldListComponent from '@/components/settings/customFieldListComponent.vue'
</script>
<route>
{
  meta: {
    layout: "spacesSettings",
    tabValue: "custom-fields"
  }
}
</route>
