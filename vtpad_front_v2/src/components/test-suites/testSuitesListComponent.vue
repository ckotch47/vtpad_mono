<template>
  <div>
    <v-toolbar density="compact" class="list-toolbar">
      <v-text-field
        v-model="search"
        prepend-inner-icon="mdi-magnify"
        label="Search test suites"
        density="compact"
        hide-details
        variant="solo"
        class="mx-2 list-filter-search"
        clearable
        @update:model-value="onSearch"
      />
      <v-select
        v-model="filterStatus"
        :items="[{title:'All', value:''}, {title:'Active', value:'active'}, {title:'Archived', value:'archived'}]"
        item-title="title"
        item-value="value"
        label="Status"
        density="compact"
        hide-details
        variant="solo"
        class="mx-2 list-filter-sm"
        @update:model-value="onFilterChange"
      />
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate = true">
        New Test Suite
      </v-btn>
    </v-toolbar>

    <v-data-table-server
      v-model:items-per-page="itemsPerPage"
      v-model:page="page"
      :headers="headers"
      :items="suites"
      :items-length="totalSuites"
      :loading="tableLoading"
      :sort-by="sortBy"
      hover
      @update:options="loadSuites"
      @click:row="(event, { item }) => $router.push(`/space/${spaceId}/test-suites/${item.id}`)"
    >
      <template v-slot:item.name="{ item }">
        <div class="font-weight-medium">{{ item.name }}</div>
        <div v-if="item.description" class="text-caption text-medium-emphasis text-truncate" style="max-width: 400px">
          {{ item.description }}
        </div>
      </template>
      <template v-slot:item.cases_count="{ item }">
        <v-chip size="small" color="primary">{{ item.cases_count || 0 }}</v-chip>
      </template>
      <template v-slot:item.sections_count="{ item }">
        <v-chip size="small" color="info">{{ item.sections_count || 0 }}</v-chip>
      </template>
      <template v-slot:item.status="{ item }">
        <v-chip size="small" :color="item.status === 'archived' ? 'grey' : 'success'">{{ item.status }}</v-chip>
      </template>
      <template v-slot:item.created_at="{ item }">
        {{ formatDate(item.created_at) }}
      </template>
      <template v-slot:item.actions="{ item }">
        <v-btn icon="mdi-pencil" size="x-small" variant="text" @click.stop="editSuite(item)" />
        <v-btn icon="mdi-delete" size="x-small" variant="text" color="error" @click.stop="deleteSuite(item)" />
      </template>
    </v-data-table-server>

    <v-dialog v-model="openCreate" max-width="500">
      <v-card>
        <v-card-title>Create Test Suite</v-card-title>
        <v-card-text>
          <v-text-field v-model="newSuite.name" label="Name" required autofocus />
          <v-textarea v-model="newSuite.description" label="Description" rows="2" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="openCreate = false">Cancel</v-btn>
          <v-btn color="primary" @click="createSuite">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="openEdit" max-width="500">
      <v-card>
        <v-card-title>Edit Test Suite</v-card-title>
        <v-card-text>
          <v-text-field v-model="editSuiteData.name" label="Name" required autofocus />
          <v-textarea v-model="editSuiteData.description" label="Description" rows="2" />
          <v-select
            v-model="editSuiteData.status"
            :items="[{title:'Active', value:'active'}, {title:'Archived', value:'archived'}]"
            item-title="title"
            item-value="value"
            label="Status"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="openEdit = false">Cancel</v-btn>
          <v-btn color="primary" @click="saveSuite">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { testSuiteService } from '@/services'

const route = useRoute()
const router = useRouter()

const spaceId = computed(() => route.params.spaceId)

const suites = ref([])
const totalSuites = ref(0)
const page = ref(1)
const itemsPerPage = ref(25)
const sortBy = ref([{ key: 'created_at', order: 'desc' }])
const tableLoading = ref(false)
const firstLoad = ref(true)
const search = ref('')
const searchDebounce = ref(null)
const optionsDebounce = ref(null)
const openCreate = ref(false)
const openEdit = ref(false)
const newSuite = ref({ name: '', description: '' })
const editSuiteData = ref({ id: null, name: '', description: '', status: 'active' })
const filterStatus = ref('')

const headers = [
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Cases', key: 'cases_count', width: '100px', sortable: false },
  { title: 'Sections', key: 'sections_count', width: '100px', sortable: false },
  { title: 'Status', key: 'status', width: '100px', sortable: false },
  { title: 'Created', key: 'created_at', width: '150px', sortable: true },
  { title: 'Actions', key: 'actions', width: '120px', sortable: false }
]

const q = route.query
page.value = parseInt(q.page) || 1
itemsPerPage.value = parseInt(q.page_size) || 25
search.value = q.search || ''
filterStatus.value = q.status || ''
if (q.sort_by && q.sort_order) {
  sortBy.value = [{ key: q.sort_by, order: q.sort_order }]
}

function loadSuites(options) {
  clearTimeout(optionsDebounce.value)
  optionsDebounce.value = setTimeout(() => {
    doLoadSuites(options)
  }, 150)
}

function doLoadSuites(options) {
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
  if (filterStatus.value) query.status = filterStatus.value
  if (sortKey !== 'created_at' || sortOrder !== 'desc') {
    query.sort_by = sortKey
    query.sort_order = sortOrder
  }
  router.replace({ query })

  testSuiteService.listBySpace(spaceId.value, {
    page: p,
    page_size: pageSize,
    sort_by: sortKey,
    sort_order: sortOrder,
    search: search.value || undefined,
    status: filterStatus.value || undefined
  }).then(res => {
    suites.value = res.data.items || res.data
    totalSuites.value = res.data.total !== undefined ? res.data.total : (res.data.length || 0)
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
    loadSuites({ page: 1, itemsPerPage: itemsPerPage.value, sortBy: sortBy.value })
  }, 400)
}

function onFilterChange() {
  page.value = 1
  loadSuites({ page: 1, itemsPerPage: itemsPerPage.value, sortBy: sortBy.value })
}

function createSuite() {
  testSuiteService.create({
    name: newSuite.value.name,
    description: newSuite.value.description,
    space_id: spaceId.value
  }).then(() => {
    openCreate.value = false
    newSuite.value = { name: '', description: '' }
    loadSuites({ page: page.value, itemsPerPage: itemsPerPage.value, sortBy: sortBy.value })
  })
}

function editSuite(item) {
  editSuiteData.value = { ...item }
  openEdit.value = true
}

function saveSuite() {
  testSuiteService.update(editSuiteData.value.id, {
    name: editSuiteData.value.name,
    description: editSuiteData.value.description,
    status: editSuiteData.value.status
  }).then(() => {
    openEdit.value = false
    loadSuites({ page: page.value, itemsPerPage: itemsPerPage.value, sortBy: sortBy.value })
  })
}

function deleteSuite(item) {
  if (!confirm(`Archive test suite "${item.name}"?`)) return
  testSuiteService.delete(item.id).then(() => {
    loadSuites({ page: page.value, itemsPerPage: itemsPerPage.value, sortBy: sortBy.value })
  })
}

function formatDate(date) {
  return date ? new Date(date).toLocaleDateString() : ''
}
</script>

<style scoped>
.list-toolbar {
  gap: 8px;
}

.list-filter-search {
  max-width: 320px;
}

.list-filter-sm {
  max-width: 160px;
}
</style>
