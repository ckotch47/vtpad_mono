<template>
  <div>
    <v-toolbar density="compact">
      <v-text-field
        v-model="search"
        prepend-inner-icon="mdi-magnify"
        label="Search test runs"
        density="compact"
        hide-details
        variant="solo"
        class="mx-2"
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
      <template v-slot:item.status="{ item }">
        <v-icon :color="statusColor(item.status)">{{ statusIcon(item.status) }}</v-icon>
        <span class="ml-1 text-capitalize">{{ item.status }}</span>
      </template>
      <template v-slot:item.created_at="{ item }">
        {{ formatDate(item.created_at) }}
      </template>
      <template v-slot:item.actions="{ item }">
        <v-btn icon="mdi-delete" size="x-small" variant="text" color="error" @click.stop="deleteRun(item)" />
      </template>
    </v-data-table-server>

    <v-dialog v-model="openCreate" max-width="500">
      <v-card>
        <v-card-title>Create Test Run</v-card-title>
        <v-card-text>
          <v-text-field v-model="newRun.name" label="Name" required autofocus />
          <v-textarea v-model="newRun.description" label="Description" rows="2" />
          <v-select
            v-model="newRun.suite_id"
            :items="suites"
            item-title="name"
            item-value="id"
            label="Test Suite"
            required
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="openCreate = false">Cancel</v-btn>
          <v-btn color="primary" @click="createRun">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { testRunService, testSuiteService } from '@/services'

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
const newRun = ref({ name: '', description: '', suite_id: null })

const headers = [
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Status', key: 'status', width: '140px', sortable: true },
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
  newRun.value = { name: '', description: '', suite_id: null }
  loadSuites()
  openCreate.value = true
}

function loadSuites() {
  testSuiteService.listBySpace(spaceId.value, { page: 1, page_size: 100, status: 'active' }).then(res => {
    suites.value = res.data.items || []
  })
}

function createRun() {
  testRunService.create({
    name: newRun.value.name,
    description: newRun.value.description,
    suite_id: newRun.value.suite_id,
    space_id: spaceId.value
  }).then(() => {
    openCreate.value = false
    loadRuns({ page: 1, itemsPerPage: itemsPerPage.value, sortBy: [] })
  })
}

function deleteRun(item) {
  if (!confirm(`Delete test run "${item.name}"?`)) return
  testRunService.delete(item.id).then(() => {
    loadRuns({ page: page.value, itemsPerPage: itemsPerPage.value, sortBy: [] })
  })
}
</script>
