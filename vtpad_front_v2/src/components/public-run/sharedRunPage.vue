<template>
  <main class="shared-run-page">
    <v-container class="py-10" max-width="1000">
      <section aria-labelledby="shared-run-title">
        <div v-if="loading" class="text-center py-12" role="status" aria-live="polite">
          <v-progress-circular indeterminate color="primary" size="38" />
          <p class="mt-4 text-medium-emphasis">Loading shared run…</p>
        </div>

        <v-empty-state
          v-else-if="!available"
          icon="mdi-link-off"
          headline="Shared run unavailable"
          title="This link is unavailable"
          text="The link may have expired, been revoked, or is invalid."
        >
          <template v-if="retryable" #actions>
            <v-btn color="primary" variant="tonal" @click="redeemFromCurrentUrl">Retry</v-btn>
          </template>
        </v-empty-state>

        <template v-else>
          <header class="mb-6">
            <div class="text-overline text-medium-emphasis">Shared test run</div>
            <h1 id="shared-run-title" class="text-h4 font-weight-bold">{{ projection.run.name || 'Unnamed run' }}</h1>
            <v-chip class="mt-3 text-capitalize" :color="statusColor(projection.run.status)">
              {{ projection.run.status || 'Unknown status' }}
            </v-chip>
          </header>

          <div class="d-flex align-center justify-space-between mb-3">
            <h2 class="text-h6">Groups</h2>
            <span class="text-body-2 text-medium-emphasis">{{ totalCases }} cases · {{ formatDuration(totalDuration) }} known</span>
          </div>

          <v-alert v-if="!projection.groups.length" type="info" variant="tonal">
            This run does not contain any groups to show.
          </v-alert>

          <v-row v-else>
            <v-col v-for="(group, index) in projection.groups" :key="index" cols="12" md="6">
              <v-card variant="outlined" height="100%">
                <v-card-title class="text-subtitle-1 text-wrap">{{ group.name || 'Unassigned' }}</v-card-title>
                <v-card-subtitle>{{ group.case_count }} {{ group.case_count === 1 ? 'case' : 'cases' }}</v-card-subtitle>
                <v-card-text>
                  <div class="d-flex flex-wrap ga-2">
                    <v-chip
                      v-for="status in statuses"
                      :key="status.key"
                      size="small"
                      :color="status.color"
                      variant="tonal"
                      :aria-label="`${status.label}: ${group.status_counts[status.key]}`"
                    >{{ status.label }} {{ group.status_counts[status.key] }}</v-chip>
                  </div>
                  <div class="text-caption text-medium-emphasis mt-3">
                    Known duration: {{ formatDuration(group.duration_seconds) }}
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </template>
      </section>
    </v-container>
  </main>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { redeemSharedRun } from '@/services/publicRunService'

const statuses = [
  { key: 'not_run', label: 'Not run', color: 'grey' },
  { key: 'passed', label: 'Passed', color: 'success' },
  { key: 'failed', label: 'Failed', color: 'error' },
  { key: 'blocked', label: 'Blocked', color: 'warning' },
  { key: 'skipped', label: 'Skipped', color: 'info' }
]
const loading = ref(true)
const available = ref(false)
const retryable = ref(false)
const projection = ref({ run: { name: '', status: '' }, groups: [] })
const totalCases = computed(() => projection.value.groups.reduce((sum, group) => sum + group.case_count, 0))
const totalDuration = computed(() => {
  const durations = projection.value.groups.map((group) => group.duration_seconds).filter(Number.isFinite)
  return durations.length ? durations.reduce((sum, value) => sum + value, 0) : null
})

let redemptionToken = ''
let requestVersion = 0
let restoreDocumentMetadata = null

onMounted(async () => {
  // A fragment is not sent in HTTP requests. Remove it synchronously before
  // starting redemption so later navigation/referrer data cannot retain it.
  const token = readShareToken(window.location.hash)
  window.history.replaceState(window.history.state, document.title, window.location.pathname)
  redemptionToken = token
  restoreDocumentMetadata = setPrivacyMetadata()
  await redeem(token)
})

onUnmounted(() => {
  requestVersion += 1
  redemptionToken = ''
  restoreDocumentMetadata?.()
})

async function redeemFromCurrentUrl() {
  retryable.value = false
  await redeem(redemptionToken)
}

async function redeem(token) {
  const version = ++requestVersion
  loading.value = true
  available.value = false
  retryable.value = false
  projection.value = { run: { name: '', status: '' }, groups: [] }
  if (!token || import.meta.env.VITE_PUBLIC_RUN_LINKS_ENABLED !== 'true') {
    loading.value = false
    return
  }
  try {
    const response = await redeemSharedRun(token)
    if (version !== requestVersion) return
    projection.value = normalizeProjection(response)
    available.value = true
  } catch (error) {
    if (version !== requestVersion) return
    // Unknown, expired, and revoked links intentionally share one UI state.
    retryable.value = error?.status !== 404
  } finally {
    if (version === requestVersion) loading.value = false
  }
}

function readShareToken(hash) {
  if (!hash || hash.length < 2) return ''
  try {
    return decodeURIComponent(hash.slice(1))
  } catch {
    return ''
  }
}

function normalizeProjection(data) {
  const allowedStatuses = ['not_run', 'passed', 'failed', 'blocked', 'skipped']
  const groups = Array.isArray(data?.groups) ? data.groups : []
  return {
    run: {
      name: safeText(data?.run?.name),
      status: safeText(data?.run?.status)
    },
    groups: groups.map((group) => {
      const statusCounts = {}
      for (const status of allowedStatuses) statusCounts[status] = safeCount(group?.status_counts?.[status])
      return {
        name: safeText(group?.name),
        case_count: safeCount(group?.case_count),
        status_counts: statusCounts,
        duration_seconds: safeDuration(group?.duration_seconds)
      }
    })
  }
}

function safeText(value) {
  return typeof value === 'string' ? value.slice(0, 500) : ''
}

function safeCount(value) {
  const number = Number(value)
  return Number.isSafeInteger(number) && number >= 0 ? number : 0
}

function safeDuration(value) {
  if (value === null || value === undefined) return null
  const number = Number(value)
  return Number.isFinite(number) && number >= 0 ? number : null
}

function statusColor(status) {
  return { running: 'success', completed: 'primary', draft: 'grey', failed: 'error', paused: 'warning' }[status] || 'default'
}

function formatDuration(seconds) {
  if (!Number.isFinite(seconds)) return '—'
  const total = Math.max(0, Math.floor(seconds))
  const hours = Math.floor(total / 3600)
  const minutes = Math.floor((total % 3600) / 60)
  const remainder = total % 60
  return hours > 0
    ? `${hours}h ${String(minutes).padStart(2, '0')}m ${String(remainder).padStart(2, '0')}s`
    : `${minutes}m ${String(remainder).padStart(2, '0')}s`
}

function setPrivacyMetadata() {
  const originalTitle = document.title
  const restoreReferrer = setMeta('name', 'referrer', 'no-referrer')
  const restoreRobots = setMeta('name', 'robots', 'noindex, nofollow, noarchive')
  document.title = 'Shared test run'
  return () => {
    document.title = originalTitle
    restoreReferrer()
    restoreRobots()
  }
}

function setMeta(attribute, name, content) {
  let element = document.head.querySelector(`meta[${attribute}="${name}"]`)
  const created = !element
  const originalContent = element?.content
  if (!element) {
    element = document.createElement('meta')
    element.setAttribute(attribute, name)
    document.head.appendChild(element)
  }
  element.content = content
  return () => {
    if (created) element.remove()
    else element.content = originalContent
  }
}
</script>

<style scoped>
.shared-run-page {
  min-height: 100vh;
}
</style>
