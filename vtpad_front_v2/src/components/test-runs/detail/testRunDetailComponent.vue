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

    <run-stats-panel :stats="stats" />

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
      <v-row>
        <v-col>
          <v-card v-for="group in groupedResults" :key="group.sectionId || 'no-section'" class="mb-4">
            <v-card-title class="d-flex align-center py-3">
              <v-icon class="mr-2">mdi-folder-outline</v-icon>
              {{ group.sectionName }}
              <v-chip size="small" class="ml-2" color="primary">{{ group.results.length }}</v-chip>
            </v-card-title>
            <v-divider />
            <v-card-text class="pa-0">
              <v-list density="compact">
                <v-list-item :id="`result-${result.id}`" v-for="result in group.results" :key="result.id" class="result-item">
                  <template #prepend>
                    <v-checkbox-btn
                      v-if="run.status === 'active' && result.status === 'not_run'"
                      v-model="selectedResultIds"
                      :value="result.id"
                      :aria-label="`Select ${result.testcase?.title || 'test case'}`"
                    />
                    <v-tooltip :text="result.status === 'not_run' ? 'Mark test case as passed' : 'Only not-run test cases can be marked quickly'" location="top">
                      <template #activator="{ props: tooltipProps }">
                        <v-btn
                          v-bind="tooltipProps"
                          icon
                          size="small"
                          variant="text"
                          :color="statusColor(result.status)"
                          :loading="passingResultId === result.id"
                          :disabled="run.status !== 'active' || result.status !== 'not_run' || passingResultId === result.id"
                          :aria-label="result.status === 'not_run'
                            ? `Mark ${result.testcase?.title || 'test case'} as passed`
                            : `${result.testcase?.title || 'Test case'} is already executed`"
                          @click.stop="markResultPassed(result)"
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
                    <span v-if="result.duration_seconds" class="ml-2 text-caption">({{ result.duration_seconds }}s)</span>
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
                      :disabled="run.status !== 'active' || result.status !== 'not_run'"
                      :aria-label="result.status === 'not_run' ? `Update ${result.testcase?.title || 'test case'} result` : 'Executed result is immutable'"
                      @click="openResultModal(result)"
                    >
                      <v-icon>mdi-pencil</v-icon>
                    </v-btn>
                  </template>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>

          <v-card v-if="groupedResults.length === 0" class="text-center pa-10" variant="outlined">
            <v-icon size="64" color="grey-lighten-1">mdi-playlist-remove</v-icon>
            <div class="text-h6 text-grey mt-4">No test cases in this run</div>
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
const passingResultId = ref(null)
const resultFilter = ref('all')
const selectedResultIds = ref([])
const bulkStatus = ref('passed')
const bulkUpdating = ref(false)
const bulkStatuses = ['passed', 'failed', 'blocked', 'skipped']

const groupedResults = computed(() => {
  const map = {}
  const visibleResults = resultFilter.value === 'all'
    ? results.value
    : results.value.filter((result) => result.status === resultFilter.value)
  for (const r of visibleResults) {
    const sectionId = r.testcase?.section?.id || 'no-section'
    const sectionName = r.testcase?.section?.name || 'No Section'
    if (!map[sectionId]) {
      map[sectionId] = { sectionId, sectionName, results: [] }
    }
    map[sectionId].results.push(r)
  }
  return Object.values(map)
})

const nextNotRunResult = computed(() => results.value.find((result) => result.status === 'not_run'))

async function loadRun() {
  loader.value = true
  try {
    const res = await testRunService.getDetail(runId.value)
    run.value = res.data.run
    stats.value = res.data.stats
    results.value = res.data.results
    selectedResultIds.value = selectedResultIds.value.filter((id) => results.value.some((result) => result.id === id && result.status === 'not_run'))
  } finally { loader.value = false }
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

function openResultModal(result) {
  editingResult.value = {
    ...result,
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

async function markResultPassed(result) {
  if (run.value.status !== 'active' || result.status !== 'not_run' || passingResultId.value === result.id) return

  passingResultId.value = result.id
  try {
    await testRunService.updateResult(result.id, { status: 'passed' })
    result.status = 'passed'
    await loadRun()
  } catch (error) {
    log.error('failed to mark test result as passed', error)
  } finally {
    passingResultId.value = null
  }
}

function goToNextNotRun() {
  if (!nextNotRunResult.value) return
  resultFilter.value = 'all'
  requestAnimationFrame(() => document.getElementById(`result-${nextNotRunResult.value.id}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' }))
}

async function bulkUpdateResults() {
  if (run.value.status !== 'active' || !selectedResultIds.value.length) return
  bulkUpdating.value = true
  try {
    await testRunService.bulkUpdateResults({ result_ids: selectedResultIds.value, status: bulkStatus.value })
    selectedResultIds.value = []
    await loadRun()
  } catch (error) { log.error('failed to bulk update test results', error) } finally { bulkUpdating.value = false }
}

function saveResult() {
  testRunService.updateResult(editingResult.value.id, {
    status: editingResult.value.status,
    duration_seconds: parseInt(editingResult.value.duration_seconds) || null,
    comment: editingResult.value.comment,
    linked_bug_ids: editingResult.value.linked_bug_ids
  }).then(() => {
    editModal.value = false
    loadRun()
  })
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
  bugService.create({
    title: newBug.value.title,
    text: newBug.value.actual,
    steps: newBug.value.steps,
    spaces: spaceId.value,
    state: 'OPEN'
  }).then(res => {
    const bugShortName = res.data.short_name
    const bugs = [...(editingResult.value.linked_bug_ids || []), bugShortName]
    return testRunService.updateResult(editingResult.value.id, {
      linked_bug_ids: bugs
    })
  }).then(() => {
    bugModal.value = false
    editModal.value = false
    loadRun()
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
</style>
