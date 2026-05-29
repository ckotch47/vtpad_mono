<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>

  <div v-else>
    <!-- Header -->
    <v-container fluid class="pb-0">
      <v-row align="center">
        <v-col>
          <v-btn
            variant="text"
            prepend-icon="mdi-arrow-left"
            :to="`/space/${spaceId}/test-runs`"
            class="pl-0"
          >
            Test Runs
          </v-btn>
          <h1 class="text-h4 font-weight-bold mt-1">{{ run.name }}</h1>
          <p v-if="run.description" class="text-body-1 text-medium-emphasis mt-1">
            {{ run.description }}
          </p>
        </v-col>
        <v-col cols="auto">
          <v-chip :color="statusColor(run.status)" size="large" class="text-uppercase font-weight-bold">
            {{ run.status }}
          </v-chip>
        </v-col>
      </v-row>
    </v-container>

    <!-- Stats -->
    <v-container fluid class="py-3">
      <v-row>
        <v-col cols="4" md="2">
          <v-card variant="outlined">
            <v-card-text class="text-center py-3">
              <div class="text-h5 font-weight-bold">{{ stats.total }}</div>
              <div class="text-caption text-medium-emphasis">Total</div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="4" md="2">
          <v-card variant="outlined">
            <v-card-text class="text-center py-3">
              <div class="text-h5 font-weight-bold text-success">{{ stats.passed }}</div>
              <div class="text-caption text-medium-emphasis">Passed</div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="4" md="2">
          <v-card variant="outlined">
            <v-card-text class="text-center py-3">
              <div class="text-h5 font-weight-bold text-error">{{ stats.failed }}</div>
              <div class="text-caption text-medium-emphasis">Failed</div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="4" md="2">
          <v-card variant="outlined">
            <v-card-text class="text-center py-3">
              <div class="text-h5 font-weight-bold text-warning">{{ stats.blocked }}</div>
              <div class="text-caption text-medium-emphasis">Blocked</div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="4" md="2">
          <v-card variant="outlined">
            <v-card-text class="text-center py-3">
              <div class="text-h5 font-weight-bold text-grey">{{ stats.skipped }}</div>
              <div class="text-caption text-medium-emphasis">Skipped</div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="4" md="2">
          <v-card variant="outlined">
            <v-card-text class="text-center py-3">
              <div class="text-h5 font-weight-bold">{{ stats.not_run }}</div>
              <div class="text-caption text-medium-emphasis">Not Run</div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
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
              <v-chip size="small" class="ml-2" color="primary">
                {{ group.results.length }}
              </v-chip>
            </v-card-title>
            <v-divider />
            <v-card-text class="pa-0">
              <v-list density="compact">
                <v-list-item
                  v-for="result in group.results"
                  :key="result.id"
                  class="result-item"
                >
                  <template #prepend>
                    <v-icon :color="statusColor(result.status)">
                      {{ statusIcon(result.status) }}
                    </v-icon>
                  </template>
                  <v-list-item-title class="font-weight-medium">
                    {{ result.testcase?.title || 'Unknown Case' }}
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

    <!-- Edit Result Dialog -->
    <v-dialog v-model="editModal" max-width="600" scrollable>
      <v-card v-if="editingResult">
        <v-card-title class="d-flex align-center">
          <span>Update Result</span>
          <v-spacer />
          <v-btn v-if="editingResult.status === 'failed'" color="error" size="small" prepend-icon="mdi-bug" @click="openBugModal">
            Create Bug
          </v-btn>
        </v-card-title>
        <v-divider />
        <v-card-text>
          <div class="text-subtitle-1 font-weight-medium mb-3">{{ editingResult.testcase?.title }}</div>

          <v-window>
              <v-select
                v-model="editingResult.status"
                :items="['not_run','passed','failed','blocked','skipped']"
                label="Status"
                class="mb-2"
              />
              <v-text-field
                v-model="editingResult.duration_seconds"
                label="Duration (seconds)"
                type="number"
                class="mb-2"
              />
              <v-textarea v-model="editingResult.comment" label="Comment" rows="2" class="mb-2" />
              <v-combobox
                v-model="editingResult.linked_bug_ids"
                :items="spaceBugs"
                item-title="short_name"
                item-value="short_name"
                label="Linked Bugs"
                multiple
                chips
                closable-chips
                clearable
                :return-object="false"
              />
          </v-window>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="editModal = false">Cancel</v-btn>
          <v-btn color="primary" @click="saveResult">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Quick Bug Modal -->
    <v-dialog v-model="bugModal" max-width="560">
      <v-card>
        <v-card-title>Create Bug</v-card-title>
        <v-card-text>
          <v-text-field v-model="newBug.title" label="Title" required autofocus />
          <v-textarea v-model="newBug.steps" label="Steps to Reproduce" rows="3" />
          <v-textarea v-model="newBug.expected" label="Expected Result" rows="2" />
          <v-textarea v-model="newBug.actual" label="Actual Result" rows="2" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="bugModal = false">Cancel</v-btn>
          <v-btn color="error" @click="createBug">Create Bug</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { testRunService, bugService } from '@/services'

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

</style>
