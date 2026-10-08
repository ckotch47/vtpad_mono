<template>
  <v-container fluid class="run-summary py-3">
    <v-card variant="outlined" class="run-summary__overview">
      <v-card-text class="pa-4 pa-md-5">
        <div class="d-flex flex-wrap align-end justify-space-between ga-3 mb-3">
          <div>
            <div class="text-overline text-medium-emphasis">Run progress</div>
            <div class="d-flex align-baseline ga-2">
              <span class="text-h4 font-weight-bold">{{ completedCount }}</span>
              <span class="text-body-2 text-medium-emphasis">of {{ stats.total || 0 }} results complete</span>
            </div>
          </div>
          <div class="text-h5 font-weight-bold text-primary">{{ completionPercent }}%</div>
        </div>
        <v-progress-linear
          :model-value="completionPercent"
          color="primary"
          height="8"
          rounded
          :aria-label="`Run progress: ${completedCount} of ${stats.total || 0} results complete`"
        />
        <div class="run-summary__statuses mt-4" aria-label="Result status totals">
          <div v-for="status in statusList" :key="status.label" class="run-summary__status">
            <span class="run-summary__status-dot" :class="status.dotClass" aria-hidden="true" />
            <span class="text-body-2">{{ status.label }}</span>
            <span class="font-weight-bold ml-auto">{{ status.value }}</span>
          </div>
        </div>

        <v-divider class="my-4" />

        <div class="d-flex align-center ga-2 mb-3">
          <v-avatar color="primary" variant="tonal" size="30">
            <v-icon size="17">mdi-chart-timeline-variant</v-icon>
          </v-avatar>
          <div>
            <div class="text-subtitle-2 font-weight-bold">Time measurements</div>
            <div class="text-caption text-medium-emphasis">Case work and shared run timer</div>
          </div>
        </div>

        <div class="run-summary__measurement-grid">
          <section class="run-summary__measurement" aria-labelledby="case-time-heading">
            <div class="d-flex align-center justify-space-between ga-2 mb-2">
              <div id="case-time-heading" class="text-body-2 font-weight-medium">Case execution</div>
              <v-icon size="18" color="primary" aria-hidden="true">mdi-timer-outline</v-icon>
            </div>
            <div class="d-flex flex-wrap align-end justify-space-between ga-2">
              <div class="text-h5 font-weight-bold">{{ formatCaseDuration(stats.duration_seconds_total, stats.duration_measured_count) }}</div>
              <div class="text-caption text-medium-emphasis">{{ stats.duration_measured_count ?? 'No data' }} measured</div>
            </div>
            <div class="text-caption text-medium-emphasis mt-2">
              {{ stats.duration_unmeasured_count ?? 'No data' }} cases without recorded time
            </div>
          </section>

          <section class="run-summary__measurement" aria-labelledby="run-time-heading">
            <div class="d-flex align-center justify-space-between ga-2 mb-2">
              <div>
                <div id="run-time-heading" class="text-body-2 font-weight-medium">Run timer</div>
                <div class="text-caption text-medium-emphasis">Calendar time since run start</div>
              </div>
              <v-chip v-if="timer.state" size="small" :color="timerStateColor(timer.state)" variant="tonal" class="text-capitalize">
                {{ timerStateLabel(timer.state) }}
              </v-chip>
            </div>
            <div class="run-summary__timer-grid">
              <div>
                <div class="text-caption text-medium-emphasis">Calendar elapsed</div>
                <div class="text-subtitle-1 font-weight-bold">{{ formatDuration(timer.calendar_seconds) }}</div>
              </div>
              <div>
                <div class="text-caption text-medium-emphasis">Tracked active</div>
                <div class="text-subtitle-1 font-weight-bold text-success">{{ formatDuration(timer.active_seconds) }}</div>
              </div>
              <div>
                <div class="text-caption text-medium-emphasis">Tracked paused</div>
                <div class="text-subtitle-1 font-weight-bold text-warning">{{ formatDuration(timer.paused_seconds) }}</div>
              </div>
            </div>
            <div v-if="timer.state === 'untracked'" class="text-caption text-medium-emphasis mt-2">
              Calendar elapsed time is based on the run timestamps. Active and paused time were not tracked for this run.
            </div>
          </section>
        </div>
      </v-card-text>
    </v-card>
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

function formatCaseDuration(seconds, measuredCount) {
  if (!Number.isFinite(Number(measuredCount)) || Number(measuredCount) <= 0) return 'No data'
  return formatDuration(seconds)
}

const statusList = computed(() => [
  { label: 'Passed', value: props.stats.passed || 0, dotClass: 'run-summary__status-dot--passed' },
  { label: 'Failed', value: props.stats.failed || 0, dotClass: 'run-summary__status-dot--failed' },
  { label: 'Blocked', value: props.stats.blocked || 0, dotClass: 'run-summary__status-dot--blocked' },
  { label: 'Skipped', value: props.stats.skipped || 0, dotClass: 'run-summary__status-dot--skipped' },
  { label: 'Not run', value: props.stats.not_run || 0, dotClass: 'run-summary__status-dot--not-run' }
])

const completedCount = computed(() => statusList.value
  .filter((status) => status.label !== 'Not run')
  .reduce((total, status) => total + status.value, 0))

const completionPercent = computed(() => {
  const total = Number(props.stats.total) || 0
  if (total <= 0) return 0
  return Math.min(100, Math.round((completedCount.value / total) * 100))
})

function timerStateLabel(state) {
  return ({ running: 'Running', paused: 'Paused', completed: 'Completed', untracked: 'Untracked' })[state] || state
}

function timerStateColor(state) {
  return ({ running: 'success', paused: 'warning', completed: 'primary', untracked: 'info' })[state] || 'default'
}
</script>

<style scoped>
.run-summary__overview {
  border-radius: 14px;
}
.run-summary__statuses {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px 16px;
}
.run-summary__status {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 7px;
}
.run-summary__status-dot {
  width: 8px;
  height: 8px;
  flex: 0 0 auto;
  border-radius: 50%;
}
.run-summary__status-dot--passed { background: rgb(var(--v-theme-success)); }
.run-summary__status-dot--failed { background: rgb(var(--v-theme-error)); }
.run-summary__status-dot--blocked { background: rgb(var(--v-theme-warning)); }
.run-summary__status-dot--skipped { background: rgba(var(--v-theme-on-surface), 0.45); }
.run-summary__status-dot--not-run { background: rgb(var(--v-theme-primary)); }
.run-summary__measurement-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr);
}
.run-summary__measurement {
  min-width: 0;
  padding: 4px 20px 4px 0;
}
.run-summary__measurement + .run-summary__measurement {
  padding-right: 0;
  padding-left: 20px;
  border-left: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}
.run-summary__timer-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}
@media (max-width: 600px) {
  .run-summary__statuses {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .run-summary__timer-grid {
    gap: 8px;
  }
  .run-summary__measurement-grid {
    grid-template-columns: minmax(0, 1fr);
  }
  .run-summary__measurement,
  .run-summary__measurement + .run-summary__measurement {
    padding: 4px 0;
  }
  .run-summary__measurement + .run-summary__measurement {
    margin-top: 12px;
    padding-top: 16px;
    border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
    border-left: 0;
  }
}
</style>
