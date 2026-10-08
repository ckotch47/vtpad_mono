<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>

  <div v-else>
    <!-- Header -->
    <v-container fluid class="pb-0">
      <v-row align="center">
        <v-col>
          <v-btn variant="text" prepend-icon="mdi-arrow-left" :to="`/space/${spaceId}/test-runs`" class="pl-0">
            Test Runs
          </v-btn>
          <h1 class="text-h4 font-weight-bold mt-1">{{ run.name }}</h1>
          <p v-if="run.description" class="text-body-1 text-medium-emphasis mt-1">{{ run.description }}</p>
        </v-col>
        <v-col cols="auto">
          <v-chip :color="statusColor(run.status)" size="large" class="text-uppercase font-weight-bold">
            {{ run.status }}
          </v-chip>
        </v-col>
      </v-row>
    </v-container>

    <run-stats-panel :stats="stats" :timer="run.timer" />

    <v-container v-if="run.timer" fluid class="py-0">
      <div class="d-flex align-center ga-2 mb-2" role="status" aria-live="polite">
        <span class="text-body-2">Run timer:</span>
        <v-chip size="small" :color="timerStateColor(run.timer.state)" class="text-capitalize">
          {{ timerStateLabel(run.timer.state) }}
        </v-chip>
        <span v-if="run.timer.interval_count != null" class="text-caption text-medium-emphasis">
          {{ run.timer.interval_count }} timer interval{{ run.timer.interval_count === 1 ? '' : 's' }}
        </span>
        <v-spacer />
        <v-btn
          size="small"
          variant="text"
          prepend-icon="mdi-refresh"
          :loading="timerRefreshLoading"
          @click="refreshTimer"
        >Refresh time</v-btn>
      </div>
    </v-container>

    <!-- Actions -->
    <v-container fluid class="py-0">
      <v-row>
        <v-col>
          <v-btn v-if="run.status === 'draft'" color="primary" prepend-icon="mdi-play" class="mr-2" @click="startRun">
            Start Run
          </v-btn>
          <v-btn v-if="run.status === 'active'" color="success" prepend-icon="mdi-check" class="mr-2" @click="completeRun">
            Complete Run
          </v-btn>
          <v-btn
            v-if="run.status === 'active' && run.timer?.state === 'running'"
            color="warning"
            prepend-icon="mdi-pause"
            :loading="timerActionLoading"
            class="mr-2"
            @click="changeTimerState('pause')"
          >Pause</v-btn>
          <v-btn
            v-if="run.status === 'active' && run.timer?.state === 'paused'"
            color="success"
            prepend-icon="mdi-play"
            :loading="timerActionLoading"
            class="mr-2"
            @click="changeTimerState('resume')"
          >Resume</v-btn>
        </v-col>
      </v-row>
    </v-container>

    <!-- Results by Section -->
    <v-container fluid>
      <v-row class="mb-1" align="center">
        <v-col cols="12" md="5">
          <v-btn-toggle v-model="resultFilter" mandatory density="compact" divided>
            <v-btn value="all">All</v-btn>
            <v-btn value="not_run">Not run</v-btn>
            <v-btn value="failed">Failed</v-btn>
            <v-btn value="blocked">Blocked</v-btn>
          </v-btn-toggle>
        </v-col>
        <v-col cols="12" md="7" class="d-flex justify-md-end align-center ga-2">
          <span class="text-caption">{{ selectedResultIds.length }} selected</span>
          <v-btn size="small" variant="text" :disabled="!nextNotRunResult" @click="goToNextNotRun">Next not run</v-btn>
          <v-select v-model="bulkStatus" :items="bulkStatuses" label="Set selected to" density="compact" hide-details style="max-width: 170px" :disabled="run.status !== 'active' || !selectedResultIds.length" />
          <v-btn size="small" color="primary" :loading="bulkUpdating" :disabled="run.status !== 'active' || !selectedResultIds.length" @click="bulkUpdateResults">Apply</v-btn>
        </v-col>
      </v-row>
      <v-row v-if="groupedResults.length">
        <v-col cols="12" md="4" lg="3" class="py-0">
          <nav aria-label="Run result groups" class="group-navigation-desktop d-none d-md-block">
            <div class="group-navigation__header">
              <div class="d-flex align-center ga-2">
                <v-avatar color="primary" variant="tonal" size="30">
                  <v-icon size="17" aria-hidden="true">mdi-folder-multiple-outline</v-icon>
                </v-avatar>
                <div class="min-width-0">
                  <div class="text-subtitle-2 font-weight-bold">Run map</div>
                  <div class="text-caption text-medium-emphasis">{{ groupedResults.length }} groups</div>
                </div>
              </div>
              <div v-if="activeGroup" class="group-navigation__current">
                <span class="group-navigation__current-label">Current group</span>
                <span class="group-navigation__current-name" :title="activeGroup.accessibleName">{{ activeGroup.pathName }}</span>
              </div>
            </div>
            <v-list density="compact" nav class="group-navigation__list">
              <v-list-item
                v-for="group in groupedResults"
                :key="group.id"
                :href="`#${group.headingId}`"
                :class="{ 'group-navigation__item--current': currentGroupId === group.id }"
                :aria-current="currentGroupId === group.id ? 'location' : undefined"
                :aria-label="`${group.accessibleName}, ${group.results.length} visible results`"
                @click.prevent="goToGroup(group)"
              >
                <v-list-item-title class="group-navigation__title">
                  <span v-if="group.suiteDisplayName" class="group-navigation__suite"><v-icon size="13" aria-hidden="true">mdi-view-grid-outline</v-icon><span>{{ group.suiteDisplayName }}</span></span>
                  <span class="group-navigation__path" :title="group.pathName">
                    <template v-for="(section, index) in group.pathOrder" :key="section.id || `${section.name}-${index}`">
                      <span
                        class="group-navigation__path-segment"
                        :class="{ 'group-navigation__path-segment--current': index === group.pathOrder.length - 1 }"
                      >{{ section.name }}</span>
                      <v-icon v-if="index < group.pathOrder.length - 1" size="13" aria-hidden="true">mdi-chevron-right</v-icon>
                    </template>
                    <span v-if="!group.pathOrder.length" class="group-navigation__path-segment group-navigation__path-segment--current">Default</span>
                  </span>
                </v-list-item-title>
                <template #append>
                  <v-chip size="x-small" :color="currentGroupId === group.id ? 'primary' : undefined">{{ group.results.length }}</v-chip>
                </template>
              </v-list-item>
            </v-list>
          </nav>
        </v-col>
        <v-col cols="12" md="8" lg="9" class="py-0">
          <nav aria-label="Run result groups" class="group-navigation-mobile d-md-none mb-3">
            <div class="d-flex ga-2 overflow-x-auto pb-2">
              <v-btn
                v-for="group in groupedResults"
                :key="group.id"
                :href="`#${group.headingId}`"
                :variant="currentGroupId === group.id ? 'tonal' : 'outlined'"
                :color="currentGroupId === group.id ? 'primary' : undefined"
                size="small"
                :aria-current="currentGroupId === group.id ? 'location' : undefined"
                :aria-label="`${group.accessibleName}, ${group.results.length} visible results`"
                @click.prevent="goToGroup(group)"
              >
                <span class="group-navigation__mobile-label">
                  <span v-if="group.suiteDisplayName" class="group-navigation__mobile-suite">{{ group.suiteDisplayName }}</span>
                  <span class="text-truncate">{{ group.pathName }}</span>
                </span>
                <v-chip size="x-small" color="primary" class="ml-2">{{ group.results.length }}</v-chip>
              </v-btn>
            </div>
          </nav>

          <v-card v-for="group in groupedResults" :id="group.headingId" :key="group.id" class="mb-4">
            <v-card-title class="d-flex align-center py-3">
              <v-icon class="mr-2">mdi-folder-outline</v-icon>
              <h2 :id="`${group.headingId}-title`" tabindex="-1" class="text-subtitle-1 font-weight-medium group-heading mb-0">
                <span v-if="group.suiteDisplayName" class="text-medium-emphasis">{{ group.suiteDisplayName }} / </span>
                {{ group.pathName }}
              </h2>
              <v-chip size="small" class="ml-2" color="primary">{{ group.results.length }}</v-chip>
            </v-card-title>
            <v-divider />
            <v-card-text class="pa-0">
              <v-list density="compact">
                <v-list-item :id="`result-${result.id}`" v-for="result in group.results" :key="result.id" class="result-item">
                  <template #prepend>
                    <v-checkbox-btn
                      v-model="selectedResultIds"
                      :value="result.id"
                      :disabled="run.status !== 'active'"
                      :aria-label="`Select ${result.testcase?.title || 'test case'}`"
                    />
                    <v-tooltip :text="`Change status to ${statusLabel(nextStatus(result.status))}`" location="top">
                      <template #activator="{ props: tooltipProps }">
                        <v-btn
                          v-bind="tooltipProps"
                          icon
                          size="small"
                          variant="text"
                          :color="statusColor(result.status)"
                          :loading="updatingResultId === result.id"
                          :disabled="run.status !== 'active' || updatingResultId === result.id"
                          :aria-label="`Change ${result.testcase?.title || 'test case'} status to ${statusLabel(nextStatus(result.status))}`"
                          @click.stop="cycleResultStatus(result)"
                        >
                          <v-icon>{{ statusIcon(result.status) }}</v-icon>
                        </v-btn>
                      </template>
                    </v-tooltip>
                  </template>
                  <v-list-item-title class="font-weight-medium">
                    <span class="cursor-pointer" @click.stop="openCaseDialog(result)">
                      {{ result.testcase?.title || 'Unknown Case' }}
                    </span>
                    <v-chip size="x-small" :color="typeColor(result.testcase?.type)" class="ml-2">
                      {{ result.testcase?.type }}
                    </v-chip>
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip size="x-small" :color="result.testcase_snapshot ? 'secondary' : 'warning'" class="mr-2">
                      {{ result.testcase_snapshot ? `Snapshot v${result.testcase?.version_number || ''}` : 'Legacy live case' }}
                    </v-chip>
                    <span v-if="result.comment" class="text-medium-emphasis">{{ result.comment }}</span>
                    <span v-else class="text-grey">No comment</span>
                    <span v-if="hasDuration(result.duration_seconds)" class="ml-2 text-caption">({{ formatDuration(result.duration_seconds) }})</span>
                  </v-list-item-subtitle>
                  <template #append>
                    <v-tooltip v-if="result.testcase_id" text="Open test case in a new tab" location="top">
                      <template #activator="{ props: tooltipProps }">
                        <v-btn
                          v-bind="tooltipProps"
                          :href="testCaseHref(result.testcase_id)"
                          target="_blank"
                          rel="noopener noreferrer"
                          icon
                          size="x-small"
                          variant="text"
                          :aria-label="`Open ${result.testcase?.title || 'test case'} in a new tab`"
                          @click.stop
                        >
                          <v-icon>mdi-open-in-new</v-icon>
                        </v-btn>
                      </template>
                    </v-tooltip>
                    <v-chip
                      v-for="bug in result.linked_bugs || []"
                      :key="bug.id"
                      size="x-small"
                      color="error"
                      class="mr-1"
                    >
                      #{{ bug.short_name || bug.title }}
                    </v-chip>
                    <v-chip
                      v-for="bugId in result.linked_bug_ids"
                      :key="bugId"
                      size="x-small"
                      color="error"
                      class="mr-1"
                      :to="`/space/${spaceId}/bugs?shortName=${bugId}`"
                    >
                      #{{ bugId }}
                    </v-chip>
                    <v-btn
                      icon
                      size="x-small"
                      variant="text"
                      :disabled="run.status !== 'active'"
                      :aria-label="`Update ${result.testcase?.title || 'test case'} result`"
                      @click="openResultModal(result)"
                    >
                      <v-icon>mdi-pencil</v-icon>
                    </v-btn>
                  </template>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>

        </v-col>
      </v-row>
      <v-row v-else>
        <v-col>
          <v-card class="text-center pa-10" variant="outlined">
            <v-icon size="64" color="grey-lighten-1">mdi-playlist-remove</v-icon>
            <div class="text-h6 text-grey mt-4">
              {{ results.length ? 'No test cases match this filter' : 'No test cases in this run' }}
            </div>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <run-result-edit-dialog
      v-model="editModal"
      :result="editingResult"
      :space-bugs="spaceBugs"
      :saving="savingResult"
      :has-unsaved-changes="resultEditDirty"
      @update:result="editingResult = $event"
      @save="saveResult"
      @create-bug="openBugModal"
    />

    <case-view-dialog v-model="caseDialogOpen" :test-case="selectedCase" @edit="caseDialogOpen = false" />

    <quick-bug-dialog
      :model-value="bugModal"
      :bug="newBug"
      :saving="creatingBug"
      :has-unsaved-changes="quickBugDirty"
      :retrying="Boolean(editingResult && pendingQuickBugAttempts[editingResult.id])"
      @update:model-value="handleBugModalUpdate"
      @update:bug="newBug = $event"
      @create="createBug"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useLogger } from '@/composables/useLogger'
import { testRunService, bugService, testCaseService } from '@/services'
import RunStatsPanel from './RunStatsPanel.vue'
import RunResultEditDialog from './RunResultEditDialog.vue'
import QuickBugDialog from './QuickBugDialog.vue'
import CaseViewDialog from '@/components/test-plans/detail/CaseViewDialog.vue'

const log = useLogger('testRunDetail')
const route = useRoute()

const spaceId = computed(() => route.params.spaceId)
const runId = computed(() => route.params.runId)

const run = ref({})
const stats = ref({})
const results = ref([])
const loader = ref(true)
const editModal = ref(false)
const editingResult = ref(null)
const spaceBugs = ref([])
const bugModal = ref(false)
const newBug = ref({ title: '', steps: '', expected: '', actual: '' })
const initialBug = ref(null)
const caseDialogOpen = ref(false)
const selectedCase = ref(null)
const updatingResultId = ref(null)
const resultFilter = ref('all')
const selectedResultIds = ref([])
const bulkStatus = ref('passed')
const bulkUpdating = ref(false)
const bulkStatuses = ['not_run', 'passed', 'failed', 'blocked', 'skipped']
const resultStatusCycle = ['not_run', 'passed', 'failed', 'blocked', 'skipped']
const timerActionLoading = ref(false)
const timerRefreshLoading = ref(false)
const savingResult = ref(false)
const creatingBug = ref(false)
const resultEditDirty = computed(() => {
  const result = editingResult.value
  if (!result) return false
  const bugIds = (result.linked_bugs || []).map(bug => bug.id)
  return result.status !== result.originalStatus ||
    result.duration_seconds !== result.originalDurationSeconds ||
    result.comment !== result.originalComment ||
    JSON.stringify(bugIds) !== JSON.stringify(result.originalLinkedBugIds)
})
const quickBugDirty = computed(() => Boolean(initialBug.value) && JSON.stringify(newBug.value) !== JSON.stringify(initialBug.value))
const pendingQuickBugAttempts = ref({})
const currentGroupId = ref(null)
const loadedRunId = ref(null)
let drilldownFocused = false
let drilldownRequestVersion = 0
let groupScrollFrame = null

const groupedResults = computed(() => {
  const groups = new Map()
  const visibleResults = resultFilter.value === 'all'
    ? results.value
    : results.value.filter((result) => result.status === resultFilter.value)
  for (const result of visibleResults) {
    const testcase = result.testcase || {}
    const suiteId = testcase.suite_id ?? 'default-suite'
    const suiteName = testcase.suite_name || ''
    const suiteDisplayName = suiteName || (suiteId === 'default-suite' ? '' : `Suite ${String(suiteId).slice(0, 8)}`)
    const sectionPath = getSectionPath(testcase)
    const pathKey = sectionPath.map((section) => section.id ?? section.name)
    const key = JSON.stringify([suiteId, suiteName, pathKey])
    if (!groups.has(key)) {
      const pathName = sectionPath.map((section) => section.name).filter(Boolean).join(' / ') || 'Default'
      const headingId = `run-group-${encodeGroupKey(key)}`
      groups.set(key, {
        id: key,
        headingId,
        suiteId,
        suiteName,
        suiteDisplayName,
        pathOrder: sectionPath,
        pathName,
        accessibleName: suiteDisplayName ? `${suiteDisplayName}, ${pathName}` : pathName,
        results: []
      })
    }
    groups.get(key).results.push(result)
  }
  return [...groups.values()].sort(compareGroups)
})

const activeGroup = computed(() => groupedResults.value.find((group) => group.id === currentGroupId.value) || null)

function getSectionPath(testcase) {
  if (Array.isArray(testcase.section_path)) {
    const savedPath = testcase.section_path.filter((section) => section && typeof section === 'object')
    if (savedPath.length) return savedPath
  }
  if (testcase.section && typeof testcase.section === 'object' && (testcase.section.id || testcase.section.name)) {
    return [testcase.section]
  }
  return []
}

function encodeGroupKey(key) {
  return Array.from(key).map((character) => character.codePointAt(0).toString(16)).join('-')
}

function compareGroups(left, right) {
  const suiteNameOrder = left.suiteName.localeCompare(right.suiteName)
  if (suiteNameOrder !== 0) return suiteNameOrder
  const suiteIdOrder = String(left.suiteId).localeCompare(String(right.suiteId))
  if (suiteIdOrder !== 0) return suiteIdOrder
  const length = Math.max(left.pathOrder.length, right.pathOrder.length)
  for (let index = 0; index < length; index += 1) {
    const leftSection = left.pathOrder[index]
    const rightSection = right.pathOrder[index]
    if (!leftSection || !rightSection) return leftSection ? 1 : -1
    const leftSort = getSectionSortOrder(leftSection.sort)
    const rightSort = getSectionSortOrder(rightSection.sort)
    if (leftSort !== rightSort) return leftSort - rightSort
    const nameOrder = String(leftSection.name || '').localeCompare(String(rightSection.name || ''))
    if (nameOrder !== 0) return nameOrder
    const idOrder = String(leftSection.id || '').localeCompare(String(rightSection.id || ''))
    if (idOrder !== 0) return idOrder
  }
  return 0
}

function getSectionSortOrder(sort) {
  if (sort === null || sort === undefined || sort === '') return Number.MAX_SAFE_INTEGER
  const numericSort = Number(sort)
  return Number.isFinite(numericSort) ? numericSort : Number.MAX_SAFE_INTEGER
}

const nextNotRunResult = computed(() => results.value.find((result) => result.status === 'not_run'))

async function loadRun({ showLoader = true } = {}) {
  const requestedRunId = String(runId.value)
  if (showLoader) loader.value = true
  try {
    const res = await testRunService.getDetail(requestedRunId)
    if (requestedRunId !== String(runId.value)) return
    run.value = res.data.run
    stats.value = res.data.stats
    results.value = res.data.results
    selectedResultIds.value = selectedResultIds.value.filter((id) => results.value.some((result) => result.id === id))
    loadedRunId.value = requestedRunId
    await nextTick()
    focusDrilldownResult()
  } finally {
    if (showLoader && requestedRunId === String(runId.value)) loader.value = false
  }
}

function focusDrilldownResult() {
  const resultId = route.query.result_id
  if (drilldownFocused || loadedRunId.value !== String(runId.value) || typeof resultId !== 'string' || !resultId) return
  const resultElement = document.getElementById(`result-${resultId}`)
  if (!resultElement) return

  drilldownFocused = true
  const requestVersion = drilldownRequestVersion
  resultElement.setAttribute('tabindex', '-1')
  requestAnimationFrame(() => {
    if (requestVersion !== drilldownRequestVersion || resultId !== route.query.result_id) return
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    resultElement.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'center' })
    resultElement.focus({ preventScroll: true })
  })
}

function resetDrilldownFocus() {
  drilldownFocused = false
  drilldownRequestVersion += 1
}

watch(() => route.query.result_id, async () => {
  resetDrilldownFocus()
  await nextTick()
  focusDrilldownResult()
})

watch(runId, async (newRunId, previousRunId) => {
  if (!newRunId || newRunId === previousRunId) return
  resetDrilldownFocus()
  loadedRunId.value = null
  run.value = {}
  stats.value = {}
  results.value = []
  selectedResultIds.value = []
  currentGroupId.value = null
  await loadRun()
})

async function refreshTimer() {
  if (timerRefreshLoading.value) return
  timerRefreshLoading.value = true
  try {
    await loadRun({ showLoader: false })
  } finally {
    timerRefreshLoading.value = false
  }
}

function loadBugs() {
  bugService.list({
    space_id: spaceId.value,
    state: ['OPEN', 'REOPEN', 'FIXED'],
    limit: 100
  }).then(res => {
    spaceBugs.value = res.data || []
  }).catch(() => {
    spaceBugs.value = []
  })
}

function startRun() {
  testRunService.start(runId.value).then(() => loadRun())
}

function completeRun() {
  testRunService.complete(runId.value).then(() => loadRun())
}

async function changeTimerState(action) {
  if (timerActionLoading.value) return
  timerActionLoading.value = true
  try {
    await testRunService[action](runId.value)
    await loadRun()
  } catch (error) {
    log.error(`failed to ${action} run timer`, error)
  } finally {
    timerActionLoading.value = false
  }
}

function hasDuration(value) {
  return value !== null && value !== undefined
}

function formatDuration(seconds) {
  if (!hasDuration(seconds)) return 'No data'
  const total = Math.max(0, Math.floor(seconds))
  const hours = Math.floor(total / 3600)
  const minutes = Math.floor((total % 3600) / 60)
  const remainder = total % 60
  return hours > 0
    ? `${hours}h ${String(minutes).padStart(2, '0')}m ${String(remainder).padStart(2, '0')}s`
    : `${minutes}m ${String(remainder).padStart(2, '0')}s`
}

function timerStateLabel(state) {
  return {
    not_started: 'not started',
    running: 'running',
    paused: 'paused',
    stopped: 'stopped',
    untracked: 'untracked'
  }[state] || state || 'unavailable'
}

function timerStateColor(state) {
  return { running: 'success', paused: 'warning', stopped: 'grey', untracked: 'info' }[state] || 'default'
}

function openResultModal(result) {
  editingResult.value = {
    ...result,
    originalStatus: result.status,
    originalDurationSeconds: result.duration_seconds,
    originalComment: result.comment,
    originalLinkedBugIds: (result.linked_bugs || []).map(bug => bug.id),
    linked_bugs: [...(result.linked_bugs || [])]
  }
  editModal.value = true
}

function openCaseDialog(result) {
  const snapshot = result?.testcase_snapshot
  if (snapshot) {
    selectedCase.value = { ...snapshot, id: snapshot.testcase_id || result.testcase_id }
    caseDialogOpen.value = true
    return
  }
  testCaseService.getById(result?.testcase_id || result).then(res => {
    selectedCase.value = res.data
    caseDialogOpen.value = true
  })
}

function testCaseHref(id) {
  return `/space/${spaceId.value}/test-cases/${id}`
}

function nextStatus(status) {
  const currentIndex = resultStatusCycle.indexOf(status)
  return resultStatusCycle[(currentIndex + 1) % resultStatusCycle.length]
}

function statusLabel(status) {
  return {
    not_run: 'not run',
    passed: 'passed',
    failed: 'failed',
    blocked: 'blocked',
    skipped: 'skipped'
  }[status] || status
}

function applyResultUpdate(updatedResult) {
  const resultChanges = { ...updatedResult }
  delete resultChanges.originalStatus
  delete resultChanges.originalLinkedBugIds
  const result = results.value.find((item) => item.id === resultChanges.id)
  if (!result) return
  const previousStatus = result.status
  Object.assign(result, resultChanges)
  if (previousStatus !== result.status) {
    stats.value = {
      ...stats.value,
      [previousStatus]: Math.max(0, (stats.value[previousStatus] || 0) - 1),
      [result.status]: (stats.value[result.status] || 0) + 1
    }
  }
  selectedResultIds.value = selectedResultIds.value.filter((id) => results.value.some((item) => item.id === id))
}

async function cycleResultStatus(result) {
  if (run.value.status !== 'active' || updatingResultId.value === result.id) return

  const status = nextStatus(result.status)
  updatingResultId.value = result.id
  try {
    await testRunService.updateResult(result.id, { status })
    applyResultUpdate({ id: result.id, status })
  } catch (error) {
    log.error('failed to cycle test result status', error)
  } finally {
    updatingResultId.value = null
  }
}

function goToNextNotRun() {
  if (!nextNotRunResult.value) return
  resultFilter.value = 'all'
  requestAnimationFrame(() => document.getElementById(`result-${nextNotRunResult.value.id}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' }))
}

function goToGroup(group) {
  currentGroupId.value = group.id
  requestAnimationFrame(() => {
    const heading = document.getElementById(`${group.headingId}-title`)
    if (!heading) return
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    heading.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' })
    heading.focus({ preventScroll: true })
  })
}

function syncCurrentGroup() {
  if (groupScrollFrame !== null) return
  groupScrollFrame = requestAnimationFrame(() => {
    groupScrollFrame = null
    const visibleGroups = groupedResults.value
      .map((group) => ({ group, element: document.getElementById(group.headingId) }))
      .filter(({ element }) => element)
    if (!visibleGroups.length) return

    const markerLine = Math.min(240, window.innerHeight * 0.3)
    const precedingGroup = visibleGroups
      .filter(({ element }) => element.getBoundingClientRect().top <= markerLine)
      .at(-1)
    const currentGroup = precedingGroup || visibleGroups.find(({ element }) => element.getBoundingClientRect().bottom > 0)
    if (currentGroup) currentGroupId.value = currentGroup.group.id
  })
}

watch(groupedResults, async () => {
  await nextTick()
  syncCurrentGroup()
}, { flush: 'post' })

onUnmounted(() => {
  window.removeEventListener('scroll', syncCurrentGroup)
  window.removeEventListener('resize', syncCurrentGroup)
  if (groupScrollFrame !== null) cancelAnimationFrame(groupScrollFrame)
})

async function bulkUpdateResults() {
  if (run.value.status !== 'active' || !selectedResultIds.value.length) return
  bulkUpdating.value = true
  try {
    await testRunService.bulkUpdateResults({ result_ids: selectedResultIds.value, status: bulkStatus.value })
    for (const resultId of selectedResultIds.value) {
      applyResultUpdate({ id: resultId, status: bulkStatus.value })
    }
    selectedResultIds.value = []
  } catch (error) { log.error('failed to bulk update test results', error) } finally { bulkUpdating.value = false }
}

async function saveResult() {
  if (savingResult.value || !editingResult.value) return
  savingResult.value = true
  const duration = editingResult.value.duration_seconds
  const parsedDuration = duration === '' || duration === null || duration === undefined
    ? null
    : Number(duration)
  const payload = {
    duration_seconds: Number.isNaN(parsedDuration) ? null : parsedDuration,
    comment: editingResult.value.comment
  }
  if (editingResult.value.status !== editingResult.value.originalStatus) {
    payload.status = editingResult.value.status
  }
  try {
    await testRunService.updateResult(editingResult.value.id, payload)
    const targetBugIds = (editingResult.value.linked_bugs || []).map(bug => bug.id)
    const currentBugIds = [...editingResult.value.originalLinkedBugIds]
    for (const bugId of currentBugIds.filter((id) => !targetBugIds.includes(id))) {
      await testRunService.unlinkBug(editingResult.value.id, bugId)
      editingResult.value.originalLinkedBugIds = currentBugIds.filter((id) => id !== bugId)
    }
    for (const bugId of targetBugIds.filter((id) => !currentBugIds.includes(id))) {
      await testRunService.linkBug(editingResult.value.id, bugId)
      editingResult.value.originalLinkedBugIds = [...editingResult.value.originalLinkedBugIds, bugId]
    }
    applyResultUpdate(editingResult.value)
    editModal.value = false
  } catch (error) {
    log.error('failed to update test result', error)
    try {
      await loadRun({ showLoader: false })
    } catch (reloadError) {
      log.error('failed to reload run after result update error', reloadError)
    }
    return
  } finally {
    savingResult.value = false
  }
  try {
    await loadRun({ showLoader: false })
  } catch (error) {
    log.error('result was saved, but the run could not be reloaded', error)
  }
}

function openBugModal() {
  const pendingAttempt = pendingQuickBugAttempts.value[editingResult.value.id]
  if (pendingAttempt) {
    newBug.value = { ...pendingAttempt.draft }
  } else {
    newBug.value = {
      title: `Bug: ${editingResult.value.testcase?.title || 'Failed test'}`,
      steps: editingResult.value.testcase?.steps || '',
      expected: editingResult.value.testcase?.expected_results || '',
      actual: editingResult.value.comment || ''
    }
  }
  initialBug.value = { ...newBug.value }
  bugModal.value = true
}

function handleBugModalUpdate(open) {
  bugModal.value = open
}

function createBugText(bug) {
  const sections = []
  if (bug.expected) sections.push(`Expected result:\n${bug.expected}`)
  if (bug.actual) sections.push(`Actual result:\n${bug.actual}`)
  return sections.join('\n\n')
}

async function createBug() {
  if (creatingBug.value || !editingResult.value) return
  creatingBug.value = true
  const resultId = editingResult.value.id
  if (!pendingQuickBugAttempts.value[resultId]) {
    pendingQuickBugAttempts.value = {
      ...pendingQuickBugAttempts.value,
      [resultId]: {
        draft: { ...newBug.value },
        request: {
          operation_id: crypto.randomUUID(),
          title: newBug.value.title,
          text: createBugText(newBug.value),
          steps: newBug.value.steps
        }
      }
    }
  }
  const pendingAttempt = pendingQuickBugAttempts.value[resultId]
  try {
    await testRunService.createAndLinkBug(resultId, pendingAttempt.request)
    const attempts = { ...pendingQuickBugAttempts.value }
    delete attempts[resultId]
    pendingQuickBugAttempts.value = attempts
    bugModal.value = false
    editModal.value = false
  } catch (error) {
    log.error('failed to create and link bug to test result', error)
    try {
      await loadRun({ showLoader: false })
    } catch (reloadError) {
      log.error('failed to reload run after quick bug error', reloadError)
    }
    return
  } finally {
    creatingBug.value = false
  }
  try {
    await loadRun({ showLoader: false })
  } catch (error) {
    log.error('bug was created, but the run could not be reloaded', error)
  }
}

function statusColor(status) {
  const map = { passed: 'success', failed: 'error', blocked: 'warning', skipped: 'grey', not_run: 'default' }
  return map[status] || 'default'
}

function statusIcon(status) {
  const map = {
    passed: 'mdi-check-circle',
    failed: 'mdi-close-circle',
    blocked: 'mdi-minus-circle',
    skipped: 'mdi-arrow-right-circle',
    not_run: 'mdi-circle-outline'
  }
  return map[status] || 'mdi-help-circle'
}

function typeColor(type) {
  const map = { manual: 'primary', checklist: 'success', automated: 'warning' }
  return map[type] || 'grey'
}

onMounted(() => {
  window.addEventListener('scroll', syncCurrentGroup, { passive: true })
  window.addEventListener('resize', syncCurrentGroup)
  loadRun()
  loadBugs()
})
</script>

<style scoped>
.result-item {
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}
.result-item:last-child {
  border-bottom: none;
}
.result-item:focus {
  outline: 2px solid rgb(var(--v-theme-primary));
  outline-offset: -2px;
}
.cursor-pointer {
  cursor: pointer;
}
.group-navigation-desktop {
  position: sticky;
  top: max(16px, env(safe-area-inset-top));
  max-height: calc(100vh - max(32px, env(safe-area-inset-top) + 16px));
  overflow-y: auto;
  overscroll-behavior: contain;
  scrollbar-gutter: stable;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 12px;
  background: rgb(var(--v-theme-surface));
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}
.group-navigation__header {
  position: sticky;
  top: 0;
  z-index: 1;
  padding: 12px;
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  background: rgb(var(--v-theme-surface));
}
.group-navigation__current {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 2px;
  margin-top: 10px;
  padding: 8px 10px;
  border-radius: 8px;
  background: rgba(var(--v-theme-primary), 0.07);
}
.group-navigation__current-label {
  color: rgb(var(--v-theme-primary));
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  line-height: 1.2;
  text-transform: uppercase;
}
.group-navigation__current-name {
  overflow: hidden;
  font-size: 0.82rem;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.group-navigation__list {
  padding: 6px !important;
}
.group-navigation__title {
  min-width: 0;
  white-space: normal;
}
.group-navigation__suite,
.group-navigation__path {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
}
.group-navigation__suite {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 4px;
  color: rgba(var(--v-theme-on-surface), var(--v-medium-emphasis-opacity));
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.025em;
  line-height: 1.35;
  white-space: nowrap;
}
.group-navigation__suite > span {
  overflow: hidden;
  text-overflow: ellipsis;
}
.group-navigation__path {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 1px;
  margin-top: 2px;
  font-size: 0.82rem;
  line-height: 1.45;
  white-space: nowrap;
}
.group-navigation__path-segment {
  min-width: 0;
  flex: 0 1 auto;
  overflow: hidden;
  color: rgba(var(--v-theme-on-surface), 0.66);
  text-overflow: ellipsis;
  white-space: nowrap;
}
.group-navigation__path-segment--current {
  color: rgb(var(--v-theme-on-surface));
  font-weight: 600;
}
.group-navigation-desktop :deep(.v-list-item) {
  position: relative;
  min-height: 48px;
  margin: 2px 4px;
  border-radius: 8px;
}
.group-navigation-desktop :deep(.v-list-item:hover) {
  background: rgba(var(--v-theme-primary), 0.06);
}
.group-navigation-desktop :deep(.v-list-item:focus-visible),
.group-navigation-mobile :deep(.v-btn:focus-visible) {
  outline: 2px solid rgb(var(--v-theme-primary));
  outline-offset: 2px;
}
.group-navigation-desktop :deep(.group-navigation__item--current) {
  background: rgba(var(--v-theme-primary), 0.1);
}
.group-navigation-desktop :deep(.group-navigation__item--current)::before {
  position: absolute;
  top: 8px;
  bottom: 8px;
  left: 0;
  width: 3px;
  border-radius: 0 4px 4px 0;
  background: rgb(var(--v-theme-primary));
  content: '';
}
.group-navigation-mobile > div {
  max-width: 100%;
  overscroll-behavior-x: contain;
  scrollbar-width: thin;
}
.group-navigation__mobile-label {
  display: flex;
  min-width: 0;
  max-width: min(52vw, 240px);
  flex-direction: column;
  align-items: flex-start;
  line-height: 1.2;
}
.group-navigation__mobile-suite {
  max-width: 100%;
  overflow: hidden;
  color: rgba(var(--v-theme-on-surface), var(--v-medium-emphasis-opacity));
  font-size: 0.65rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.group-navigation-mobile :deep(.v-btn) {
  flex: 0 0 auto;
  max-width: min(76vw, 320px);
}
.group-heading {
  scroll-margin-top: max(16px, env(safe-area-inset-top));
}
.group-heading:focus {
  outline: 2px solid rgb(var(--v-theme-primary));
  outline-offset: 3px;
}
@media (max-width: 959px) {
  .group-navigation-mobile > div {
    padding: 2px 2px 8px;
  }
}
</style>
