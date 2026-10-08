<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>

  <div v-else>
    <v-container fluid class="pb-0">
      <breadcrumbs-component :items="breadcrumbItems" />
    </v-container>
    <v-toolbar density="compact">
      <v-btn icon @click="$router.back()">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <v-toolbar-title>{{ testcase.title }}</v-toolbar-title>
      <v-spacer />
      <v-chip size="small" :color="typeColor(testcase.type)" class="mr-2">{{ testcase.type }}</v-chip>
      <v-chip size="small" :color="priorityColor(testcase.priority)" class="mr-2">{{ priorityLabel(testcase.priority) }}</v-chip>
      <v-chip size="small" :color="statusColor(testcase.status)">{{ testcase.status }}</v-chip>
      <v-btn
        icon
        class="ml-2"
        :to="`/space/${spaceId}/test-cases/${caseId}/edit`"
      >
        <v-icon>mdi-pencil</v-icon>
      </v-btn>
    </v-toolbar>

    <v-container fluid>
      <v-tabs v-model="activeTab" class="mb-4">
        <v-tab value="details">Details</v-tab>
        <v-tab value="history">Run History</v-tab>
      </v-tabs>

      <v-window v-model="activeTab">
        <v-window-item value="details">
          <v-row>
            <v-col cols="12" md="8">
              <v-card v-if="testcase.text" class="mb-4">
                <v-card-title>Description</v-card-title>
                <v-card-text>
                  <editor-component
                    :text="testcase.text"
                    :edit="false"
                    accessible-label="Description"
                    :show-menu-bubble="false"
                    :show-menu-floating="false"
                    :show-menu-fixed="false"
                  />
                </v-card-text>
              </v-card>

              <template v-if="testcase.type === 'checklist'">
                <v-card class="mb-4">
                  <v-card-title class="d-flex align-center">
                    <v-icon class="mr-2" color="success">mdi-format-list-checks</v-icon>
                    Checks
                    <v-spacer />
                    <v-chip size="small" color="success">Checklist</v-chip>
                  </v-card-title>
                  <v-card-text>
                    <editor-component
                      v-if="testcase.steps"
                      :text="testcase.steps"
                      :edit="false"
                      accessible-label="Checks"
                      :show-menu-bubble="false"
                      :show-menu-floating="false"
                      :show-menu-fixed="false"
                    />
                    <div v-else class="text-medium-emphasis">No checks have been added yet.</div>
                    <div class="text-caption text-medium-emphasis mt-3">A run records one result for this checklist.</div>
                  </v-card-text>
                </v-card>
              </template>

              <template v-else>
                <v-card class="mb-4">
                  <v-card-title>Preconditions</v-card-title>
                  <v-card-text>
                    <editor-component
                      :text="testcase.preconditions || ''"
                      :edit="false"
                      accessible-label="Preconditions"
                      :show-menu-bubble="false"
                      :show-menu-floating="false"
                      :show-menu-fixed="false"
                    />
                  </v-card-text>
                </v-card>

                <v-card class="mb-4">
                  <v-card-title>Steps</v-card-title>
                  <v-card-text>
                    <editor-component
                      :text="testcase.steps || ''"
                      :edit="false"
                      accessible-label="Steps"
                      :show-menu-bubble="false"
                      :show-menu-floating="false"
                      :show-menu-fixed="false"
                    />
                  </v-card-text>
                </v-card>

                <v-card class="mb-4">
                  <v-card-title>Expected Results</v-card-title>
                  <v-card-text>
                    <editor-component
                      :text="testcase.expected_results || ''"
                      :edit="false"
                      accessible-label="Expected Results"
                      :show-menu-bubble="false"
                      :show-menu-floating="false"
                      :show-menu-fixed="false"
                    />
                  </v-card-text>
                </v-card>
              </template>
            </v-col>

            <v-col cols="12" md="4">
              <v-card>
                <v-card-title>Info</v-card-title>
                <v-card-text>
                  <v-list density="compact">
                    <v-list-item>
                      <v-list-item-title>ID</v-list-item-title>
                      <v-list-item-subtitle>{{ testcase.id }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Short Name</v-list-item-title>
                      <v-list-item-subtitle>{{ testcase.short_name || '-' }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Priority</v-list-item-title>
                      <v-list-item-subtitle>{{ priorityLabel(testcase.priority) }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Tags</v-list-item-title>
                      <v-list-item-subtitle>
                        <span v-if="!testcase.tags?.length">—</span>
                        <v-chip v-for="tag in testcase.tags || []" :key="tag" size="x-small" class="mr-1 mb-1" variant="tonal">{{ tag }}</v-chip>
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>External ID</v-list-item-title>
                      <v-list-item-subtitle>{{ testcase.external_id || '-' }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Link</v-list-item-title>
                      <v-list-item-subtitle>
                        <a v-if="testcase.link" :href="testcase.link" target="_blank">{{ testcase.link }}</a>
                        <span v-else>-</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Created</v-list-item-title>
                      <v-list-item-subtitle>{{ formatDate(testcase.created_at) }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Created by</v-list-item-title>
                      <v-list-item-subtitle>{{ testcase.created_by?.username || '—' }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Updated</v-list-item-title>
                      <v-list-item-subtitle>{{ formatDate(testcase.updated_at) }}</v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>

              <v-card class="mt-4">
                <v-card-title>Linked Tech Docs</v-card-title>
                <v-card-text>
                  <v-chip v-for="doc in techDocs" :key="doc.id" class="mr-1 mb-1" :to="`/space/${spaceId}/tech-docs?doc=${doc.id}`">{{ doc.title }}</v-chip>
                  <span v-if="!techDocs.length" class="text-medium-emphasis">No linked documentation</span>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <v-card class="mt-4">
            <v-card-title>Compare versions</v-card-title>
            <v-card-text>
              <div v-if="versions.length < 2" class="text-medium-emphasis">At least two saved versions are required for comparison.</div>
              <template v-else>
                <v-row>
                  <v-col cols="12" md="6">
                    <v-select
                      v-model="versionAId"
                      :items="versions"
                      item-title="version_number"
                      item-value="id"
                      label="Version A"
                      density="comfortable"
                      aria-label="Select first version to compare"
                    >
                      <template #item="{ props, item }">
                        <v-list-item v-bind="props" :subtitle="formatDate(item.raw.created_at)" />
                      </template>
                    </v-select>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-select
                      v-model="versionBId"
                      :items="versions"
                      item-title="version_number"
                      item-value="id"
                      label="Version B"
                      density="comfortable"
                      aria-label="Select second version to compare"
                    >
                      <template #item="{ props, item }">
                        <v-list-item v-bind="props" :subtitle="formatDate(item.raw.created_at)" />
                      </template>
                    </v-select>
                  </v-col>
                </v-row>

                <v-alert v-if="sameVersionsSelected" type="info" variant="tonal" density="compact" class="mb-3">
                  Select two different versions to compare.
                </v-alert>
                <v-alert v-else-if="versionA?.legacy || versionB?.legacy" type="info" variant="tonal" density="compact" class="mb-3">
                  Some older snapshots do not contain type, priority, or tag history. Those values are shown as unknown.
                </v-alert>

                <template v-if="versionA && versionB && !sameVersionsSelected">
                  <div class="version-columns text-caption text-medium-emphasis mb-2">
                    <span />
                    <span>v{{ versionA.version_number }} · {{ formatDate(versionA.created_at) }}</span>
                    <span>v{{ versionB.version_number }} · {{ formatDate(versionB.created_at) }}</span>
                  </div>
                  <v-table density="compact" class="version-comparison">
                    <thead>
                      <tr>
                        <th scope="col">Field</th>
                        <th scope="col">Version {{ versionA.version_number }}</th>
                        <th scope="col">Version {{ versionB.version_number }}</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="row in versionComparisonRows" :key="row.key">
                        <th scope="row">
                          {{ row.label }}
                          <span class="text-caption d-block">{{ row.changed ? 'Changed' : 'Unchanged' }}</span>
                        </th>
                        <td :class="{ 'version-changed': row.changed }">
                          <template v-if="row.rich">
                            <div class="version-rich" v-html="row.a" />
                          </template>
                          <template v-else>{{ row.a }}</template>
                        </td>
                        <td :class="{ 'version-changed': row.changed }">
                          <template v-if="row.rich">
                            <div class="version-rich" v-html="row.b" />
                          </template>
                          <template v-else>{{ row.b }}</template>
                        </td>
                      </tr>
                      <tr v-for="step in stepComparisonRows" :key="`step-${step.index}`">
                        <th scope="row">Step {{ step.index + 1 }}<span class="text-caption d-block">{{ step.change }}</span></th>
                        <td :class="{ 'version-changed': step.change !== 'Unchanged' }">
                          <div class="version-rich" v-html="step.a || '—'" />
                        </td>
                        <td :class="{ 'version-changed': step.change !== 'Unchanged' }">
                          <div class="version-rich" v-html="step.b || '—'" />
                        </td>
                      </tr>
                    </tbody>
                  </v-table>
                  <div class="d-flex justify-end mt-3">
                    <v-btn color="primary" variant="tonal" :loading="restoringVersion" @click="restoreVersionB">
                      Restore v{{ versionB.version_number }} as new version
                    </v-btn>
                  </div>
                </template>
              </template>
            </v-card-text>
          </v-card>
        </v-window-item>

        <v-window-item value="history">
          <v-card>
            <v-card-title>Run History</v-card-title>
            <v-card-text>
              <v-data-table-server
                v-model:items-per-page="historyPageSize"
                :headers="historyHeaders"
                :items="runHistory"
                :items-length="historyTotal"
                :loading="historyLoading"
                item-value="id"
                @update:options="loadRunHistory"
              >
                <template v-slot:[`item.status`]="{ item }">
                  <v-chip size="small" :color="resultStatusColor(item.status)">{{ item.status }}</v-chip>
                </template>
                <template v-slot:[`item.run_name`]="{ item }">
                  <router-link :to="`/space/${spaceId}/test-runs/${item.run_id}`">
                    {{ item.run_name }}
                  </router-link>
                </template>
                <template v-slot:[`item.executed_at`]="{ item }">
                  {{ formatDate(item.executed_at) }}
                </template>
                <template v-slot:[`item.duration_seconds`]="{ item }">
                  {{ formatDuration(item.duration_seconds) }}
                </template>
                <template v-slot:[`item.run_timer.calendar_seconds`]="{ item }">
                  {{ formatDuration(item.run_timer?.calendar_seconds) }}
                </template>
                <template v-slot:[`item.run_timer.active_seconds`]="{ item }">
                  {{ formatDuration(item.run_timer?.active_seconds) }}
                </template>
                <template v-slot:[`item.run_timer.paused_seconds`]="{ item }">
                  {{ formatDuration(item.run_timer?.paused_seconds) }}
                </template>
              </v-data-table-server>
            </v-card-text>
          </v-card>
        </v-window-item>
      </v-window>
    </v-container>

  </div>
</template>

<script setup>
import {ref, computed, onMounted} from 'vue'
import { useLogger } from '@/composables/useLogger'
import { useRoute } from 'vue-router'
import { useApi } from '@/composables/useApi'
import EditorComponent from '@/components/common/editor/editorComponent.vue'
import BreadcrumbsComponent from '@/components/common/breadcrumbsComponent.vue'
import { testCaseService } from '@/services'
import { sanitizeHtml } from '@/utils/sanitize'

const log = useLogger('app')
const route = useRoute()
const api = useApi()

const spaceId = computed(() => route.params.spaceId)
const caseId = route.params.caseId

const loader = ref(true)
const testcase = ref({})
const versions = ref([])
const activeTab = ref('details')
const runHistory = ref([])
const historyTotal = ref(0)
const historyPageSize = ref(25)
const historyLoading = ref(false)
const breadcrumbItems = ref([])
const techDocs = ref([])
const versionAId = ref(null)
const versionBId = ref(null)
const restoringVersion = ref(false)

const versionA = computed(() => versions.value.find((version) => version.id === versionAId.value) || null)
const versionB = computed(() => versions.value.find((version) => version.id === versionBId.value) || null)
const sameVersionsSelected = computed(() => Boolean(versionAId.value && versionAId.value === versionBId.value))

const versionComparisonRows = computed(() => {
  if (!versionA.value || !versionB.value || sameVersionsSelected.value) return []
  const textRows = [
    { key: 'title', label: 'Title', a: versionA.value.title, b: versionB.value.title },
    { key: 'type', label: 'Type', a: legacyValue(versionA.value.type), b: legacyValue(versionB.value.type) },
    { key: 'priority', label: 'Priority', a: legacyValue(versionA.value.priority), b: legacyValue(versionB.value.priority) },
    { key: 'tags', label: 'Tags', a: formatTags(versionA.value.tags), b: formatTags(versionB.value.tags) }
  ]
  const richRows = [
    { key: 'description', label: 'Description', field: 'text' },
    { key: 'preconditions', label: 'Preconditions', field: 'preconditions' },
    { key: 'expected-results', label: 'Expected results', field: 'expected_results' }
  ].map((row) => {
    const a = sanitizeHtml(versionA.value[row.field] || '')
    const b = sanitizeHtml(versionB.value[row.field] || '')
    return { ...row, a: a || '—', b: b || '—', rich: true, changed: a !== b }
  })
  return [
    ...textRows.map((row) => ({ ...row, changed: row.a !== row.b })),
    ...richRows
  ]
})

const stepComparisonRows = computed(() => {
  if (!versionA.value || !versionB.value || sameVersionsSelected.value) return []
  const stepsA = extractSteps(versionA.value.steps)
  const stepsB = extractSteps(versionB.value.steps)
  return alignSteps(stepsA, stepsB)
})

const historyHeaders = computed(() => [
  { title: 'Run', key: 'run_name', sortable: false },
  { title: 'Status', key: 'status', sortable: false },
  { title: 'Case duration', key: 'duration_seconds', sortable: false },
  { title: 'Run calendar time', key: 'run_timer.calendar_seconds', sortable: false },
  { title: 'Run active time', key: 'run_timer.active_seconds', sortable: false },
  { title: 'Run paused time', key: 'run_timer.paused_seconds', sortable: false },
  { title: 'Comment', key: 'comment', sortable: false },
  { title: 'Executed', key: 'executed_at', sortable: false }
])

function loadCase() {
  api.get(`/api/v2/test-case/${caseId}`).then(res => {
    testcase.value = res.data
    versions.value = res.data.versions || []
    versionAId.value = versions.value[0]?.id || null
    versionBId.value = versions.value[1]?.id || versions.value[0]?.id || null
    breadcrumbItems.value = [
      { title: 'Test Cases', to: `/space/${spaceId.value}/test-cases` },
      { title: res.data.title }
    ]
    loader.value = false
  }).catch(() => { loader.value = false })
  testCaseService.getTechDocs(caseId).then((res) => { techDocs.value = res.data.items || res.data || [] }).catch(() => { techDocs.value = [] })
}

function legacyValue(value) {
  return value === null || value === undefined ? 'Unknown (legacy snapshot)' : value
}

function formatTags(tags) {
  if (tags === null || tags === undefined) return 'Unknown (legacy snapshot)'
  return tags.length ? [...tags].sort((a, b) => a.localeCompare(b)).join(', ') : 'No tags'
}

function extractSteps(value) {
  const sanitized = sanitizeHtml(value || '')
  if (!sanitized) return []
  const document = new DOMParser().parseFromString(sanitized, 'text/html')
  const topLevelLists = [...document.querySelectorAll('ol, ul')].filter((list) => !list.parentElement?.closest('li'))
  const listItems = topLevelLists.flatMap((list) => [...list.children].filter((child) => child.tagName === 'LI'))
  if (listItems.length) return listItems.map((item) => sanitizeHtml(item.innerHTML).trim()).filter(Boolean)
  const blockItems = [...document.body.children]
  if (blockItems.length > 1) return blockItems.map((item) => sanitizeHtml(item.innerHTML).trim()).filter(Boolean)
  const text = document.body.textContent || ''
  return text.split(/\r?\n/).map((line) => line.trim()).filter(Boolean).map((line) => sanitizeHtml(line))
}

function alignSteps(stepsA, stepsB) {
  const lengths = Array.from({ length: stepsA.length + 1 }, () => Array(stepsB.length + 1).fill(0))
  for (let a = stepsA.length - 1; a >= 0; a -= 1) {
    for (let b = stepsB.length - 1; b >= 0; b -= 1) {
      lengths[a][b] = stepsA[a] === stepsB[b]
        ? lengths[a + 1][b + 1] + 1
        : Math.max(lengths[a + 1][b], lengths[a][b + 1])
    }
  }

  const rows = []
  let a = 0
  let b = 0
  while (a < stepsA.length || b < stepsB.length) {
    if (a < stepsA.length && b < stepsB.length && stepsA[a] === stepsB[b]) {
      rows.push({ a: stepsA[a], b: stepsB[b], change: 'Unchanged' })
      a += 1
      b += 1
    } else if (b < stepsB.length && (a === stepsA.length || lengths[a][b + 1] >= lengths[a + 1][b])) {
      rows.push({ a: '', b: stepsB[b], change: 'Added' })
      b += 1
    } else {
      rows.push({ a: stepsA[a], b: '', change: 'Removed' })
      a += 1
    }
  }
  return rows.map((row, index) => ({ ...row, index }))
}

async function restoreVersionB() {
  if (!versionB.value || !confirm(`Restore version ${versionB.value.version_number} as a new version?`)) return
  restoringVersion.value = true
  try { await testCaseService.restoreVersion(caseId, versionB.value.id); loadCase() } catch (error) { log.error('failed to restore test case version', error) } finally { restoringVersion.value = false }
}

async function loadRunHistory({ page, itemsPerPage }) {
  historyLoading.value = true
  try {
    const res = await api.get(`/api/v2/test-case/${caseId}/runs`, {
      params: { page, page_size: itemsPerPage }
    })
    runHistory.value = res.data.items
    historyTotal.value = res.data.total
  } catch (e) {
    log.error("request failed", e)
  } finally {
    historyLoading.value = false
  }
}

function typeColor(type) {
  const map = { manual: 'primary', checklist: 'warning', automated: 'success' }
  return map[type] || 'grey'
}

function statusColor(status) {
  const map = { active: 'success', draft: 'grey', deprecated: 'error' }
  return map[status] || 'grey'
}

function priorityLabel(priority) {
  const labels = { P0: 'P0 · Blocker', P1: 'P1 · High', P2: 'P2 · Normal', P3: 'P3 · Low' }
  return labels[priority] || labels.P2
}

function priorityColor(priority) {
  return ({ P0: 'error', P1: 'warning', P2: 'primary', P3: 'grey' })[priority] || 'primary'
}

function resultStatusColor(status) {
  const map = { passed: 'success', failed: 'error', blocked: 'warning', skipped: 'grey', not_run: 'grey' }
  return map[status] || 'grey'
}

function formatDate(date) {
  return date ? new Date(date).toLocaleDateString() : ''
}

function formatDuration(seconds) {
  if (seconds === null || seconds === undefined) return 'No data'
  const total = Math.max(0, Math.floor(seconds))
  const hours = Math.floor(total / 3600)
  const minutes = Math.floor((total % 3600) / 60)
  const remainder = total % 60
  return hours > 0
    ? `${hours}h ${String(minutes).padStart(2, '0')}m ${String(remainder).padStart(2, '0')}s`
    : `${minutes}m ${String(remainder).padStart(2, '0')}s`
}

onMounted(() => {
  loadCase()
})
</script>

<style scoped>
.version-columns { display: grid; grid-template-columns: 10rem repeat(2, minmax(0, 1fr)); gap: 1rem; }
.version-comparison th { width: 10rem; min-width: 10rem; text-align: left; vertical-align: top; font-weight: 600; }
.version-comparison td { width: 50%; vertical-align: top; overflow-wrap: anywhere; }
.version-comparison .version-changed { background: rgba(var(--v-theme-warning), .12); }
.version-rich { min-height: 1rem; white-space: normal; overflow-wrap: anywhere; }
.version-rich :deep(p:first-child) { margin-top: 0; }
.version-rich :deep(p:last-child) { margin-bottom: 0; }
</style>
