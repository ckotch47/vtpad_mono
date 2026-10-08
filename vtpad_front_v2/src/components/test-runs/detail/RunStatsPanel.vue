<template>
  <v-container fluid class="py-3">
    <v-row>
      <v-col v-for="stat in statsList" :key="stat.label" cols="6" sm="4" md="2">
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
  stats: { type: Object, default: () => ({}) },
  timer: { type: Object, default: () => ({}) }
})

function formatDuration(seconds) {
  if (seconds === null || seconds === undefined) return 'No data'
  const total = Math.max(0, Math.floor(seconds))
  const hours = Math.floor(total / 3600)
  const minutes = Math.floor((total % 3600) / 60)
  const remainder = total % 60
  return hours > 0
    ? `${hours}h ${String(minutes).padStart(2, '0')}m`
    : `${minutes}m ${String(remainder).padStart(2, '0')}s`
}

const statsList = computed(() => [
  { label: 'Total', value: props.stats.total || 0, textClass: '' },
  { label: 'Passed', value: props.stats.passed || 0, textClass: 'text-success' },
  { label: 'Failed', value: props.stats.failed || 0, textClass: 'text-error' },
  { label: 'Blocked', value: props.stats.blocked || 0, textClass: 'text-warning' },
  { label: 'Skipped', value: props.stats.skipped || 0, textClass: 'text-grey' },
  { label: 'Not Run', value: props.stats.not_run || 0, textClass: '' },
  { label: 'Measured case time', value: formatDuration(props.stats.duration_seconds_total), textClass: '' },
  { label: 'Cases with time', value: props.stats.duration_measured_count ?? 'No data', textClass: 'text-medium-emphasis' },
  { label: 'Cases without time', value: props.stats.duration_unmeasured_count ?? 'No data', textClass: 'text-medium-emphasis' },
  { label: 'Run calendar time', value: formatDuration(props.timer.calendar_seconds), textClass: '' },
  { label: 'Run active time', value: formatDuration(props.timer.active_seconds), textClass: 'text-success' },
  { label: 'Run paused time', value: formatDuration(props.timer.paused_seconds), textClass: 'text-warning' },
])
</script>
