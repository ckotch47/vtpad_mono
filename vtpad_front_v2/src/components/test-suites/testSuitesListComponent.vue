<template>
  <div class="suite-navigation">
    <div class="suite-navigation__toolbar">
      <v-text-field
        v-model="search"
        prepend-inner-icon="mdi-magnify"
        label="Search suites"
        density="compact"
        hide-details
        variant="solo"
        clearable
        aria-label="Search test suites"
        @update:model-value="onSearch"
      />
      <v-select
        v-model="filterStatus"
        :items="statusOptions"
        item-title="title"
        item-value="value"
        label="Status"
        density="compact"
        hide-details
        variant="solo"
        aria-label="Filter test suites by status"
        @update:model-value="onFilterChange"
      />
      <v-select
        v-model="sortSelection"
        :items="sortOptions"
        item-title="title"
        item-value="value"
        label="Sort"
        density="compact"
        hide-details
        variant="solo"
        aria-label="Sort test suites"
      />
      <v-btn color="primary" prepend-icon="mdi-plus" block @click="openCreate = true">
        New Test Suite
      </v-btn>
    </div>

    <nav class="suite-navigation__list" aria-label="Test suites" :aria-busy="tableLoading">
      <v-progress-linear v-if="tableLoading" color="primary" indeterminate />
      <v-alert v-else-if="loadError" type="error" variant="tonal" density="compact" class="ma-3">
        {{ loadError }}
        <template #append>
          <v-btn size="small" variant="text" @click="loadSuites()">Retry</v-btn>
        </template>
      </v-alert>
      <v-list v-else-if="suites.length" nav density="compact" class="suite-navigation__items">
        <v-list-item
          v-for="item in suites"
          :key="item.id"
          :to="suiteRoute(item.id)"
          :active="String(route.params.suiteId || '') === String(item.id)"
          active-color="primary"
          rounded="lg"
          class="suite-navigation__item"
          :aria-label="`${item.name}, ${item.cases_count || 0} cases, ${item.status || 'active'}`"
        >
          <template #prepend>
            <v-icon :color="item.status === 'archived' ? 'grey' : 'primary'" size="small">
              {{ item.status === 'archived' ? 'mdi-archive-outline' : 'mdi-folder-outline' }}
            </v-icon>
          </template>
          <v-list-item-title class="suite-navigation__title">
            {{ item.name }}
          </v-list-item-title>
          <v-list-item-subtitle class="suite-navigation__subtitle">
            <span>{{ item.cases_count || 0 }} cases</span>
            <span aria-hidden="true">·</span>
            <span>{{ item.sections_count || 0 }} sections</span>
          </v-list-item-subtitle>
          <template #append>
            <div class="suite-navigation__actions">
              <v-chip
                size="x-small"
                :color="item.status === 'archived' ? 'grey' : 'success'"
                variant="tonal"
              >
                {{ item.status || 'active' }}
              </v-chip>
              <v-btn
                icon="mdi-pencil"
                size="x-small"
                variant="text"
                :aria-label="`Edit ${item.name}`"
                @click.stop.prevent="editSuite(item)"
              />
              <v-btn
                icon="mdi-archive-outline"
                size="x-small"
                variant="text"
                :aria-label="`Archive ${item.name}`"
                @click.stop.prevent="deleteSuite(item)"
              />
            </div>
          </template>
        </v-list-item>
      </v-list>
      <v-empty-state
        v-else
        icon="mdi-folder-search-outline"
        :title="search || filterStatus ? 'No matching suites' : 'No test suites yet'"
        :text="search || filterStatus ? 'Try changing the search or status filter.' : 'Create a suite to start organizing test cases.'"
        class="suite-navigation__empty"
      />
    </nav>

    <div v-if="pageCount > 1" class="suite-navigation__pagination">
      <v-btn
        icon="mdi-chevron-left"
        size="small"
        variant="text"
        aria-label="Previous suites page"
        :disabled="page <= 1 || tableLoading"
        @click="changePage(page - 1)"
      />
      <span class="text-caption">{{ page }} / {{ pageCount }}</span>
      <v-btn
        icon="mdi-chevron-right"
        size="small"
        variant="text"
        aria-label="Next suites page"
        :disabled="page >= pageCount || tableLoading"
        @click="changePage(page + 1)"
      />
      <span class="text-caption text-medium-emphasis ml-auto">{{ totalSuites }} suites</span>
    </div>

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
          <v-btn color="primary" :disabled="!newSuite.name.trim()" @click="createSuite">Create</v-btn>
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
            :items="[{ title: 'Active', value: 'active' }, { title: 'Archived', value: 'archived' }]"
            item-title="title"
            item-value="value"
            label="Status"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="openEdit = false">Cancel</v-btn>
          <v-btn color="primary" :disabled="!editSuiteData.name.trim()" @click="saveSuite">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { testSuiteService } from '@/services'

const emit = defineEmits(['suite-changed'])

const route = useRoute()
const router = useRouter()
const spaceId = computed(() => route.params.spaceId)

const suites = ref([])
const totalSuites = ref(0)
const page = ref(1)
const pageSize = ref(25)
const sortBy = ref([{ key: 'created_at', order: 'desc' }])
const tableLoading = ref(false)
const loadError = ref('')
const search = ref('')
const filterStatus = ref('')
const searchDebounce = ref(null)
const optionsDebounce = ref(null)
const requestId = ref(0)
const openCreate = ref(false)
const openEdit = ref(false)
const newSuite = ref({ name: '', description: '' })
const editSuiteData = ref({ id: null, name: '', description: '', status: 'active' })

const pageCount = computed(() => Math.max(1, Math.ceil(totalSuites.value / pageSize.value)))
const sortSelection = computed({
  get: () => {
    const sort = sortBy.value[0] || { key: 'created_at', order: 'desc' }
    return `${sort.key}:${sort.order}`
  },
  set: value => {
    const [key, order] = value.split(':')
    sortBy.value = [{ key, order }]
    loadSuites({ page: 1 })
  }
})
const statusOptions = [
  { title: 'Active suites', value: '' },
  { title: 'Archived', value: 'archived' },
  { title: 'All suites', value: 'all' }
]
const sortOptions = [
  { title: 'Recently created', value: 'created_at:desc' },
  { title: 'Oldest first', value: 'created_at:asc' },
  { title: 'Name A–Z', value: 'name:asc' },
  { title: 'Name Z–A', value: 'name:desc' }
]

function readRouteState() {
  const query = route.query
  page.value = Math.max(1, Number.parseInt(query.page, 10) || 1)
  pageSize.value = Math.max(1, Number.parseInt(query.page_size, 10) || 25)
  search.value = typeof query.search === 'string' ? query.search : ''
  filterStatus.value = typeof query.status === 'string' ? query.status : ''
  if (typeof query.sort_by === 'string' && typeof query.sort_order === 'string') {
    sortBy.value = [{ key: query.sort_by, order: query.sort_order }]
  } else {
    sortBy.value = [{ key: 'created_at', order: 'desc' }]
  }
}

function routeQueryForState() {
  const sort = sortBy.value[0] || { key: 'created_at', order: 'desc' }
  const query = { page: String(page.value), page_size: String(pageSize.value) }
  if (search.value) query.search = search.value
  if (filterStatus.value) query.status = filterStatus.value
  if (sort.key !== 'created_at' || sort.order !== 'desc') {
    query.sort_by = sort.key
    query.sort_order = sort.order
  }
  return query
}

function sameQuery(left, right) {
  const keys = new Set([...Object.keys(left), ...Object.keys(right)])
  return [...keys].every(key => String(left[key] ?? '') === String(right[key] ?? ''))
}

function syncRouteQuery() {
  const query = routeQueryForState()
  if (!sameQuery(route.query, query)) router.replace({ query })
}

function loadSuites(options = {}) {
  clearTimeout(optionsDebounce.value)
  optionsDebounce.value = setTimeout(() => doLoadSuites(options), 120)
}

function doLoadSuites(options = {}) {
  if (!spaceId.value) return
  const currentRequest = ++requestId.value
  page.value = Math.max(1, options.page || page.value)
  pageSize.value = Math.max(1, options.itemsPerPage || pageSize.value)
  if (options.sortBy?.[0]) sortBy.value = options.sortBy
  syncRouteQuery()
  tableLoading.value = true
  loadError.value = ''

  const sort = sortBy.value[0] || { key: 'created_at', order: 'desc' }
  testSuiteService.listBySpace(spaceId.value, {
    page: page.value,
    page_size: pageSize.value,
    sort_by: sort.key,
    sort_order: sort.order,
    search: search.value || undefined,
    status: filterStatus.value || undefined
  }).then(res => {
    if (currentRequest !== requestId.value) return
    suites.value = res.data.items || res.data
    totalSuites.value = res.data.total !== undefined ? res.data.total : (res.data.length || 0)
    pageSize.value = res.data.page_size || pageSize.value
  }).catch(() => {
    if (currentRequest === requestId.value) {
      loadError.value = 'Could not load test suites.'
      suites.value = []
      totalSuites.value = 0
    }
  }).finally(() => {
    if (currentRequest === requestId.value) tableLoading.value = false
  })
}

function onSearch() {
  clearTimeout(searchDebounce.value)
  searchDebounce.value = setTimeout(() => loadSuites({ page: 1 }), 350)
}

function onFilterChange() {
  loadSuites({ page: 1 })
}

function changePage(nextPage) {
  loadSuites({ page: nextPage })
}

function suiteRoute(id) {
  return { path: `/space/${spaceId.value}/test-suites/${id}`, query: route.query }
}

function createSuite() {
  testSuiteService.create({
    name: newSuite.value.name.trim(),
    description: newSuite.value.description,
    space_id: spaceId.value
  }).then(() => {
    openCreate.value = false
    newSuite.value = { name: '', description: '' }
    loadSuites({ page: 1 })
  })
}

function editSuite(item) {
  editSuiteData.value = {
    id: item.id,
    name: item.name || '',
    description: item.description || '',
    status: item.status || 'active'
  }
  openEdit.value = true
}

function saveSuite() {
  testSuiteService.update(editSuiteData.value.id, {
    name: editSuiteData.value.name.trim(),
    description: editSuiteData.value.description,
    status: editSuiteData.value.status
  }).then(() => {
    openEdit.value = false
    emit('suite-changed')
    loadSuites()
  })
}

function deleteSuite(item) {
  if (!confirm(`Archive test suite "${item.name}"?`)) return
  testSuiteService.delete(item.id).then(() => {
    if (String(route.params.suiteId || '') === String(item.id)) {
      router.push({ path: `/space/${spaceId.value}/test-suites`, query: route.query })
    }
    emit('suite-changed')
    loadSuites()
  })
}

watch(() => route.query, (query, oldQuery) => {
  if (sameQuery(query, oldQuery || {})) return
  readRouteState()
  loadSuites()
}, { deep: true })

watch(spaceId, (nextSpaceId, oldSpaceId) => {
  if (nextSpaceId !== oldSpaceId) {
    clearTimeout(optionsDebounce.value)
    requestId.value += 1
    tableLoading.value = false
    readRouteState()
    loadSuites()
  }
}, { immediate: true })

onBeforeUnmount(() => {
  clearTimeout(searchDebounce.value)
  clearTimeout(optionsDebounce.value)
  requestId.value += 1
})
</script>

<style scoped>
.suite-navigation {
  display: flex;
  flex-direction: column;
  min-height: 0;
  height: 100%;
}

.suite-navigation__toolbar {
  display: grid;
  gap: 10px;
  padding: 12px;
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.suite-navigation__list {
  min-height: 180px;
  overflow: auto;
  flex: 1;
}

.suite-navigation__items {
  padding: 8px;
}

.suite-navigation__item {
  margin-bottom: 4px;
  min-width: 0;
}

.suite-navigation__title,
.suite-navigation__subtitle {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.suite-navigation__subtitle {
  display: flex;
  gap: 5px;
}

.suite-navigation__actions {
  display: flex;
  align-items: center;
  gap: 2px;
}

.suite-navigation__empty {
  min-height: 220px;
}

.suite-navigation__pagination {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}
</style>
