<template>
  <v-container fluid class="py-3">
    <v-row>
      <v-col v-for="stat in statsList" :key="stat.label" cols="4" md="2">
        <v-card variant="outlined">
          <v-card-text class="text-center py-3">
            <div class="text-h5 font-weight-bold" :class="stat.textClass">{{ stat.value }}</div>
            <div class="text-caption text-medium-emphasis">{{ stat.label }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  stats: { type: Object, default: () => ({}) }
})

const statsList = computed(() => [
  { label: 'Total', value: props.stats.total || 0, textClass: '' },
  { label: 'Passed', value: props.stats.passed || 0, textClass: 'text-success' },
  { label: 'Failed', value: props.stats.failed || 0, textClass: 'text-error' },
  { label: 'Blocked', value: props.stats.blocked || 0, textClass: 'text-warning' },
  { label: 'Skipped', value: props.stats.skipped || 0, textClass: 'text-grey' },
  { label: 'Not Run', value: props.stats.not_run || 0, textClass: '' },
])
</script>
