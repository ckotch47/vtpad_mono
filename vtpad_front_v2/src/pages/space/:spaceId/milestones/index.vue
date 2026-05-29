<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <milestone-list-component />
  </v-container>
</template>

<script setup>
import MilestoneListComponent from '@/components/milestones/milestoneListComponent.vue'
</script>
<route>
{
  meta: {
    layout: "spaces",
    tabValue: "milestones"
  }
}
</route>
