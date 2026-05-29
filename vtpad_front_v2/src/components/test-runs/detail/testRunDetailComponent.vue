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
                <v-list-item v-for="result in group.results" :key="result.id" class="result-item">
                  <template #prepend>
                    <v-icon :color="statusColor(result.status)">{{ statusIcon(result.status) }}</v-icon>
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
                    <span v-if="result.comment" class="text-medium-emphasis">{{ result.comment }}</span>
                    <span v-else class="text-grey">No comment</span>
                    <span v-if="result.duration_seconds" class="ml-2 text-caption">({{ result.duration_seconds }}s)</span>
                  </v-list-item-subtitle>
                  <template #append>
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
                    <v-btn icon size="x-small" variant="text" @click="openResultModal(result)">
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
import { testRunService, bugService, testCaseService } from '@/services'
import RunStatsPanel from './RunStatsPanel.vue'
import RunResultEditDialog from './RunResultEditDialog.vue'
import QuickBugDialog from './QuickBugDialog.vue'
import CaseViewDialog from '@/components/test-plans/detail/CaseViewDialog.vue'

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

const groupedResults = computed(() => {
  const map = {}
  for (const r of results.value) {
    const sectionId = r.testcase?.section?.id || 'no-section'
    const sectionName = r.testcase?.section?.name || 'No Section'
    if (!map[sectionId]) {
      map[sectionId] = { sectionId, sectionName, results: [] }
    }
    map[sectionId].results.push(r)
  }
  return Object.values(map)
})

function loadRun() {
  testRunService.getDetail(runId.value).then(res => {
    run.value = res.data.run
    stats.value = res.data.stats
    results.value = res.data.results
    loader.value = false
  }).catch(() => { loader.value = false })
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
