<template>
  <v-dialog v-model="open" max-width="1200" scrollable>
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between ga-3">
        <span>Compare completed runs</span>
        <v-btn icon="mdi-close" variant="text" aria-label="Close run comparison" @click="open = false" />
      </v-card-title>

      <v-card-text>
        <v-alert v-if="props.run.status !== 'completed'" type="info" variant="tonal">
          Only completed runs can be compared.
        </v-alert>
        <template v-else>
          <div class="run-comparison__selectors">
            <v-text-field :model-value="props.run.name" label="First run" readonly hide-details />
            <v-autocomplete
              v-model="otherRunId"
              v-model:search="search"
              :items="runOptions"
              item-title="name"
              item-value="id"
              label="Compare with"
              placeholder="Search completed runs"
              no-data-text="No completed runs found"
              clearable
              hide-details
              :loading="optionsLoading"
              @update:model-value="loadComparison"
            >
              <template #item="{ props: itemProps, item }">
                <v-list-item v-bind="itemProps" :subtitle="formatDate(item.raw.completed_at)" />
              </template>
              <template #append-item>
                <v-list-item v-if="runOptions.length < optionsTotal">
                  <v-btn
                    block
                    variant="text"
                    :loading="optionsLoading"
                    @click.stop="loadMoreRuns"
                  >Load older completed runs</v-btn>
                </v-list-item>
              </template>
            </v-autocomplete>
          </div>

          <v-alert v-if="loadError" type="error" variant="tonal" class="mt-4" role="alert">
            {{ errorMessage }}
            <v-btn v-if="!forbidden" size="small" variant="text" @click="loadComparison">Retry</v-btn>
          </v-alert>

          <div v-if="comparison" class="mt-5" :aria-busy="comparisonLoading">
            <v-progress-linear v-if="comparisonLoading" indeterminate color="primary" class="mb-3" />
            <div class="d-flex flex-wrap ga-2 mb-4" aria-label="Comparison totals">
              <v-chip color="success" variant="tonal">Added {{ comparison.summary.added }}</v-chip>
              <v-chip color="error" variant="tonal">Removed {{ comparison.summary.removed }}</v-chip>
              <v-chip color="warning" variant="tonal">Changed {{ comparison.summary.changed }}</v-chip>
              <v-chip color="info" variant="tonal">Inconclusive {{ comparison.summary.inconclusive }}</v-chip>
              <v-chip>Unchanged {{ comparison.summary.unchanged }}</v-chip>
            </div>

            <v-alert v-if="comparison.sources_differ" type="info" variant="tonal" class="mb-4">
              These runs were created from different sources.
              <div class="text-body-2 mt-1">
                {{ sourceLabel(comparison.left_run.source) }} → {{ sourceLabel(comparison.right_run.source) }}
              </div>
            </v-alert>

            <v-select
              v-model="changeFilter"
              :items="changeFilters"
              item-title="title"
              item-value="value"
              label="Show results"
              density="compact"
              hide-details
              class="mb-3"
              style="max-width: 260px"
            />

            <div v-if="filteredResults.length" class="d-flex flex-column ga-2">
              <v-expansion-panels variant="accordion">
                <v-expansion-panel v-for="row in filteredResults" :key="row.testcase_id">
                  <v-expansion-panel-title>
                    <div class="d-flex flex-wrap align-center ga-2">
                      <span class="font-weight-medium">{{ rowTitle(row) }}</span>
                      <v-chip size="x-small" :color="changeColor(row.change_type)">{{ row.change_type }}</v-chip>
                      <span v-if="row.case_fields_changed.length" class="text-caption text-medium-emphasis">
                        Case: {{ row.case_fields_changed.map(fieldLabel).join(', ') }}
                      </span>
                      <span v-if="row.result_fields_changed.length" class="text-caption text-medium-emphasis">
                        Result: {{ row.result_fields_changed.map(fieldLabel).join(', ') }}
                      </span>
                    </div>
                  </v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <v-alert v-if="row.unknown_case_fields.length" type="info" variant="tonal" density="compact" class="mb-3">
                      Historical case content is unavailable for: {{ row.unknown_case_fields.map(fieldLabel).join(', ') }}.
                      This comparison uses the saved run snapshots only.
                    </v-alert>
                    <div class="run-comparison__columns">
                      <section v-for="side in sides" :key="side.key" class="run-comparison__side">
                        <h3 class="text-subtitle-2 font-weight-bold mb-2">{{ side.title }}</h3>
                        <template v-if="row[side.key]">
                          <div class="text-body-2 mb-2">
                            <span class="text-medium-emphasis">Status: </span>
                            {{ row[side.key].result.status }}
                          </div>
                          <div class="text-body-2 mb-2">
                            <span class="text-medium-emphasis">Duration: </span>
                            {{ formatDuration(row[side.key].result.duration_seconds) }}
                          </div>
                          <div v-if="row[side.key].result.comment" class="text-body-2 mb-2">
                            <span class="text-medium-emphasis">Comment: </span>{{ row[side.key].result.comment }}
                          </div>
                          <template v-if="row[side.key].testcase_snapshot">
                            <div v-for="field in visibleCaseFields(row)" :key="field" class="run-comparison__field">
                              <div class="text-caption font-weight-medium text-medium-emphasis">{{ fieldLabel(field) }}</div>
                              <div v-if="isRichField(field)" class="run-comparison__rich" v-html="safeMarkup(row[side.key].testcase_snapshot[snapshotKey(field)])" />
                              <div v-else class="text-body-2">{{ displayValue(row[side.key].testcase_snapshot[snapshotKey(field)]) }}</div>
                            </div>
                          </template>
                          <div v-else class="text-body-2 text-medium-emphasis">Saved case snapshot unavailable.</div>
                        </template>
                        <div v-else class="text-body-2 text-medium-emphasis">Case is not present in this run.</div>
                      </section>
                    </div>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </div>
            <contextual-empty-state
              v-else
              icon="mdi-check-all"
              title="No results in this category"
              text="Choose another comparison filter to see run changes."
            />
          </div>
        </template>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="open = false">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { testRunService } from '@/services'
import { sanitizeHtml } from '@/utils/sanitize'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  spaceId: { type: String, required: true },
  run: { type: Object, required: true }
})
const emit = defineEmits(['update:modelValue'])

const open = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
const otherRunId = ref(null)
const search = ref('')
const runOptions = ref([])
const optionsTotal = ref(0)
const optionPage = ref(1)
const optionsLoading = ref(false)
const comparison = ref(null)
const comparisonLoading = ref(false)
const loadError = ref(false)
const forbidden = ref(false)
const errorMessage = ref('Run comparison could not be loaded.')
const changeFilter = ref('all')
const requestVersion = ref(0)
let optionRequestVersion = 0

const sides = computed(() => [
  { key: 'left', title: comparison.value?.left_run?.name || 'First run' },
  { key: 'right', title: comparison.value?.right_run?.name || 'Second run' }
])
const changeFilters = [
  { title: 'All results', value: 'all' },
  { title: 'Added', value: 'added' },
  { title: 'Removed', value: 'removed' },
  { title: 'Changed', value: 'changed' },
  { title: 'Inconclusive', value: 'inconclusive' },
  { title: 'Unchanged', value: 'unchanged' }
]
const filteredResults = computed(() => (comparison.value?.results || []).filter((row) =>
  changeFilter.value === 'all' || row.change_type === changeFilter.value
))

watch(() => [open.value, props.run.id, props.run.status], ([isOpen]) => {
  requestVersion.value += 1
  if (!isOpen) {
    comparison.value = null
    comparisonLoading.value = false
    return
  }
  comparison.value = null
  otherRunId.value = null
  search.value = ''
  optionPage.value = 1
  loadCompletedRuns('')
})

watch(search, (value) => {
  if (open.value) {
    optionPage.value = 1
    loadCompletedRuns(value || '')
  }
})

async function loadCompletedRuns(query, append = false) {
  const version = ++optionRequestVersion
  const page = append ? optionPage.value + 1 : 1
  optionsLoading.value = true
  try {
    const response = await testRunService.listBySpace(props.spaceId, {
      page,
      page_size: 50,
      sort_by: 'created_at',
      sort_order: 'desc',
      status: 'completed',
      search: query || undefined
    })
    if (version !== optionRequestVersion) return
    const items = (response.data.items || []).filter((item) => item.id !== props.run.id)
    runOptions.value = append
      ? [...runOptions.value, ...items.filter((item) => !runOptions.value.some((existing) => existing.id === item.id))]
      : items
    optionPage.value = page
    const normalizedQuery = String(query || '').toLowerCase()
    const currentRunMatches = !normalizedQuery || [props.run.name, props.run.description]
      .some((value) => String(value || '').toLowerCase().includes(normalizedQuery))
    optionsTotal.value = Math.max(0, Number(response.data.total || 0) - (currentRunMatches ? 1 : 0))
  } catch (error) {
    if (version === optionRequestVersion) runOptions.value = []
  } finally {
    if (version === optionRequestVersion) optionsLoading.value = false
  }
}

function loadMoreRuns() {
  if (optionsLoading.value || runOptions.value.length >= optionsTotal.value) return
  loadCompletedRuns(search.value || '', true)
}

async function loadComparison() {
  const version = ++requestVersion.value
  if (!otherRunId.value) {
    comparison.value = null
    loadError.value = false
    comparisonLoading.value = false
    return
  }
  comparison.value = null
  comparisonLoading.value = true
  loadError.value = false
  forbidden.value = false
  try {
    const response = await testRunService.compare(props.run.id, otherRunId.value)
    if (version === requestVersion.value) comparison.value = response.data
  } catch (error) {
    if (version !== requestVersion.value) return
    loadError.value = true
    forbidden.value = Number(error?.response?.status || 0) === 403
    errorMessage.value = forbidden.value
      ? 'You do not have access to compare these runs.'
      : Number(error?.response?.status || 0) === 422
        ? 'Both runs must be completed before comparison.'
        : 'Run comparison could not be loaded. Check the selected run and try again.'
  } finally {
    if (version === requestVersion.value) comparisonLoading.value = false
  }
}

function rowTitle(row) {
  return row.left?.testcase_snapshot?.title || row.right?.testcase_snapshot?.title || 'Historical case snapshot unavailable'
}

function fieldLabel(field) {
  return ({
    title: 'Title', type: 'Type', suite_id: 'Suite', suite_name: 'Suite name',
    section_path: 'Section path', description: 'Description', preconditions: 'Preconditions',
    steps: 'Steps', expected_results: 'Expected results', priority: 'Priority', tags: 'Tags',
    estimated_duration_seconds: 'Estimated time', status: 'Status', comment: 'Comment',
    duration_seconds: 'Actual duration'
  })[field] || field
}

function snapshotKey(field) {
  return field === 'description' ? 'text' : field
}

function visibleCaseFields(row) {
  return row.case_fields_changed.length
    ? row.case_fields_changed
    : row.change_type === 'added' || row.change_type === 'removed'
      ? ['title', 'type', 'suite_name', 'section_path']
      : []
}

function isRichField(field) {
  return ['description', 'preconditions', 'steps', 'expected_results'].includes(field)
}

function safeMarkup(value) {
  return sanitizeHtml(value || '')
}

function displayValue(value) {
  if (value === null || value === undefined || value === '') return '—'
  if (Array.isArray(value)) return value.map((item) => typeof item === 'object' ? item.name || JSON.stringify(item) : item).join(', ')
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

function changeColor(value) {
  return { added: 'success', removed: 'error', changed: 'warning', inconclusive: 'info' }[value]
}

function sourceLabel(source) {
  const kind = source?.type || 'legacy_unknown'
  return `${source?.name || 'Unknown source'} (${kind})`
}

function formatDate(value) {
  if (!value) return 'Completion date unavailable'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? 'Completion date unavailable' : date.toLocaleString()
}

function formatDuration(value) {
  if (value === null || value === undefined) return 'Not measured'
  if (value === 0) return '0s'
  return `${value}s`
}
</script>

<style scoped>
.run-comparison__selectors,
.run-comparison__columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.run-comparison__side {
  min-width: 0;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 8px;
  padding: 16px;
}

.run-comparison__field + .run-comparison__field {
  margin-top: 12px;
}

.run-comparison__rich {
  overflow-wrap: anywhere;
}

.run-comparison__rich :deep(img) {
  max-width: 100%;
  height: auto;
}
</style>
