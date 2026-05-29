<template>
  <v-breadcrumbs :items="items" class="pa-0 mb-2">
    <template #prepend>
      <v-icon size="small" icon="mdi-home" />
    </template>
    <template #divider>
      <v-icon icon="mdi-chevron-right" size="small" />
    </template>
  </v-breadcrumbs>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => []
  }
})
</script>
