<template>
  <div>
    <v-toolbar density="compact">
      <v-text-field
        v-model="search"
        prepend-inner-icon="mdi-magnify"
        label="Search test cases"
        density="compact"
        hide-details
        variant="solo"
        class="mx-2"
        clearable
        style="max-width: 260px"
        @update:model-value="onSearch"
      />
      <v-select
        v-model="filterType"
        :items="[{title:'All', value:''}, {title:'Manual', value:'manual'}, {title:'Checklist', value:'checklist'}, {title:'Automated', value:'automated'}]"
        item-title="title"
        item-value="value"
        label="Type"
        density="compact"
        hide-details
        variant="solo"
        class="mx-2"
        style="max-width: 140px"
        @update:model-value="onFilterChange"
      />
      <v-select
        v-model="filterStatus"
        :items="[{title:'All', value:''}, {title:'Draft', value:'draft'}, {title:'Active', value:'active'}, {title:'Deprecated', value:'deprecated'}]"
        item-title="title"
        item-value="value"
        label="Status"
        density="compact"
        hide-details
        variant="solo"
        class="mx-2"
        style="max-width: 140px"
        @update:model-value="onFilterChange"
      />
      <v-spacer />
      <v-btn v-if="selectedCases.length" size="small" variant="text" color="error" class="mr-2" @click="bulkDelete">
        Delete ({{ selectedCases.length }})
      </v-btn>
      <v-btn v-if="selectedCases.length" size="small" variant="text" class="mr-2" @click="bulkStatusDialog = true">
        Change Status ({{ selectedCases.length }})
      </v-btn>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate = true">
        New Test Case
      </v-btn>
    </v-toolbar>

    <v-data-table-server
      v-model="selectedCases"
      v-model:items-per-page="itemsPerPage"
      v-model:page="page"
      :headers="headers"
      :items="cases"
      :items-length="totalCases"
      :loading="tableLoading"
      :sort-by="sortBy"
      hover
      show-select
      item-value="id"
      @update:options="loadCases"
      @click:row="(event, { item }) => $router.push(`/space/${spaceId}/test-cases/${item.id}`)"
    >
      <template v-slot:item.type="{ item }">
        <v-chip size="small" :color="typeColor(item.type)">{{ item.type }}</v-chip>
      </template>
      <template v-slot:item.status="{ item }">
        <v-chip size="small" :color="statusColor(item.status)">{{ item.status }}</v-chip>
      </template>
      <template v-slot:item.updated_at="{ item }">
        {{ formatDate(item.updated_at) }}
      </template>
      <template v-slot:item.actions="{ item }">
        <v-btn icon size="x-small" variant="text" @click.stop="duplicateCase(item.id)">
          <v-icon>mdi-content-copy</v-icon>
        </v-btn>
      </template>
    </v-data-table-server>

    <v-dialog v-model="openCreate" max-width="700">
      <v-card>
        <v-card-title>Create Test Case</v-card-title>
        <v-card-text>
          <v-text-field v-model="newCase.title" label="Title" required />
          <v-select v-model="newCase.type" :items="['manual','checklist','automated']" label="Type" />
          <v-textarea v-model="newCase.steps" label="Steps" rows="4" />
          <v-textarea v-model="newCase.expected_results" label="Expected Results" rows="3" />
          <v-textarea v-model="newCase.preconditions" label="Preconditions" rows="2" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="openCreate = false" :disabled="creating">Cancel</v-btn>
          <v-btn color="primary" @click="createCase" :loading="creating" :disabled="creating">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="bulkStatusDialog" max-width="300">
      <v-card>
        <v-card-title>Change Status</v-card-title>
        <v-card-text>
          <v-select v-model="bulkStatus" :items="['draft','active','deprecated']" label="New Status" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="bulkStatusDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="bulkChangeStatus">Apply</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { testCaseService } from '@/services'

const route = useRoute()
const router = useRouter()

const spaceId = computed(() => route.params.spaceId)

const cases = ref([])
const totalCases = ref(0)
const page = ref(1)
const itemsPerPage = ref(25)
const sortBy = ref([{ key: 'created_at', order: 'desc' }])
const tableLoading = ref(false)
const creating = ref(false)
const firstLoad = ref(true)
const search = ref('')
const filterType = ref('')
const filterStatus = ref('')
const searchDebounce = ref(null)
const optionsDebounce = ref(null)
const openCreate = ref(false)
const newCase = ref({ title: '', type: 'manual', steps: '', expected_results: '', preconditions: '' })
const selectedCases = ref([])
const bulkStatusDialog = ref(false)
const bulkStatus = ref('active')

const headers = [
  { title: 'Title', key: 'title', sortable: true },
  { title: 'Type', key: 'type', width: '120px', sortable: true },
  { title: 'Status', key: 'status', width: '120px', sortable: true },
  { title: 'Short Name', key: 'short_name', sortable: true },
  { title: 'Updated', key: 'updated_at', width: '150px', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end', width: '100px' }
]

const q = route.query
page.value = parseInt(q.page) || 1
itemsPerPage.value = parseInt(q.page_size) || 25
search.value = q.search || ''
filterType.value = q.type || ''
filterStatus.value = q.status || ''
if (q.sort_by && q.sort_order) {
  sortBy.value = [{ key: q.sort_by, order: q.sort_order }]
}

function loadCases(options) {
  clearTimeout(optionsDebounce.value)
  optionsDebounce.value = setTimeout(() => {
    doLoadCases(options)
  }, 150)
}

function doLoadCases(options) {
  if (!spaceId.value || tableLoading.value) return
  tableLoading.value = true
  const p = firstLoad.value ? page.value : (options?.page || page.value)
  const pageSize = firstLoad.value ? itemsPerPage.value : (options?.itemsPerPage || itemsPerPage.value)
  firstLoad.value = false
  const sb = options?.sortBy?.[0]
  const sortKey = sb?.key || 'created_at'
  const sortOrder = sb?.order || 'desc'

  const query = { page: p, page_size: pageSize }
  if (search.value) query.search = search.value
  if (filterType.value) query.type = filterType.value
  if (filterStatus.value) query.status = filterStatus.value
  if (sortKey !== 'created_at' || sortOrder !== 'desc') {
    query.sort_by = sortKey
    query.sort_order = sortOrder
  }
  router.replace({ query })

  testCaseService.listBySpace(spaceId.value, {
    page: p,
    page_size: pageSize,
    sort_by: sortKey,
    sort_order: sortOrder,
    search: search.value || undefined,
    type: filterType.value || undefined,
    status: filterStatus.value || undefined
  }).then(res => {
    cases.value = res.data.items || res.data
    totalCases.value = res.data.total !== undefined ? res.data.total : (res.data.length || 0)
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
    loadCases({ page: 1, itemsPerPage: itemsPerPage.value, sortBy: sortBy.value })
  }, 400)
}

function onFilterChange() {
  page.value = 1
  loadCases({ page: 1, itemsPerPage: itemsPerPage.value, sortBy: sortBy.value })
}

function createCase() {
  creating.value = true
  testCaseService.create({
    ...newCase.value,
    space_id: spaceId.value
  }).then(() => {
    openCreate.value = false
    newCase.value = { title: '', type: 'manual', steps: '', expected_results: '', preconditions: '' }
    loadCases({ page: page.value, itemsPerPage: itemsPerPage.value, sortBy: sortBy.value })
  }).finally(() => {
    creating.value = false
  })
}

function bulkDelete() {
  if (!confirm(`Delete ${selectedCases.value.length} test cases?`)) return
  Promise.all(selectedCases.value.map(id => testCaseService.delete(id)))
    .then(() => {
      selectedCases.value = []
      loadCases({ page: page.value, itemsPerPage: itemsPerPage.value, sortBy: sortBy.value })
    })
}

function bulkChangeStatus() {
  Promise.all(selectedCases.value.map(id =>
    testCaseService.update(id, { status: bulkStatus.value })
  )).then(() => {
    selectedCases.value = []
    bulkStatusDialog.value = false
    loadCases({ page: page.value, itemsPerPage: itemsPerPage.value, sortBy: sortBy.value })
  })
}

function duplicateCase(id) {
  testCaseService.duplicate(id).then(() => {
    loadCases({ page: page.value, itemsPerPage: itemsPerPage.value, sortBy: sortBy.value })
  })
}

function typeColor(type) {
  const map = { manual: 'primary', checklist: 'warning', automated: 'success' }
  return map[type] || 'grey'
}

function statusColor(status) {
  const map = { active: 'success', draft: 'grey', deprecated: 'error' }
  return map[status] || 'grey'
}

function formatDate(date) {
  return date ? new Date(date).toLocaleDateString() : ''
}
</script>
