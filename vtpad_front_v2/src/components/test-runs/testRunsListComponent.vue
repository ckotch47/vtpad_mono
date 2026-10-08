<template>
  <div>
    <v-toolbar density="compact" class="list-toolbar">
      <v-text-field
        v-model="search"
        prepend-inner-icon="mdi-magnify"
        label="Search test runs"
        density="compact"
        hide-details
        variant="solo"
        class="mx-2 list-filter-search"
        clearable
        @update:model-value="onSearch"
      />
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreateDialog">
        New Test Run
      </v-btn>
    </v-toolbar>

    <v-data-table-server
      v-model:items-per-page="itemsPerPage"
      :headers="headers"
      :items="runs"
      :items-length="totalRuns"
      :loading="tableLoading"
      :page="page"
      hover
      @update:options="loadRuns"
      @click:row="(event, { item }) => $router.push(`/space/${spaceId}/test-runs/${item.id}`)"
    >
      <template v-slot:[`item.status`]="{ item }">
        <v-chip size="small" :color="statusColor(item.status)">
          <v-icon start size="x-small">{{ statusIcon(item.status) }}</v-icon>
          <span class="text-capitalize">{{ item.status }}</span>
        </v-chip>
      </template>
      <template v-slot:[`item.created_by`]="{ item }">
        <div v-if="item.created_by?.username" class="creator-cell">
          <v-avatar color="grey" size="24">
            <span class="text-body-2">{{ item.created_by.username[0]?.toUpperCase() }}</span>
          </v-avatar>
          <span>{{ item.created_by.username }}</span>
        </div>
        <span v-else class="text-medium-emphasis">—</span>
      </template>
      <template v-slot:[`item.created_at`]="{ item }">
        {{ formatDate(item.created_at) }}
      </template>
      <template v-slot:[`item.actions`]="{ item }">
        <v-btn icon="mdi-delete" size="x-small" variant="text" color="error" @click.stop="deleteRun(item)" />
      </template>
    </v-data-table-server>

    <v-dialog v-model="openCreate" max-width="760">
      <v-card
        data-keyboard-save-scope
        :data-keyboard-escape-confirm="isCreateDirty ? 'Discard unsaved test run changes?' : null"
        :data-keyboard-escape-saving="creating ? 'true' : null"
      >
        <v-card-title>Create Test Run</v-card-title>
        <v-card-text>
          <v-text-field v-model="newRun.name" label="Name" required autofocus />
          <v-textarea v-model="newRun.description" label="Description" rows="2" />
          <v-btn-toggle v-model="newRun.sourceType" mandatory divided color="primary" class="mb-4">
            <v-btn value="suite">Suite</v-btn>
            <v-btn value="plan">Plan</v-btn>
            <v-btn value="cases">Selected cases</v-btn>
          </v-btn-toggle>
          <v-select
            v-if="newRun.sourceType === 'suite'"
            v-model="newRun.suite_id"
            :items="suites"
            item-title="name"
            item-value="id"
            label="Test Suite"
            required
          />
          <v-select
            v-if="newRun.sourceType === 'plan'"
            v-model="newRun.plan_id"
            :items="plans"
            item-title="name"
            item-value="id"
            label="Test Plan"
            required
          />
          <v-autocomplete
            v-if="newRun.sourceType === 'cases'"
            v-model="newRun.testcase_ids"
            :items="cases"
            item-title="title"
            item-value="id"
            label="Test cases"
            multiple
            chips
            closable-chips
          />
          <v-row>
            <v-col cols="12" md="6">
              <v-select v-model="newRun.milestone_id" :items="milestones" item-title="title" item-value="id" label="Milestone" clearable />
            </v-col>
            <v-col cols="12" md="6">
              <v-select v-model="newRun.environment_id" :items="environments" item-title="name" item-value="id" label="Environment" clearable />
            </v-col>
          </v-row>
          <v-alert v-if="previewError" type="info" variant="tonal" density="compact" class="mb-2">
            Preview is unavailable on this server. The selected source will be validated when the draft run is created.
          </v-alert>
          <v-alert v-else-if="preview" type="info" variant="tonal" density="compact" class="mb-2">
            This run will include <strong>{{ preview.case_count ?? preview.total ?? preview.testcases?.length ?? 0 }}</strong> test cases.
          </v-alert>
          <v-alert v-if="createError" type="error" variant="tonal" density="compact" class="mb-2">{{ createError }}</v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="openCreate = false">Cancel</v-btn>
          <v-btn variant="text" :loading="previewLoading" @click="loadPreview">Preview</v-btn>
          <v-btn color="primary" data-keyboard-save-action :disabled="!hasSource || creating" :loading="creating" @click="createRun">Create draft</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { testRunService, testSuiteService, testPlanService, testCaseService, milestoneService, environmentService } from '@/services'

const route = useRoute()
const spaceId = computed(() => route.params.spaceId)

const runs = ref([])
const totalRuns = ref(0)
const page = ref(1)
const itemsPerPage = ref(25)
const tableLoading = ref(false)
const firstLoad = ref(true)
const search = ref('')
const searchDebounce = ref(null)
const optionsDebounce = ref(null)
const openCreate = ref(false)
const suites = ref([])
const plans = ref([])
const cases = ref([])
const milestones = ref([])
const environments = ref([])
const preview = ref(null)
const previewError = ref(false)
const previewLoading = ref(false)
const creating = ref(false)
const createError = ref('')
const newRun = ref(emptyRun())
const isCreateDirty = computed(() => JSON.stringify(newRun.value) !== JSON.stringify(emptyRun()))

const hasSource = computed(() => {
  if (newRun.value.sourceType === 'suite') return Boolean(newRun.value.suite_id)
  if (newRun.value.sourceType === 'plan') return Boolean(newRun.value.plan_id)
  return newRun.value.testcase_ids.length > 0
})

function emptyRun() {
  return { name: '', description: '', sourceType: 'suite', suite_id: null, plan_id: null, testcase_ids: [], milestone_id: null, environment_id: null }
}

const headers = [
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Status', key: 'status', width: '140px', sortable: true },
  { title: 'Create', key: 'created_by', width: '180px', sortable: false },
  { title: 'Created', key: 'created_at', width: '150px', sortable: true },
  { title: 'Actions', key: 'actions', width: '100px', sortable: false }
]

function loadRuns(options) {
  clearTimeout(optionsDebounce.value)
  optionsDebounce.value = setTimeout(() => {
    doLoadRuns(options)
  }, 150)
}

function doLoadRuns(options) {
  if (!spaceId.value || tableLoading.value) return
  tableLoading.value = true
  const p = firstLoad.value ? page.value : (options?.page || page.value)
  const pageSize = firstLoad.value ? itemsPerPage.value : (options?.itemsPerPage || itemsPerPage.value)
  firstLoad.value = false
  const sortBy = options?.sortBy?.[0]
  const sortKey = sortBy?.key || 'created_at'
  const sortOrder = sortBy?.order || 'desc'

  testRunService.listBySpace(spaceId.value, {
    page: p,
    page_size: pageSize,
    sort_by: sortKey,
    sort_order: sortOrder,
    search: search.value || undefined
  }).then(res => {
    runs.value = res.data.items || res.data
    totalRuns.value = res.data.total !== undefined ? res.data.total : (res.data.length || 0)
    itemsPerPage.value = res.data.page_size || itemsPerPage.value
    tableLoading.value = false
  }).catch(() => {
    tableLoading.value = false
  })
}

function onSearch() {
  clearTimeout(searchDebounce.value)
  searchDebounce.value = setTimeout(() => {
    page.value = 1
    loadRuns({ page: 1, itemsPerPage: itemsPerPage.value, sortBy: [] })
  }, 400)
}

function statusColor(status) {
  const map = { completed: 'success', active: 'primary', draft: 'grey' }
  return map[status] || 'grey'
}

function statusIcon(status) {
  const map = { completed: 'mdi-check-circle', active: 'mdi-play-circle', draft: 'mdi-circle-outline' }
  return map[status] || 'mdi-circle-outline'
}

function formatDate(date) {
  return date ? new Date(date).toLocaleDateString() : ''
}

function openCreateDialog() {
  newRun.value = emptyRun()
  preview.value = null
  previewError.value = false
  createError.value = ''
  loadCreateSources()
  openCreate.value = true
}

function loadCreateSources() {
  testSuiteService.listBySpace(spaceId.value, { page: 1, page_size: 100, status: 'active' }).then(res => { suites.value = res.data.items || [] })
  testPlanService.listBySpace(spaceId.value, { page: 1, page_size: 100 }).then(res => { plans.value = res.data.items || [] })
  testCaseService.listBySpace(spaceId.value, { page: 1, page_size: 500 }).then(res => { cases.value = res.data.items || res.data || [] })
  milestoneService.list(spaceId.value).then(res => { milestones.value = res.data.items || res.data || [] })
  environmentService.list(spaceId.value).then(res => { environments.value = res.data.items || res.data || [] })
}

function payload(includeSourceHash = false) {
  return {
    name: newRun.value.name.trim() || 'Untitled test run', description: newRun.value.description || null,
    space_id: spaceId.value,
    suite_id: newRun.value.sourceType === 'suite' ? newRun.value.suite_id : null,
    plan_id: newRun.value.sourceType === 'plan' ? newRun.value.plan_id : null,
    testcase_ids: newRun.value.sourceType === 'cases' ? newRun.value.testcase_ids : null,
    milestone_id: newRun.value.milestone_id || null, environment_id: newRun.value.environment_id || null,
    ...(includeSourceHash && preview.value?.source_hash ? { source_hash: preview.value.source_hash } : {}),
  }
}

async function loadPreview() {
  if (!hasSource.value) return
  previewLoading.value = true
  previewError.value = false
  try { preview.value = (await testRunService.preview(payload())).data } catch (_) { preview.value = null; previewError.value = true } finally { previewLoading.value = false }
}

async function createRun() {
  if (creating.value) return
  creating.value = true
  createError.value = ''
  try {
    await testRunService.create(payload(true))
    openCreate.value = false
    loadRuns({ page: 1, itemsPerPage: itemsPerPage.value, sortBy: [] })
  } catch (error) {
    createError.value = error?.response?.data?.detail || 'Could not create the test run. Refresh the preview and try again.'
  } finally { creating.value = false }
}

function deleteRun(item) {
  if (!confirm(`Delete test run "${item.name}"?`)) return
  testRunService.delete(item.id).then(() => {
    loadRuns({ page: page.value, itemsPerPage: itemsPerPage.value, sortBy: [] })
  })
}
</script>

<style scoped>
.list-toolbar {
  gap: 8px;
}

.list-filter-search {
  max-width: 320px;
}

.creator-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.creator-cell span:last-child {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
