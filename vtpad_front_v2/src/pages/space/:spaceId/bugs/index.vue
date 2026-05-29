<route lang="json">
{
  "meta": {
    "layout": "spaces",
    "tabValue": "bugs"
  }
}
</route>

<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <bugs-list-component :spase-id-from="spaceId" />
  </v-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import BugsListComponent from '@/components/bugs/bugsListComponent.vue'

const route = useRoute()
const spaceId = computed(() => route.params.spaceId)
</script>

<style lang="scss">
</style>
