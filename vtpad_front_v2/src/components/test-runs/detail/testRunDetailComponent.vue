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
      <v-alert
        v-if="run.timer.state === 'untracked'"
        type="info"
        variant="tonal"
        density="compact"
        class="mb-2"
      >This run predates timer tracking. Active and paused time are unavailable.</v-alert>
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
      <v-row v-if="groupedResults.length" class="align-start">
        <v-col cols="12" md="3" lg="2" class="py-0">
          <nav aria-label="Run result groups" class="group-navigation-desktop d-none d-md-block">
            <div class="text-subtitle-2 font-weight-bold mb-2">Groups</div>
            <v-list density="compact" nav class="pa-0">
              <v-list-item
                v-for="group in groupedResults"
                :key="group.id"
                :href="`#${group.headingId}`"
                :aria-label="`${group.accessibleName}, ${group.results.length} visible results`"
                @click.prevent="goToGroup(group)"
              >
                <v-list-item-title class="text-body-2 text-wrap">{{ group.navigationName }}</v-list-item-title>
                <template #append>
                  <v-chip size="x-small" color="primary">{{ group.results.length }}</v-chip>
                </template>
              </v-list-item>
            </v-list>
          </nav>
        </v-col>
        <v-col cols="12" md="9" lg="10" class="py-0">
          <nav aria-label="Run result groups" class="group-navigation-mobile d-md-none mb-3">
            <div class="d-flex ga-2 overflow-x-auto pb-2">
              <v-btn
                v-for="group in groupedResults"
                :key="group.id"
                :href="`#${group.headingId}`"
                variant="outlined"
                size="small"
                :aria-label="`${group.accessibleName}, ${group.results.length} visible results`"
                @click.prevent="goToGroup(group)"
              >
                <span class="text-truncate">{{ group.navigationName }}</span>
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
                    <span class="cursor-pointer" @click.stop="openCaseDialog(result.testcase_id)">
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
      @update:result="editingResult = $event"
      @save="saveResult"
      @create-bug="openBugModal"
    />

    <case-view-dialog v-model="caseDialogOpen" :test-case="selectedCase" @edit="caseDialogOpen = false" />

    <quick-bug-dialog
      v-model="bugModal"
      :bug="newBug"
      @update:bug="newBug = $event"
      @create="createBug"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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
        navigationName: suiteDisplayName ? `${suiteDisplayName} / ${pathName}` : pathName,
        accessibleName: suiteDisplayName ? `${suiteDisplayName}, ${pathName}` : pathName,
        results: []
      })
    }
    groups.get(key).results.push(result)
  }
  return [...groups.values()].sort(compareGroups)
})

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
  if (showLoader) loader.value = true
  try {
    const res = await testRunService.getDetail(runId.value)
    run.value = res.data.run
    stats.value = res.data.stats
    results.value = res.data.results
    selectedResultIds.value = selectedResultIds.value.filter((id) => results.value.some((result) => result.id === id))
  } finally {
    if (showLoader) loader.value = false
  }
}

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
    linked_bug_ids: result.linked_bug_ids || []
  }
  editModal.value = true
}

function openCaseDialog(id) {
  testCaseService.getById(id).then(res => {
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
  requestAnimationFrame(() => {
    const heading = document.getElementById(`${group.headingId}-title`)
    if (!heading) return
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    heading.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' })
    heading.focus({ preventScroll: true })
  })
}

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
  const duration = editingResult.value.duration_seconds
  const parsedDuration = duration === '' || duration === null || duration === undefined
    ? null
    : Number(duration)
  const payload = {
    duration_seconds: Number.isNaN(parsedDuration) ? null : parsedDuration,
    comment: editingResult.value.comment,
    linked_bug_ids: editingResult.value.linked_bug_ids
  }
  if (editingResult.value.status !== editingResult.value.originalStatus) {
    payload.status = editingResult.value.status
  }
  try {
    await testRunService.updateResult(editingResult.value.id, payload)
    applyResultUpdate(editingResult.value)
    editModal.value = false
    await loadRun()
  } catch (error) {
    log.error('failed to update test result', error)
  }
}

function openBugModal() {
  newBug.value = {
    title: `Bug: ${editingResult.value.testcase?.title || 'Failed test'}`,
    steps: editingResult.value.testcase?.steps || '',
    expected: editingResult.value.testcase?.expected_results || '',
    actual: editingResult.value.comment || ''
  }
  bugModal.value = true
}

function createBug() {
  let linkedBugIds = []
  bugService.create({
    title: newBug.value.title,
    text: newBug.value.actual,
    steps: newBug.value.steps,
    spaces: spaceId.value,
    state: 'OPEN'
  }).then(res => {
    const bugShortName = res.data.short_name
    linkedBugIds = [...(editingResult.value.linked_bug_ids || []), bugShortName]
    return testRunService.updateResult(editingResult.value.id, {
      linked_bug_ids: linkedBugIds
    })
  }).then(() => {
    bugModal.value = false
    editModal.value = false
    editingResult.value.linked_bug_ids = linkedBugIds
    applyResultUpdate(editingResult.value)
  }).catch(err => {
    console.error(err)
  })
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
.cursor-pointer {
  cursor: pointer;
}
.group-navigation-desktop {
  position: sticky;
  top: 16px;
  max-height: calc(100vh - 32px);
  overflow-y: auto;
}
.group-heading {
  scroll-margin-top: 16px;
}
.group-heading:focus {
  outline: 2px solid rgb(var(--v-theme-primary));
  outline-offset: 3px;
}
</style>
