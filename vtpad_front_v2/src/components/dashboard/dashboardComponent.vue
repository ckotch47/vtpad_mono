<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>

  <v-container v-else-if="dashboardError" class="mx-auto custom-container max-width-1500 py-10">
    <contextual-empty-state
      icon="mdi-chart-box-outline"
      :title="dashboardErrorStatus === 403 ? 'You do not have access to this dashboard' : 'Analytics could not be loaded'"
      :text="dashboardErrorStatus === 403 ? 'Ask a space administrator to grant access.' : 'Check your connection and try again.'"
      :action-label="dashboardErrorStatus === 403 ? '' : 'Retry'"
      action-icon="mdi-refresh"
      @action="retryDashboard"
    />
  </v-container>

  <div v-else>
    <v-container class="mx-auto custom-container max-width-1500 pb-0">
      <page-header-component title="Dashboard" />
    </v-container>

    <v-container v-if="!dashboardHasData" class="mx-auto custom-container max-width-1500">
      <contextual-empty-state
        icon="mdi-chart-box-outline"
        title="No analytics data yet"
        text="Dashboard metrics will appear after test cases and runs are added to this space."
      />
    </v-container>

    <!-- Stats Cards -->
    <v-container class="mx-auto custom-container max-width-1500">
      <v-row>
        <v-col cols="6" md="3">
          <v-card variant="outlined">
            <v-card-text class="d-flex align-center py-3">
              <v-icon size="32" color="primary" class="mr-3">mdi-test-tube</v-icon>
              <div>
                <div class="text-h6 font-weight-bold">{{ stats.cases.total }}</div>
                <div class="text-caption text-medium-emphasis">Total Cases</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="6" md="3">
          <v-card variant="outlined">
            <v-card-text class="d-flex align-center py-3">
              <v-icon size="32" color="info" class="mr-3">mdi-folder-open-outline</v-icon>
              <div>
                <div class="text-h6 font-weight-bold">{{ stats.suites }}</div>
                <div class="text-caption text-medium-emphasis">Suites</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="6" md="3">
          <v-card variant="outlined">
            <v-card-text class="d-flex align-center py-3">
              <v-icon size="32" color="success" class="mr-3">mdi-play-circle-outline</v-icon>
              <div>
                <div class="text-h6 font-weight-bold">{{ stats.runs.total }}</div>
                <div class="text-caption text-medium-emphasis">Total Runs</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="6" md="3">
          <v-card variant="outlined">
            <v-card-text class="d-flex align-center py-3">
              <v-icon size="32" color="warning" class="mr-3">mdi-run-fast</v-icon>
              <div>
                <div class="text-h6 font-weight-bold">{{ stats.runs.active }}</div>
                <div class="text-caption text-medium-emphasis">Active Runs</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Case Type Breakdown -->
      <v-row class="mt-2">
        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>Case Types</v-card-title>
            <v-card-text>
              <v-list density="compact">
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="info">mdi-hand-back-right-outline</v-icon>
                  </template>
                  <v-list-item-title>Manual</v-list-item-title>
                  <template v-slot:append>
                    <v-chip size="small" color="info">{{ stats.cases.manual }}</v-chip>
                  </template>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="success">mdi-check-box-outline</v-icon>
                  </template>
                  <v-list-item-title>Checklist</v-list-item-title>
                  <template v-slot:append>
                    <v-chip size="small" color="success">{{ stats.cases.checklist }}</v-chip>
                  </template>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="warning">mdi-robot</v-icon>
                  </template>
                  <v-list-item-title>Automated</v-list-item-title>
                  <template v-slot:append>
                    <v-chip size="small" color="warning">{{ stats.cases.automated }}</v-chip>
                  </template>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>Latest Results</v-card-title>
            <v-card-text>
              <v-list density="compact">
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="success">mdi-check-circle</v-icon>
                  </template>
                  <v-list-item-title>Passed</v-list-item-title>
                  <template v-slot:append>
                    <v-chip size="small" color="success">{{ stats.latest_results.passed }}</v-chip>
                  </template>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="error">mdi-close-circle</v-icon>
                  </template>
                  <v-list-item-title>Failed</v-list-item-title>
                  <template v-slot:append>
                    <v-chip size="small" color="error">{{ stats.latest_results.failed }}</v-chip>
                  </template>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="warning">mdi-minus-circle</v-icon>
                  </template>
                  <v-list-item-title>Blocked</v-list-item-title>
                  <template v-slot:append>
                    <v-chip size="small" color="warning">{{ stats.latest_results.blocked }}</v-chip>
                  </template>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="grey">mdi-alert-circle-outline</v-icon>
                  </template>
                  <v-list-item-title>Skipped</v-list-item-title>
                  <template v-slot:append>
                    <v-chip size="small" color="grey">{{ stats.latest_results.skipped }}</v-chip>
                  </template>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>Top Failed Cases</v-card-title>
            <v-card-text>
              <v-list density="compact" v-if="topFailed.length">
                <v-list-item
                  v-for="tc in topFailed"
                  :key="tc.id"
                  :to="`/space/${spaceId}/test-cases/${tc.id}`"
                >
                  <v-list-item-title class="text-truncate" style="max-width: 220px">
                    {{ tc.title }}
                  </v-list-item-title>
                  <template v-slot:append>
                    <v-chip size="x-small" color="error">{{ tc.fail_count }} fails</v-chip>
                  </template>
                </v-list-item>
              </v-list>
              <v-empty-state
                v-else
                icon="mdi-check-circle"
                text="No failed cases recently"
              />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Trend Chart -->
      <v-row class="mt-2">
        <v-col cols="12">
          <v-card>
            <v-card-title>Run Trend (Last 30 Days)</v-card-title>
            <v-card-text>
              <v-table v-if="trend.length">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Run</th>
                    <th>Total</th>
                    <th class="text-success">Passed</th>
                    <th class="text-error">Failed</th>
                    <th class="text-warning">Blocked</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in trend" :key="row.run_id">
                    <td>{{ row.date }}</td>
                    <td>
                      <router-link :to="`/space/${spaceId}/test-runs/${row.run_id}`">
                        {{ row.run_name }}
                      </router-link>
                    </td>
                    <td>{{ row.total }}</td>
                    <td class="text-success">{{ row.passed }}</td>
                    <td class="text-error">{{ row.failed }}</td>
                    <td class="text-warning">{{ row.blocked }}</td>
                  </tr>
                </tbody>
              </v-table>
              <v-empty-state
                v-else
                icon="mdi-chart-line"
                text="No completed runs in the last 30 days"
              />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <v-container class="mx-auto custom-container max-width-1500 pt-0">
      <v-card variant="outlined" class="linked-defects-card">
        <v-card-item>
          <template #prepend>
            <v-avatar color="error" variant="tonal" rounded="lg">
              <v-icon>mdi-bug-outline</v-icon>
            </v-avatar>
          </template>
          <v-card-title>Linked defects</v-card-title>
          <v-card-subtitle>
            Analytics includes bugs explicitly linked to run results by UUID. Legacy text links are not included.
          </v-card-subtitle>
          <template #append>
            <v-btn
              variant="text"
              prepend-icon="mdi-open-in-new"
              :to="`/space/${spaceId}/bugs`"
              aria-label="Open bugs list"
            >
              Bugs
            </v-btn>
          </template>
        </v-card-item>

        <v-divider />

        <v-card-text>
          <v-alert
            v-if="linkedDefects.error"
            type="error"
            variant="tonal"
            class="mb-4"
            role="alert"
          >
            <div class="d-flex flex-wrap align-center justify-space-between ga-3">
              <span>Linked defect analytics could not be loaded. Your existing dashboard data is still available.</span>
              <v-btn variant="outlined" color="error" @click="retryLinkedDefects">Retry</v-btn>
            </div>
          </v-alert>

          <div v-if="linkedDefects.loading && !linkedDefects.summary" aria-live="polite" aria-busy="true">
            <v-skeleton-loader type="article, table" />
          </div>

          <template v-else-if="linkedDefects.summary">
            <v-row class="mb-1" role="region" aria-label="Linked defect summary">
              <v-col v-for="metric in defectMetrics" :key="metric.key || metric.status" cols="6" sm="4" lg="2">
                <v-card class="defect-metric" variant="tonal" :color="metric.color">
                  <v-card-text class="py-3">
                    <div class="text-h5 font-weight-bold">
                      {{ metric.status ? linkedDefects.summary.statuses?.[metric.status] ?? 0 : linkedDefects.summary[metric.key] ?? 0 }}
                    </div>
                    <div class="text-caption text-medium-emphasis">{{ metric.label }}</div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>

            <v-tabs v-model="defectView" color="primary" show-arrows aria-label="Linked defect views">
              <v-tab value="list">Defect list</v-tab>
              <v-tab value="run">By run</v-tab>
              <v-tab value="suite">By suite</v-tab>
            </v-tabs>

            <v-tabs-window v-model="defectView">
              <v-tabs-window-item value="list">
                <div class="d-flex flex-wrap align-center ga-3 py-4">
                  <v-select
                    v-model="defectStatus"
                    :items="statusOptions"
                    item-title="title"
                    item-value="value"
                    label="Filter by status"
                    clearable
                    hide-details
                    density="compact"
                    variant="outlined"
                    class="defect-status-filter"
                    aria-label="Filter linked bugs by status"
                  />
                  <v-chip v-if="linkedDefects.loading" size="small" color="primary" variant="tonal" aria-live="polite">
                    Updating…
                  </v-chip>
                  <v-spacer />
                  <span class="text-body-2 text-medium-emphasis" aria-live="polite">
                    {{ linkedDefects.total }} linked bugs
                  </span>
                </div>

                <v-alert v-if="!linkedDefects.error && !linkedDefects.loading && linkedDefects.items.length === 0" type="info" variant="tonal">
                  <template v-if="defectStatus">No linked bugs match the selected status. This report includes UUID links only, not legacy text links.</template>
                  <template v-else>No UUID-linked bugs yet. Links stored only as legacy text are not included in this report.</template>
                </v-alert>

                <v-table v-else-if="linkedDefects.items.length" density="comfortable" class="defect-table">
                  <thead>
                    <tr>
                      <th scope="col">Bug</th>
                      <th scope="col">Status</th>
                      <th scope="col" class="text-right">Result links</th>
                      <th scope="col">Runs</th>
                      <th scope="col">Navigation</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="bug in linkedDefects.items" :key="bug.bug_uuid">
                      <td class="defect-title-cell">
                        <v-btn
                          size="small"
                          variant="text"
                          class="font-weight-medium px-0"
                          :aria-label="`Show details for ${bug.short_name || bug.title}`"
                          @click="openBugDetail(bug)"
                        >
                          {{ bug.short_name || 'Bug' }}
                        </v-btn>
                        <div class="text-body-2 text-medium-emphasis text-truncate defect-title">{{ bug.title }}</div>
                      </td>
                      <td>
                        <v-chip size="small" :color="statusColor(bug.status)" variant="tonal">
                          {{ bug.status }}
                        </v-chip>
                      </td>
                      <td class="text-right">{{ bug.link_count }}</td>
                      <td>
                        <div v-if="bug.result_links?.length" class="d-flex flex-wrap ga-1">
                          <v-btn
                            v-for="link in bug.result_links"
                            :key="`${link.run_id}-${link.result_id}`"
                            size="small"
                            variant="text"
                            :to="runResultHref(link)"
                            :aria-label="`Open run ${shortId(link.run_id)}, result ${shortId(link.result_id)}`"
                          >
                            Result {{ shortId(link.result_id) }}
                          </v-btn>
                        </div>
                        <span v-else class="text-medium-emphasis">—</span>
                        <div v-if="bug.result_links_truncated" class="text-caption text-medium-emphasis mt-1">
                          Showing first {{ bug.result_links.length }} of {{ bug.link_count }} result links.
                        </div>
                      </td>
                      <td>
                        <v-btn size="small" variant="text" prepend-icon="mdi-bug-outline" @click="openBugDetail(bug)">
                          Details
                        </v-btn>
                      </td>
                    </tr>
                  </tbody>
                </v-table>

                <div v-if="linkedDefects.total > linkedDefects.pageSize" class="d-flex justify-center pt-3">
                  <v-pagination
                    v-model="linkedDefects.page"
                    :length="pageCount(linkedDefects.total, linkedDefects.pageSize)"
                    :total-visible="5"
                    aria-label="Linked bug pages"
                    @update:model-value="loadLinkedBugs"
                  />
                </div>
              </v-tabs-window-item>

              <v-tabs-window-item value="run">
                <v-progress-linear v-if="linkedDefects.runLoading" indeterminate color="primary" aria-label="Loading run analytics" />
                <v-alert v-else-if="!linkedDefects.error && !linkedDefects.runs.length" type="info" variant="tonal" class="mt-4">
                  No linked defects are attributed to runs for the selected status.
                </v-alert>
                <v-table v-else density="comfortable" class="defect-table mt-3">
                  <thead>
                    <tr><th scope="col">Run</th><th scope="col" class="text-right">Unique bugs</th><th scope="col" class="text-right">Links</th><th scope="col">Open</th></tr>
                  </thead>
                  <tbody>
                    <tr v-for="run in linkedDefects.runs" :key="run.run_id">
                      <td><router-link :to="runHref(run.run_id)">{{ run.run_name }}</router-link></td>
                      <td class="text-right">{{ run.unique_bug_count }}</td>
                      <td class="text-right">{{ run.link_count }}</td>
                      <td><v-btn size="small" variant="text" :to="runHref(run.run_id)">Open run</v-btn></td>
                    </tr>
                  </tbody>
                </v-table>
                <div v-if="linkedDefects.runTotal > linkedDefects.pageSize" class="d-flex justify-center pt-3">
                  <v-pagination v-model="linkedDefects.runPage" :length="pageCount(linkedDefects.runTotal, linkedDefects.pageSize)" :total-visible="5" aria-label="Runs pages" @update:model-value="loadLinkedBugsByRun" />
                </div>
              </v-tabs-window-item>

              <v-tabs-window-item value="suite">
                <v-progress-linear v-if="linkedDefects.suiteLoading" indeterminate color="primary" aria-label="Loading suite analytics" />
                <v-alert v-else-if="!linkedDefects.error && !linkedDefects.suites.length" type="info" variant="tonal" class="mt-4">
                  No linked defects are attributed to suites for the selected status.
                </v-alert>
                <v-table v-else density="comfortable" class="defect-table mt-3">
                  <thead>
                    <tr><th scope="col">Suite</th><th scope="col">Attribution</th><th scope="col" class="text-right">Unique bugs</th><th scope="col" class="text-right">Links</th><th scope="col">Open</th></tr>
                  </thead>
                  <tbody>
                    <tr v-for="suite in linkedDefects.suites" :key="suite.suite_id || suite.attribution">
                      <td>{{ suite.suite_name }}</td>
                      <td>
                        <v-chip size="small" :color="suite.attribution === 'legacy_missing_snapshot' ? 'warning' : 'secondary'" variant="tonal">
                          {{ suiteAttributionLabel(suite.attribution) }}
                        </v-chip>
                      </td>
                      <td class="text-right">{{ suite.unique_bug_count }}</td>
                      <td class="text-right">{{ suite.link_count }}</td>
                      <td>
                        <v-btn v-if="suite.suite_id && suite.attribution !== 'unknown_suite'" size="small" variant="text" :to="`/space/${spaceId}/test-suites/${suite.suite_id}`">Open suite</v-btn>
                        <span v-else class="text-medium-emphasis">{{ suite.attribution === 'legacy_missing_snapshot' ? 'Historical group' : 'Unknown suite group' }}</span>
                      </td>
                    </tr>
                  </tbody>
                </v-table>
                <div v-if="linkedDefects.suiteTotal > linkedDefects.pageSize" class="d-flex justify-center pt-3">
                  <v-pagination v-model="linkedDefects.suitePage" :length="pageCount(linkedDefects.suiteTotal, linkedDefects.pageSize)" :total-visible="5" aria-label="Suites pages" @update:model-value="loadLinkedBugsBySuite" />
                </div>
                <p class="text-caption text-medium-emphasis mt-3">
                  Suite attribution uses the snapshot saved with each run result. Legacy results without a snapshot are grouped as Unknown / legacy.
                </p>
              </v-tabs-window-item>
            </v-tabs-window>
          </template>
        </v-card-text>
      </v-card>
    </v-container>

    <v-dialog
      :model-value="bugDetailOpen"
      max-width="880"
      scrollable
      @update:model-value="(open) => { if (!open) closeBugDetail() }"
    >
      <v-card>
        <v-card-title class="d-flex align-center ga-2">
          <v-icon color="error">mdi-bug-outline</v-icon>
          <span>{{ bugDetail?.short_name || 'Linked bug' }}</span>
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" aria-label="Close bug details" @click="closeBugDetail" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-progress-linear v-if="bugDetailLoading" indeterminate color="primary" aria-label="Loading bug details" />
          <v-alert v-else-if="bugDetailError" type="error" variant="tonal" role="alert">
            This bug could not be loaded in the current space. It may have been removed or is no longer accessible.
          </v-alert>
          <template v-else-if="bugDetail">
            <h2 class="text-h6 mb-3">{{ bugDetail.title || 'Untitled bug' }}</h2>
            <div class="d-flex flex-wrap align-center ga-2 mb-4">
              <v-chip size="small" :color="statusColor(bugDetail.state)" variant="tonal">
                {{ bugDetail.state || 'Unknown status' }}
              </v-chip>
              <span class="text-caption text-medium-emphasis">Stable ID: {{ bugDetail.link_uuid }}</span>
            </div>
            <v-sheet rounded="lg" color="surface-variant" class="pa-4 bug-detail-text">
              <p v-if="bugDetail.text">{{ bugDetail.text }}</p>
              <span v-else class="text-medium-emphasis">No description provided.</span>
            </v-sheet>
            <p v-if="bugDetail.steps" class="text-body-2 mt-4 bug-detail-text">
              <strong>Steps:</strong> {{ bugDetail.steps }}
            </p>
          </template>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeBugDetail">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useLogger } from '@/composables/useLogger'
import { useRoute, useRouter } from 'vue-router'
import { analyticsService, bugService } from '@/services'
import PageHeaderComponent from '@/components/common/pageHeaderComponent.vue'

const log = useLogger('app')
const route = useRoute()
const router = useRouter()
const spaceId = computed(() => route.params.spaceId)
const selectedBugUuid = computed(() => route.query.bug_uuid)

const loader = ref(true)
const dashboardError = ref(false)
const dashboardErrorStatus = ref(0)
const stats = ref({
  cases: { total: 0, manual: 0, checklist: 0, automated: 0 },
  suites: 0,
  runs: { total: 0, active: 0 },
  latest_results: { total: 0, passed: 0, failed: 0, blocked: 0, skipped: 0, not_run: 0 }
})
const topFailed = ref([])
const trend = ref([])
const bugDetail = ref(null)
const bugDetailOpen = ref(false)
const bugDetailLoading = ref(false)
const bugDetailError = ref(false)
const defectView = ref('list')
const defectStatus = ref(null)
const statusOptions = [
  { title: 'All statuses', value: null },
  { title: 'Open', value: 'OPEN' },
  { title: 'Fixed', value: 'FIXED' },
  { title: 'Reopen', value: 'REOPEN' },
  { title: 'Other', value: 'OTHER' }
]
const defectMetrics = [
  { key: 'unique_bug_count', label: 'Unique bugs', color: 'error' },
  { key: 'link_count', label: 'Result links', color: 'primary' },
  { status: 'OPEN', label: 'Open', color: 'warning' },
  { status: 'FIXED', label: 'Fixed', color: 'success' },
  { status: 'REOPEN', label: 'Reopen', color: 'deep-orange' },
  { status: 'OTHER', label: 'Other', color: 'secondary' }
]
const linkedDefects = ref({
  loading: true,
  error: false,
  summary: null,
  items: [],
  page: 1,
  pageSize: 25,
  total: 0,
  runs: [],
  runPage: 1,
  runTotal: 0,
  runLoading: false,
  suites: [],
  suitePage: 1,
  suiteTotal: 0,
  suiteLoading: false
})
let dashboardRequest = 0
let linkedRequest = 0
let runRequest = 0
let suiteRequest = 0
let activeSpaceRequest = 0
let bugDetailRequest = 0

const dashboardHasData = computed(() => Boolean(
  stats.value.cases.total || stats.value.suites || stats.value.runs.total || stats.value.latest_results.total || topFailed.value.length || trend.value.length
))

function retryDashboard() {
  loadDashboard(spaceId.value, ++dashboardRequest)
}

async function loadDashboard(space, requestId) {
  loader.value = true
  dashboardError.value = false
  try {
    const [statsRes, topRes, trendRes] = await Promise.all([
      analyticsService.getSpaceStats(space),
      analyticsService.getTopFailed(space),
      analyticsService.getTrend(space)
    ])
    if (requestId !== dashboardRequest || space !== spaceId.value) return
    stats.value = statsRes.data
    topFailed.value = topRes.data
    trend.value = trendRes.data
  } catch (e) {
    if (requestId === dashboardRequest) {
      dashboardError.value = true
      dashboardErrorStatus.value = Number(e?.response?.status || 0)
      log.error('request failed', e)
    }
  } finally {
    if (requestId === dashboardRequest) loader.value = false
  }
}

function linkedParams(page) {
  const params = { page, page_size: linkedDefects.value.pageSize }
  if (defectStatus.value) params.status = defectStatus.value
  return params
}

async function loadLinkedBugs() {
  const space = spaceId.value
  const requestId = ++linkedRequest
  if (!space) return
  linkedDefects.value.loading = true
  linkedDefects.value.error = false
  try {
    const response = await analyticsService.getLinkedBugs(space, linkedParams(linkedDefects.value.page))
    if (requestId !== linkedRequest || space !== spaceId.value) return
    const data = response.data
    linkedDefects.value.summary = data.summary
    linkedDefects.value.items = data.items || []
    linkedDefects.value.total = data.total || 0
    linkedDefects.value.pageSize = data.page_size || linkedDefects.value.pageSize
  } catch (error) {
    if (requestId === linkedRequest && space === spaceId.value) {
      linkedDefects.value.error = true
      log.error('linked defect analytics request failed', error)
    }
  } finally {
    if (requestId === linkedRequest && space === spaceId.value) linkedDefects.value.loading = false
  }
}

async function loadLinkedBugsByRun() {
  const space = spaceId.value
  const requestId = ++runRequest
  if (!space) return
  linkedDefects.value.runLoading = true
  try {
    const response = await analyticsService.getLinkedBugsByRun(space, linkedParams(linkedDefects.value.runPage))
    if (requestId !== runRequest || space !== spaceId.value) return
    linkedDefects.value.runs = response.data.items || []
    linkedDefects.value.runTotal = response.data.total || 0
  } catch (error) {
    if (requestId === runRequest && space === spaceId.value) {
      linkedDefects.value.error = true
      log.error('run defect analytics request failed', error)
    }
  } finally {
    if (requestId === runRequest && space === spaceId.value) linkedDefects.value.runLoading = false
  }
}

async function loadLinkedBugsBySuite() {
  const space = spaceId.value
  const requestId = ++suiteRequest
  if (!space) return
  linkedDefects.value.suiteLoading = true
  try {
    const response = await analyticsService.getLinkedBugsBySuite(space, linkedParams(linkedDefects.value.suitePage))
    if (requestId !== suiteRequest || space !== spaceId.value) return
    linkedDefects.value.suites = response.data.items || []
    linkedDefects.value.suiteTotal = response.data.total || 0
  } catch (error) {
    if (requestId === suiteRequest && space === spaceId.value) {
      linkedDefects.value.error = true
      log.error('suite defect analytics request failed', error)
    }
  } finally {
    if (requestId === suiteRequest && space === spaceId.value) linkedDefects.value.suiteLoading = false
  }
}

function retryLinkedDefects() {
  loadLinkedBugs()
  loadLinkedBugsByRun()
  loadLinkedBugsBySuite()
}

function pageCount(total, pageSize) {
  return Math.max(1, Math.ceil(total / pageSize))
}

function statusColor(status) {
  return ({ OPEN: 'warning', FIXED: 'success', REOPEN: 'deep-orange', OTHER: 'secondary' })[status] || 'secondary'
}

function suiteAttributionLabel(attribution) {
  return ({
    legacy_missing_snapshot: 'Historical legacy',
    unknown_suite: 'Unknown suite',
    snapshot_without_suite: 'No suite assigned',
    snapshot: 'Run snapshot'
  })[attribution] || 'Unknown attribution'
}

function shortId(value) {
  return String(value).slice(0, 8)
}

function runHref(runId) {
  return `/space/${spaceId.value}/test-runs/${runId}`
}

function runResultHref(link) {
  return {
    path: runHref(link.run_id),
    query: { result_id: link.result_id }
  }
}

function openBugDetail(bug) {
  router.push({ query: { ...route.query, bug_uuid: bug.bug_uuid } })
}

async function loadBugDetail(uuid, space) {
  const requestId = ++bugDetailRequest
  bugDetail.value = null
  bugDetailError.value = false
  bugDetailLoading.value = true
  bugDetailOpen.value = true
  try {
    const response = await bugService.getByLinkUuid(space, uuid)
    if (requestId !== bugDetailRequest || String(selectedBugUuid.value) !== String(uuid) || String(spaceId.value) !== String(space)) return
    if (String(response.data.spaces_id) !== String(space)) {
      bugDetailError.value = true
      return
    }
    bugDetail.value = response.data
  } catch (error) {
    if (requestId === bugDetailRequest && String(selectedBugUuid.value) === String(uuid)) {
      bugDetailError.value = true
      log.error('linked bug detail request failed', error)
    }
  } finally {
    if (requestId === bugDetailRequest) bugDetailLoading.value = false
  }
}

function closeBugDetail() {
  bugDetailOpen.value = false
  if (!selectedBugUuid.value) return
  const query = { ...route.query }
  delete query.bug_uuid
  router.replace({ query })
}

watch(defectStatus, () => {
  linkedDefects.value.page = 1
  linkedDefects.value.runPage = 1
  linkedDefects.value.suitePage = 1
  loadLinkedBugs()
  loadLinkedBugsByRun()
  loadLinkedBugsBySuite()
})

watch(defectView, (view) => {
  if (view === 'run' && !linkedDefects.value.runs.length) loadLinkedBugsByRun()
  if (view === 'suite' && !linkedDefects.value.suites.length) loadLinkedBugsBySuite()
})

watch(spaceId, (space) => {
  const requestId = ++activeSpaceRequest
  dashboardRequest += 1
  linkedRequest += 1
  runRequest += 1
  suiteRequest += 1
  loader.value = true
  defectStatus.value = null
  defectView.value = 'list'
  linkedDefects.value = {
    ...linkedDefects.value,
    loading: true,
    error: false,
    summary: null,
    items: [],
    page: 1,
    total: 0,
    runs: [],
    runPage: 1,
    runTotal: 0,
    suites: [],
    suitePage: 1,
    suiteTotal: 0
  }
  if (!space) return
  const currentDashboardRequest = ++dashboardRequest
  loadDashboard(space, currentDashboardRequest)
  loadLinkedBugs()
  if (requestId === activeSpaceRequest) {
    loadLinkedBugsByRun()
    loadLinkedBugsBySuite()
  }
}, { immediate: true })

watch([spaceId, selectedBugUuid], ([space, uuid]) => {
  if (space && uuid) {
    loadBugDetail(String(uuid), String(space))
  } else {
    bugDetailRequest += 1
    bugDetailOpen.value = false
    bugDetailLoading.value = false
    bugDetailError.value = false
    bugDetail.value = null
  }
}, { immediate: true })
</script>

<style scoped>
.linked-defects-card {
  overflow: hidden;
}

.defect-metric {
  min-height: 82px;
}

.defect-status-filter {
  max-width: 240px;
  min-width: 190px;
}

.defect-title-cell {
  min-width: 220px;
  max-width: 420px;
}

.defect-title {
  max-width: 380px;
}

.bug-detail-text {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.defect-table {
  overflow-x: auto;
}

@media (max-width: 600px) {
  .defect-table {
    min-width: 620px;
  }
}
</style>
