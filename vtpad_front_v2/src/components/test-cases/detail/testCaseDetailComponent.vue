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
                <v-card-title>Versions</v-card-title>
                <v-card-text>
                  <v-list density="compact">
                    <v-list-item v-for="ver in versions" :key="ver.id" :active="selectedVersion?.id === ver.id" @click="selectVersion(ver)">
                      <v-list-item-title>v{{ ver.version_number }}</v-list-item-title>
                      <v-list-item-subtitle>{{ formatDate(ver.created_at) }}</v-list-item-subtitle>
                      <template #append><v-btn icon="mdi-compare" size="x-small" variant="text" @click.stop="selectVersion(ver)" /></template>
                    </v-list-item>
                    <v-list-item v-if="!versions.length" title="No saved versions" />
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

    <v-dialog v-model="versionDialog" max-width="900">
      <v-card v-if="selectedVersion">
        <v-card-title class="d-flex align-center">Version {{ selectedVersion.version_number }}<v-spacer /><v-btn color="primary" :loading="restoringVersion" @click="restoreSelectedVersion">Restore as new version</v-btn></v-card-title>
        <v-card-text>
          <v-alert v-if="selectedVersion.legacy" type="info" variant="tonal" density="compact" class="mb-3">This historical record does not contain a complete snapshot.</v-alert>
          <v-row>
            <v-col cols="12" md="6"><div class="text-subtitle-2 mb-2">Current</div><pre class="version-diff">{{ comparableCase(testcase) }}</pre></v-col>
            <v-col cols="12" md="6"><div class="text-subtitle-2 mb-2">Selected version</div><pre class="version-diff">{{ comparableCase(selectedVersion) }}</pre></v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-dialog>
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
const selectedVersion = ref(null)
const versionDialog = ref(false)
const restoringVersion = ref(false)

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
    breadcrumbItems.value = [
      { title: 'Test Cases', to: `/space/${spaceId.value}/test-cases` },
      { title: res.data.title }
    ]
    loader.value = false
  }).catch(() => { loader.value = false })
  testCaseService.getTechDocs(caseId).then((res) => { techDocs.value = res.data.items || res.data || [] }).catch(() => { techDocs.value = [] })
}

async function selectVersion(version) {
  selectedVersion.value = version
  versionDialog.value = true
  try {
    const response = await testCaseService.getVersion(caseId, version.id)
    selectedVersion.value = { ...version, ...(response.data || {}) }
  } catch (_) { /* list response is still useful on older deployments */ }
}

function comparableCase(value) {
  const fields = ['title', 'preconditions', 'steps', 'expected_results', 'text']
  return fields.map((field) => `${field}: ${value?.[field] || '—'}`).join('\n\n')
}

async function restoreSelectedVersion() {
  if (!selectedVersion.value || !confirm(`Restore version ${selectedVersion.value.version_number} as a new version?`)) return
  restoringVersion.value = true
  try { await testCaseService.restoreVersion(caseId, selectedVersion.value.id); versionDialog.value = false; loadCase() } catch (error) { log.error('failed to restore test case version', error) } finally { restoringVersion.value = false }
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
.version-diff { white-space: pre-wrap; overflow-wrap: anywhere; font-family: inherit; font-size: .8rem; }
</style>
