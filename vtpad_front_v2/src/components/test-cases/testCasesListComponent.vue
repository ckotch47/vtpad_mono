<template>
  <div>
    <list-page-toolbar layout="filters-actions">
      <template #filters>
        <div class="list-toolbar__filter-row">
          <v-text-field
            v-model="search"
            prepend-inner-icon="mdi-magnify"
            label="Search test cases"
            density="compact"
            hide-details
            :variant="mdAndUp ? 'outlined' : 'solo'"
            class="list-filter-search"
            clearable
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
            :variant="mdAndUp ? 'outlined' : 'solo'"
            class="list-filter-sm"
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
            :variant="mdAndUp ? 'outlined' : 'solo'"
            class="list-filter-sm"
            @update:model-value="onFilterChange"
          />
          <v-select
            v-model="filterPriority"
            :items="priorityOptions"
            item-title="title"
            item-value="value"
            label="Priority"
            density="compact"
            hide-details
            :variant="mdAndUp ? 'outlined' : 'solo'"
            class="list-filter-sm"
            @update:model-value="onFilterChange"
          />
        </div>
        <div class="list-toolbar__filter-row list-toolbar__filter-row--secondary">
          <v-select
            v-model="filterTags"
            :items="availableTagOptions"
            :loading="tagOptionsLoading"
            label="Tags (all)"
            multiple
            chips
            closable-chips
            density="compact"
            hide-details
            :variant="mdAndUp ? 'outlined' : 'solo'"
            class="list-filter-tags"
            @update:model-value="onFilterChange"
          />
          <v-tooltip v-if="tagOptionsError" text="Existing tags could not be loaded. Tag filtering may be incomplete.">
            <template #activator="{ props }">
              <v-icon v-bind="props" color="warning" aria-label="Tag options could not be loaded">mdi-alert-circle-outline</v-icon>
            </template>
          </v-tooltip>
          <v-tooltip v-if="suiteOptionsError" text="Existing suites could not be loaded. Suite filtering may be incomplete.">
            <template #activator="{ props }">
              <v-icon v-bind="props" color="warning" aria-label="Suite options could not be loaded">mdi-alert-circle-outline</v-icon>
            </template>
          </v-tooltip>
          <v-autocomplete
            v-model="filterSuite"
            :items="availableSuiteOptions"
            :loading="suiteOptionsLoading"
            item-title="title"
            item-value="value"
            label="Suite"
            density="compact"
            hide-details
            :variant="mdAndUp ? 'outlined' : 'solo'"
            class="list-filter-sm"
            @update:model-value="onFilterChange"
          />
        </div>
      </template>
      <template #actions>
        <div class="case-list-actions">
          <div v-if="canEditCases && selectedCases.length" class="case-list-actions__bulk">
            <v-btn size="small" variant="text" color="error" @click="bulkDelete">Delete ({{ selectedCases.length }})</v-btn>
            <v-btn size="small" variant="text" @click="bulkStatusDialog = true">Change Status ({{ selectedCases.length }})</v-btn>
          </div>
          <div class="case-list-actions__primary">
            <v-btn v-if="canEditCases" variant="outlined" @click="openTemplates = true">Case Templates</v-btn>
            <v-btn v-if="canEditCases" color="primary" prepend-icon="mdi-plus" @click="openCreate = true">New Test Case</v-btn>
          </div>
        </div>
      </template>
    </list-page-toolbar>

    <v-alert v-if="loadError" type="error" variant="tonal" density="compact" class="mb-3" role="alert">
      {{ loadErrorStatus === 403 ? 'You do not have permission to view test cases in this space.' : cases.length ? 'Test cases could not be refreshed. Existing results are still shown.' : 'Test cases could not be loaded.' }}
      <v-btn v-if="loadErrorStatus !== 403" size="small" variant="text" @click="loadCases({ page: page, itemsPerPage: itemsPerPage, sortBy: sortBy })">Retry</v-btn>
    </v-alert>

    <div class="list-loading-region" :aria-busy="initialLoading || tableLoading">
      <list-loading-skeleton
        v-if="initialLoading"
        class="list-loading-region__skeleton"
        variant="table"
        :columns="headers.length"
        label="test cases"
      />
      <v-data-table-server
      class="row-navigation-table"
      :class="{ 'list-loading-region__content--hidden': initialLoading || (loadError && !cases.length) }"
      v-model="selectedCases"
      v-model:items-per-page="itemsPerPage"
      v-model:page="page"
      :headers="headers"
      :items="cases"
      :items-length="totalCases"
      :loading="tableLoading"
      :sort-by="sortBy"
      hover
      :show-select="canEditCases"
      item-value="id"
      @update:options="loadCases"
    >
      <template #no-data>
        <contextual-empty-state
          v-if="hasCaseFilters"
          icon="mdi-filter-off-outline"
          title="No matching test cases"
          text="Change or clear the current search and filters."
          action-label="Clear filters"
          @action="clearCaseFilters"
        />
        <contextual-empty-state
          v-else
          icon="mdi-test-tube-empty"
          title="No test cases yet"
          text="Use New Test Case when you have permission to add cases to this space."
        />
      </template>
      <template v-slot:[`item.title`]="{ item }">
        <router-link class="list-row-link" :to="`/space/${spaceId}/test-cases/${item.id}`" :aria-label="`Open test case ${item.title}`">
          {{ item.title }}
        </router-link>
      </template>
      <template v-slot:[`item.type`]="{ item }">
        <v-chip size="small" :color="typeColor(item.type)">{{ item.type }}</v-chip>
      </template>
      <template v-slot:[`item.status`]="{ item }">
        <v-chip size="small" :color="statusColor(item.status)">{{ item.status }}</v-chip>
      </template>
      <template v-slot:[`item.priority`]="{ item }">
        <v-chip size="small" :color="priorityColor(item.priority)">{{ priorityLabel(item.priority) }}</v-chip>
      </template>
      <template v-slot:[`item.tags`]="{ item }">
        <div class="d-flex flex-wrap ga-1">
          <v-chip v-for="tag in item.tags || []" :key="tag" size="x-small" variant="tonal">{{ tag }}</v-chip>
          <span v-if="!item.tags?.length" class="text-medium-emphasis">—</span>
        </div>
      </template>
      <template v-slot:[`item.short_name`]="{ item }">
        <v-tooltip v-if="item.short_name" :text="item.short_name" location="top">
          <template #activator="{ props }">
            <span v-bind="props" class="short-name-cell">{{ item.short_name }}</span>
          </template>
        </v-tooltip>
        <span v-else class="text-medium-emphasis">—</span>
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
      <template v-slot:[`item.updated_at`]="{ item }">
        {{ formatDate(item.updated_at) }}
      </template>
      <template v-if="canEditCases" v-slot:[`item.actions`]="{ item }">
        <v-btn icon size="x-small" variant="text" :aria-label="`Duplicate ${item.title}`" :title="`Duplicate ${item.title}`" @click.stop="duplicateCase(item.id)">
          <v-icon>mdi-content-copy</v-icon>
        </v-btn>
      </template>
      </v-data-table-server>
    </div>

    <case-templates-dialog v-model="openTemplates" :space-id="String(spaceId)" />

    <v-dialog v-model="openCreate" max-width="900">
      <v-card
        data-keyboard-save-scope
        :data-keyboard-escape-confirm="isCreateDirty ? 'Discard unsaved test case changes?' : null"
        :data-keyboard-escape-saving="creating ? 'true' : null"
      >
        <v-card-title>Create Test Case</v-card-title>
        <v-card-text>
          <v-alert v-if="createError" type="error" variant="tonal" density="compact" class="mb-4" role="alert">
            The test case could not be created. Check the fields and try again.
          </v-alert>
          <v-select
            v-if="caseTemplates.length"
            v-model="selectedTemplateId"
            :items="caseTemplates"
            item-title="name"
            item-value="id"
            label="Start from a template (optional)"
            :loading="loadingCaseTemplates || applyingTemplate"
            :disabled="loadingCaseTemplates || applyingTemplate"
            hint="Template content is copied into this draft and can be edited before creating the case."
            persistent-hint
            @update:model-value="applyCaseTemplate"
          />
          <v-alert v-if="caseTemplateLoadError || templateApplyError" type="warning" variant="tonal" density="compact" class="mb-3" role="alert">
            Case templates could not be loaded.
            <v-btn v-if="templateApplyError && selectedTemplateId" size="small" variant="text" @click="applyCaseTemplate(selectedTemplateId)">Retry</v-btn>
            <v-btn v-else size="small" variant="text" @click="loadCaseTemplates">Retry</v-btn>
          </v-alert>
          <v-alert v-else-if="!loadingCaseTemplates && !caseTemplates.length" type="info" variant="tonal" density="compact" class="mb-3">
            No templates are available in this space. You can create one with Case Templates.
          </v-alert>
          <v-alert v-if="appliedTemplate" type="info" variant="tonal" density="compact" class="mb-3">
            Copied “{{ appliedTemplate.name }}” version {{ appliedTemplate.version }}. Review or change these values; this draft is independent of the template.
          </v-alert>
          <v-text-field v-model="newCase.title" label="Title" required @update:model-value="caseTitleTouched = true" />
          <v-select v-model="newCase.type" :items="['manual','checklist','automated']" label="Type" />
          <v-row>
            <v-col cols="4">
              <v-select v-model="newCase.priority" :items="priorityOptions" item-title="title" item-value="value" label="Priority" />
            </v-col>
            <v-col cols="8">
              <v-combobox v-if="canEditTags" v-model="newCase.tags" :items="tagOptions" :loading="tagOptionsLoading" label="Tags" multiple chips closable-chips clearable hint="Choose an existing tag or enter a new one" persistent-hint />
              <div v-if="canEditTags && tagOptionsError" class="text-caption text-warning">Existing tags could not be loaded. You can still enter tag labels.</div>
            </v-col>
          </v-row>
          <v-text-field
            v-model="newCase.estimated_duration_seconds"
            label="Estimated duration (seconds)"
            type="number"
            min="0"
            step="1"
            clearable
            :rules="[nonNegativeIntegerRule]"
            hint="Leave empty when no estimate is available. Zero is a valid estimate."
            persistent-hint
          />
          <div class="text-subtitle-1 mb-2">Description</div>
          <editor-component
            :text="newCase.text"
            :edit="true"
            :show-menu-fixed="true"
            accessible-label="Description"
            place-holder-editor="Describe the test..."
            @editor-update="newCase.text = $event"
          />
          <template v-if="newCase.type === 'checklist'">
            <div class="text-subtitle-1 mt-4 mb-2">Checks</div>
            <editor-component
              :text="newCase.steps"
              :edit="true"
              :show-menu-fixed="true"
              accessible-label="Checks"
              place-holder-editor="Add checks, one per list item..."
              @editor-update="newCase.steps = $event"
            />
            <div class="text-caption text-medium-emphasis mt-2">The run records one result for the whole checklist.</div>
          </template>
          <template v-else>
            <div class="text-subtitle-1 mt-4 mb-2">Preconditions</div>
            <editor-component
              :text="newCase.preconditions"
              :edit="true"
              :show-menu-fixed="true"
              accessible-label="Preconditions"
              place-holder-editor="Enter preconditions..."
              @editor-update="newCase.preconditions = $event"
            />
            <div class="text-subtitle-1 mt-4 mb-2">Steps</div>
            <editor-component
              :text="newCase.steps"
              :edit="true"
              :show-menu-fixed="true"
              accessible-label="Steps"
              place-holder-editor="Enter steps..."
              @editor-update="newCase.steps = $event"
            />
            <div class="text-subtitle-1 mt-4 mb-2">Expected Results</div>
            <editor-component
              :text="newCase.expected_results"
              :edit="true"
              :show-menu-fixed="true"
              accessible-label="Expected Results"
              place-holder-editor="Enter expected results..."
              @editor-update="newCase.expected_results = $event"
            />
            <div class="text-subtitle-1 mt-4 mb-2">Postconditions</div>
            <editor-component
              :text="newCase.postconditions"
              :edit="true"
              :show-menu-fixed="true"
              accessible-label="Postconditions"
              place-holder-editor="Enter postconditions..."
              @editor-update="newCase.postconditions = $event"
            />
          </template>
          <custom-field-values-component
            ref="createCustomFieldForm"
            v-model="newCase.custom_fields"
            :space-id="spaceId"
            entity-type="testcase"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="openCreate = false" :disabled="creating">Cancel</v-btn>
          <v-btn color="primary" data-keyboard-save-action @click="createCase" :loading="creating" :disabled="creating || applyingTemplate || createCustomFieldForm?.loading">Create</v-btn>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDisplay } from 'vuetify'
import { testCaseService, testCaseTemplateService, testSuiteService } from '@/services'
import EditorComponent from '@/components/common/editor/editorComponent.vue'
import CustomFieldValuesComponent from '@/components/custom-fields/customFieldValuesComponent.vue'
import ListLoadingSkeleton from '@/components/common/ListLoadingSkeleton.vue'
import ListPageToolbar from '@/components/common/ListPageToolbar.vue'
import CaseTemplatesDialog from '@/components/test-cases/CaseTemplatesDialog.vue'
import { useSpaceCapabilitiesStore } from '@/stores/spaceCapabilities'

const route = useRoute()
const router = useRouter()
const { mdAndUp } = useDisplay()

const spaceId = computed(() => route.params.spaceId)
const capabilityStore = useSpaceCapabilitiesStore()
const canEditCases = computed(() => capabilityStore.can(spaceId.value, 'cases'))
const canEditTags = computed(() => capabilityStore.can(spaceId.value, 'tags'))

const cases = ref([])
const totalCases = ref(0)
const page = ref(1)
const itemsPerPage = ref(25)
const sortBy = ref([{ key: 'created_at', order: 'desc' }])
const tableLoading = ref(false)
const hasLoaded = ref(false)
const initialLoading = computed(() => Boolean(spaceId.value) && !hasLoaded.value)
const creating = ref(false)
const createError = ref(false)
const firstLoad = ref(true)
const search = ref('')
const filterType = ref('')
const filterStatus = ref('')
const filterSuite = ref('')
const suiteOptions = ref([])
const suiteOptionsLoading = ref(false)
const suiteOptionsError = ref(false)
const priorityOptions = [
  { title: 'All priorities', value: '' },
  { title: 'P0 · Blocker', value: 'P0' },
  { title: 'P1 · High', value: 'P1' },
  { title: 'P2 · Normal', value: 'P2' },
  { title: 'P3 · Low', value: 'P3' }
]
const nonNegativeIntegerRule = value => value === '' || value === null || value === undefined ||
  (Number.isInteger(Number(value)) && Number(value) >= 0) || 'Enter a whole number greater than or equal to zero'
const filterPriority = ref('')
const filterTags = ref([])
const tagOptions = ref([])
const tagOptionsLoading = ref(false)
const tagOptionsError = ref(false)
const loadError = ref(false)
const loadErrorStatus = ref(0)
const hasCaseFilters = computed(() => Boolean(search.value || filterType.value || filterStatus.value || filterSuite.value || filterPriority.value || filterTags.value.length))
const availableTagOptions = computed(() => [...new Set([...tagOptions.value, ...filterTags.value])])
const availableSuiteOptions = computed(() => [
  { title: 'All Suites', value: '' },
  { title: 'No Suite', value: 'none' },
  ...suiteOptions.value.map(suite => ({ title: suite.name, value: String(suite.id) }))
])
const searchDebounce = ref(null)
const optionsDebounce = ref(null)
const openCreate = ref(false)
const openTemplates = ref(false)
const loadingCaseTemplates = ref(false)
const caseTemplateLoadError = ref(false)
const templateApplyError = ref(false)
const caseTemplates = ref([])
const selectedTemplateId = ref(null)
const applyingTemplate = ref(false)
const appliedTemplate = ref(null)
const caseTitleTouched = ref(false)
let templateSelectionRequestId = 0
let suiteOptionsRequestId = 0
let caseListRequestId = 0
const emptyCase = () => ({ title: '', type: 'manual', priority: 'P2', tags: [], text: '', steps: '', expected_results: '', preconditions: '', postconditions: '', estimated_duration_seconds: null, custom_fields: [] })
const newCase = ref(emptyCase())
const createCustomFieldForm = ref(null)
const isCreateDirty = computed(() => JSON.stringify(newCase.value) !== JSON.stringify(emptyCase()))
const selectedCases = ref([])
const bulkStatusDialog = ref(false)
const bulkStatus = ref('active')

const headers = [
  { title: 'Title', key: 'title', sortable: true },
  { title: 'Type', key: 'type', width: '120px', sortable: true },
  { title: 'Priority', key: 'priority', width: '125px', sortable: true },
  { title: 'Tags', key: 'tags', sortable: false },
  { title: 'Status', key: 'status', width: '120px', sortable: true },
  { title: 'Short Name', key: 'short_name', width: '150px', sortable: true },
  { title: 'Create', key: 'created_by', width: '180px', sortable: false },
  { title: 'Updated', key: 'updated_at', width: '105px', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end', width: '100px' }
]

const q = route.query
page.value = parseInt(q.page) || 1
itemsPerPage.value = parseInt(q.page_size) || 25
search.value = q.search || ''
filterType.value = q.type || ''
filterStatus.value = q.status || ''
filterSuite.value = q.suite_id || ''
filterPriority.value = q.priority || ''
filterTags.value = (Array.isArray(q.tags) ? q.tags : q.tags ? [q.tags] : []).map(String)
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
  if (!spaceId.value) return
  if (tableLoading.value) {
    clearTimeout(optionsDebounce.value)
    optionsDebounce.value = setTimeout(() => doLoadCases(options), 150)
    return
  }
  tableLoading.value = true
  loadError.value = false
  loadErrorStatus.value = 0
  const requestId = ++caseListRequestId
  const requestedSpaceId = String(spaceId.value)
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
  if (filterSuite.value) query.suite_id = filterSuite.value
  if (filterPriority.value) query.priority = filterPriority.value
  if (filterTags.value.length) query.tags = [...filterTags.value]
  if (sortKey !== 'created_at' || sortOrder !== 'desc') {
    query.sort_by = sortKey
    query.sort_order = sortOrder
  }
  router.replace({ query })

  testCaseService.listBySpace(requestedSpaceId, {
    page: p,
    page_size: pageSize,
    sort_by: sortKey,
    sort_order: sortOrder,
    search: search.value || undefined,
    type: filterType.value || undefined,
    status: filterStatus.value || undefined,
    suite_id: filterSuite.value || undefined,
    priority: filterPriority.value || undefined,
    tags: filterTags.value.length ? [...filterTags.value] : undefined
  }).then(res => {
    if (requestId !== caseListRequestId || requestedSpaceId !== String(spaceId.value)) return
    cases.value = res.data.items || res.data
    totalCases.value = res.data.total !== undefined ? res.data.total : (res.data.length || 0)
    itemsPerPage.value = res.data.page_size || itemsPerPage.value
    hasLoaded.value = true
  }).catch((error) => {
    if (requestId !== caseListRequestId || requestedSpaceId !== String(spaceId.value)) return
    loadError.value = true
    loadErrorStatus.value = Number(error?.response?.status || 0)
    if (loadErrorStatus.value === 403) {
      cases.value = []
      totalCases.value = 0
    }
  }).finally(() => {
    if (requestId === caseListRequestId) {
      if (requestedSpaceId === String(spaceId.value)) hasLoaded.value = true
      tableLoading.value = false
    }
  })
}

async function loadTagOptions() {
  if (!spaceId.value) return
  tagOptionsLoading.value = true
  tagOptionsError.value = false
  try {
    const response = await testCaseService.listTagsBySpace(spaceId.value)
    const tags = Array.isArray(response.data) ? response.data : response.data?.items
    tagOptions.value = Array.isArray(tags) ? tags.filter(tag => typeof tag === 'string') : []
  } catch (_) {
    tagOptionsError.value = true
  } finally {
    tagOptionsLoading.value = false
  }
}

async function loadSuiteOptions() {
  const requestedSpaceId = String(spaceId.value || '')
  if (!requestedSpaceId || requestedSpaceId === 'undefined') return
  const requestId = ++suiteOptionsRequestId
  suiteOptions.value = []
  suiteOptionsLoading.value = true
  suiteOptionsError.value = false
  try {
    const response = await testSuiteService.listBySpace(requestedSpaceId, {
      page: 1,
      page_size: 1000,
      sort_by: 'name',
      sort_order: 'asc',
      status: 'all'
    })
    if (requestId !== suiteOptionsRequestId || requestedSpaceId !== String(spaceId.value)) return
    const firstPage = response.data || {}
    const suites = Array.isArray(firstPage) ? [...firstPage] : [...(firstPage.items || [])]
    const pageCount = Math.max(1, Number(firstPage.pages) || 1)
    for (let page = 2; page <= pageCount; page += 1) {
      if (requestId !== suiteOptionsRequestId || requestedSpaceId !== String(spaceId.value)) return
      const pageResponse = await testSuiteService.listBySpace(requestedSpaceId, {
        page,
        page_size: 1000,
        sort_by: 'name',
        sort_order: 'asc',
        status: 'all'
      })
      suites.push(...(pageResponse.data?.items || []))
    }
    if (requestId === suiteOptionsRequestId && requestedSpaceId === String(spaceId.value)) {
      suiteOptions.value = suites
    }
  } catch (_) {
    if (requestId === suiteOptionsRequestId && requestedSpaceId === String(spaceId.value)) {
      suiteOptionsError.value = true
    }
  } finally {
    if (requestId === suiteOptionsRequestId) suiteOptionsLoading.value = false
  }
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

function clearCaseFilters() {
  search.value = ''
  filterType.value = ''
  filterStatus.value = ''
  filterSuite.value = ''
  filterPriority.value = ''
  filterTags.value = []
  onFilterChange()
}

async function loadCaseTemplates() {
  if (!spaceId.value) return
  loadingCaseTemplates.value = true
  caseTemplateLoadError.value = false
  try {
    const response = await testCaseTemplateService.listBySpace(spaceId.value, { page: 1, page_size: 100 })
    caseTemplates.value = response.data?.items || []
  } catch (_) {
    caseTemplateLoadError.value = true
  } finally {
    loadingCaseTemplates.value = false
  }
}

async function applyCaseTemplate(templateId) {
  const requestId = ++templateSelectionRequestId
  selectedTemplateId.value = templateId || null
  templateApplyError.value = false
  appliedTemplate.value = null
  if (!templateId) {
    applyingTemplate.value = false
    return
  }
  applyingTemplate.value = true
  try {
    const response = await testCaseTemplateService.getById(spaceId.value, templateId)
    if (requestId !== templateSelectionRequestId) return
    const template = response.data
    const fields = template.fields || {}
    const title = caseTitleTouched.value ? newCase.value.title : (fields.title || '')
    newCase.value = {
      ...newCase.value,
      title,
      text: fields.text ?? '',
      preconditions: fields.preconditions ?? '',
      steps: fields.steps ?? '',
      expected_results: fields.expected_results ?? '',
      postconditions: fields.postconditions ?? '',
      type: fields.type || 'manual',
      priority: fields.priority || 'P2',
      estimated_duration_seconds: fields.estimated_duration_seconds ?? null
    }
    appliedTemplate.value = { name: template.name, version: template.current_version }
  } catch (_) {
    if (requestId === templateSelectionRequestId) templateApplyError.value = true
  } finally {
    if (requestId === templateSelectionRequestId) applyingTemplate.value = false
  }
}

async function createCase() {
  const validation = await createCustomFieldForm.value?.validate()
  if (validation && !validation.valid) return
  creating.value = true
  createError.value = false
  const estimatedDuration = newCase.value.estimated_duration_seconds
  testCaseService.create({
    ...newCase.value,
    priority: newCase.value.priority || 'P2',
    estimated_duration_seconds: estimatedDuration === '' || estimatedDuration === null || estimatedDuration === undefined
      ? null
      : Number(estimatedDuration),
    tags: normalizeTags(newCase.value.tags),
    custom_fields: newCase.value.custom_fields || [],
    space_id: spaceId.value
  }).then(() => {
    openCreate.value = false
    newCase.value = emptyCase()
    loadTagOptions()
    loadCases({ page: page.value, itemsPerPage: itemsPerPage.value, sortBy: sortBy.value })
  }).catch(() => {
    createError.value = true
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

function priorityLabel(priority) {
  return priorityOptions.find(option => option.value === priority)?.title || 'P2 · Normal'
}

function priorityColor(priority) {
  return ({ P0: 'error', P1: 'warning', P2: 'primary', P3: 'grey' })[priority] || 'primary'
}

function normalizeTags(tags) {
  const seen = new Set()
  return (Array.isArray(tags) ? tags : []).reduce((result, tag) => {
    if (typeof tag !== 'string') return result
    const label = tag.trim()
    const key = label.toLocaleLowerCase()
    if (label && !seen.has(key)) {
      seen.add(key)
      result.push(label)
    }
    return result
  }, [])
}

onMounted(() => {
  capabilityStore.load(spaceId.value)
  loadTagOptions()
  loadSuiteOptions()
})

watch(() => route.query, (query) => {
  const nextPage = parseInt(query.page) || 1
  const nextPageSize = parseInt(query.page_size) || 25
  const nextSearch = query.search || ''
  const nextType = query.type || ''
  const nextStatus = query.status || ''
  const nextSuite = query.suite_id || ''
  const nextPriority = query.priority || ''
  const nextTags = (Array.isArray(query.tags) ? query.tags : query.tags ? [query.tags] : []).map(String)
  const nextSortBy = query.sort_by && query.sort_order
    ? [{ key: query.sort_by, order: query.sort_order }]
    : [{ key: 'created_at', order: 'desc' }]
  const changed = page.value !== nextPage || itemsPerPage.value !== nextPageSize || search.value !== nextSearch ||
    filterType.value !== nextType || filterStatus.value !== nextStatus || filterSuite.value !== nextSuite ||
    filterPriority.value !== nextPriority || JSON.stringify(filterTags.value) !== JSON.stringify(nextTags) ||
    JSON.stringify(sortBy.value) !== JSON.stringify(nextSortBy)
  if (!changed) return
  page.value = nextPage
  itemsPerPage.value = nextPageSize
  search.value = nextSearch
  filterType.value = nextType
  filterStatus.value = nextStatus
  filterSuite.value = nextSuite
  filterPriority.value = nextPriority
  filterTags.value = nextTags
  sortBy.value = nextSortBy
  selectedCases.value = []
  loadCases({ page: nextPage, itemsPerPage: nextPageSize, sortBy: nextSortBy })
}, { deep: true })

watch(spaceId, () => {
  if (spaceId.value && spaceId.value !== 'undefined') capabilityStore.load(spaceId.value)
  caseListRequestId += 1
  tableLoading.value = false
  loadTagOptions()
  loadSuiteOptions()
  filterSuite.value = ''
  suiteOptions.value = []
  cases.value = []
  totalCases.value = 0
  hasLoaded.value = false
  selectedCases.value = []
  page.value = 1
  loadCases({ page: 1, itemsPerPage: itemsPerPage.value, sortBy: sortBy.value })
})

watch(openCreate, (isOpen) => {
  if (isOpen) {
    caseTitleTouched.value = false
    selectedTemplateId.value = null
    appliedTemplate.value = null
    templateApplyError.value = false
    applyingTemplate.value = false
    loadCaseTemplates()
  } else if (!creating.value) {
    templateSelectionRequestId += 1
    applyingTemplate.value = false
    newCase.value = emptyCase()
    selectedTemplateId.value = null
    appliedTemplate.value = null
    templateApplyError.value = false
    caseTitleTouched.value = false
  }
})
</script>

<style scoped>
.list-toolbar__filter-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  flex: 1 1 100%;
}

.list-filter-search {
  flex: 1 1 280px;
  min-width: 240px;
  max-width: 420px;
}

.list-filter-sm {
  flex: 0 1 160px;
  min-width: 145px;
}

.list-filter-tags {
  flex: 0 1 240px;
  min-width: 210px;
}

.list-toolbar__filter-row--secondary {
  margin-top: 0;
}

.case-list-actions,
.case-list-actions__primary,
.case-list-actions__bulk {
  display: contents;
}

@media (min-width: 960px) {
  .case-list-actions,
  .case-list-actions__primary,
  .case-list-actions__bulk {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: flex-end;
    gap: 8px;
  }

  .case-list-actions {
    width: 100%;
  }

  .case-list-actions__bulk {
    width: 100%;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  }

  .case-list-actions__primary {
    width: 100%;
  }
}

.list-row-link { color: inherit; font-weight: 500; text-decoration: none; }
.list-row-link:hover { text-decoration: underline; }
.list-row-link:focus-visible { border-radius: 2px; outline: 2px solid currentColor; outline-offset: 2px; }

@media (min-width: 960px) {
  .row-navigation-table :deep(.v-data-table__tr) {
    position: relative;
  }

  .row-navigation-table :deep(.list-row-link) {
    position: static;
  }

  .row-navigation-table :deep(.list-row-link::after) {
    position: absolute;
    z-index: 0;
    inset: 0;
    content: '';
  }

  .row-navigation-table :deep(.list-row-link:focus-visible::after) {
    outline: 2px solid rgb(var(--v-theme-primary));
    outline-offset: -2px;
  }

  .row-navigation-table :deep(td:has(.v-btn)),
  .row-navigation-table :deep(td:has(.v-selection-control)) {
    position: relative;
    z-index: 1;
  }
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

.short-name-cell {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.list-loading-region {
  position: relative;
  min-height: 360px;
}

.list-loading-region__skeleton {
  position: absolute;
  z-index: 1;
  inset: 0;
}

.list-loading-region__content--hidden {
  visibility: hidden;
}
</style>
