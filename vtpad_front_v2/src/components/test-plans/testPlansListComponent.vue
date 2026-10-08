<template>
  <div>
    <v-toolbar density="compact" class="list-toolbar ">
      <v-text-field
        v-model="search"
        prepend-inner-icon="mdi-magnify"
        label="Search test plans"
        density="compact"
        hide-details
        variant="solo"
        class="mx-2 list-filter-search"
        clearable
        @update:model-value="onSearch"
      />
      <v-spacer />
      <v-btn v-if="loadErrorStatus !== 403" color="primary" prepend-icon="mdi-plus" @click="openDialog = true">
        New Plan
      </v-btn>
    </v-toolbar>

    <v-alert v-if="loadError" type="error" variant="tonal" density="compact" class="mb-3" role="alert">
      {{ loadErrorStatus === 403 ? 'You do not have permission to view test plans in this space.' : plans.length ? 'Test plans could not be refreshed. Existing results are still shown.' : 'Test plans could not be loaded.' }}
      <v-btn v-if="loadErrorStatus !== 403" size="small" variant="text" @click="loadPlans({ page: page, itemsPerPage: pageSize })">Retry</v-btn>
    </v-alert>

    <div class="list-loading-region" :aria-busy="initialLoading || loading">
      <list-loading-skeleton
        v-if="initialLoading"
        class="list-loading-region__skeleton"
        variant="table"
        :columns="headers.length"
        label="test plans"
      />
      <v-data-table-server
      :class="{ 'list-loading-region__content--hidden': initialLoading || (loadError && !plans.length) }"
      v-model:page="page"
      v-model:items-per-page="pageSize"
      :headers="headers"
      :items="plans"
      :items-length="total"
      :loading="loading"
      item-value="id"
      @update:options="loadPlans"
      @click:row="(event, { item }) => $router.push(`/space/${spaceId}/test-plans/${item.id}`)"
    >
      <template #no-data>
        <contextual-empty-state
          v-if="search"
          icon="mdi-filter-off-outline"
          title="No matching test plans"
          text="Clear the search to see all test plans."
          action-label="Clear search"
          @action="search = ''; onSearch()"
        />
        <contextual-empty-state
          v-else
          icon="mdi-clipboard-text-outline"
          title="No test plans yet"
          text="Use New Plan when you have permission to add plans to this space."
        />
      </template>
      <template v-slot:[`item.name`]="{ item }">
        <span class="font-weight-medium">{{ item.name }}</span>
      </template>
      <template v-slot:[`item.case_count`]="{ item }">
        <v-chip size="small" color="primary">{{ (item.case_ids || []).length }}</v-chip>
      </template>
      <template v-slot:[`item.description`]="{ item }">
        <span class="text-medium-emphasis">{{ item.description || '—' }}</span>
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
        <v-btn icon size="small" variant="text" @click.stop="deletePlan(item.id)">
          <v-icon color="error">mdi-delete</v-icon>
        </v-btn>
      </template>
      </v-data-table-server>
    </div>

    <!-- Create Dialog -->
    <v-dialog v-model="openDialog" max-width="500">
      <v-card
        data-keyboard-save-scope
        :data-keyboard-escape-confirm="isCreateDirty ? 'Discard unsaved test plan changes?' : null"
        :data-keyboard-escape-saving="creating ? 'true' : null"
      >
        <v-card-title>Create Test Plan</v-card-title>
        <v-card-text>
          <v-text-field v-model="newPlan.name" label="Name" required autofocus />
          <v-textarea v-model="newPlan.description" label="Description" rows="2" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="openDialog = false">Cancel</v-btn>
          <v-btn color="primary" data-keyboard-save-action :loading="creating" :disabled="creating" @click="createPlan">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useLogger } from '@/composables/useLogger'
import { useRoute } from 'vue-router'
import { testPlanService } from '@/services'
import ListLoadingSkeleton from '@/components/common/ListLoadingSkeleton.vue'

const log = useLogger('app')
const route = useRoute()

const spaceId = computed(() => route.params.spaceId)

const plans = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(25)
const loading = ref(false)
const hasLoaded = ref(false)
const initialLoading = computed(() => Boolean(spaceId.value) && spaceId.value !== 'undefined' && !hasLoaded.value)
const loadError = ref(false)
const loadErrorStatus = ref(0)
const requestId = ref(0)
const search = ref('')
const searchDebounce = ref(null)
const openDialog = ref(false)
const newPlan = ref({ name: '', description: '' })
const creating = ref(false)
const isCreateDirty = computed(() => Boolean(newPlan.value.name || newPlan.value.description))

watch(openDialog, (isOpen) => {
  if (!isOpen && !creating.value) newPlan.value = { name: '', description: '' }
})

watch(spaceId, (nextSpaceId, previousSpaceId) => {
  if (!nextSpaceId || nextSpaceId === previousSpaceId) return
  requestId.value += 1
  clearTimeout(searchDebounce.value)
  plans.value = []
  total.value = 0
  page.value = 1
  hasLoaded.value = false
  loading.value = false
  loadError.value = false
  loadErrorStatus.value = 0
  search.value = ''
  openDialog.value = false
  newPlan.value = { name: '', description: '' }
  loadPlans({ page: 1, itemsPerPage: pageSize.value })
})

const headers = computed(() => [
  { title: 'Name', key: 'name', sortable: false },
  { title: 'Cases', key: 'case_count', sortable: false, width: '120px' },
  { title: 'Description', key: 'description', sortable: false },
  { title: 'Create', key: 'created_by', sortable: false, width: '180px' },
  { title: 'Created', key: 'created_at', sortable: false, width: '160px' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end', width: '100px' }
])

async function loadPlans(options = {}) {
  if (!spaceId.value || spaceId.value === 'undefined') return
  const currentRequest = ++requestId.value
  const p = options.page || page.value
  const itemsPerPage = options.itemsPerPage || pageSize.value
  loading.value = true
  loadError.value = false
  loadErrorStatus.value = 0
  page.value = p
  pageSize.value = itemsPerPage
  try {
    const res = await testPlanService.listBySpace(spaceId.value, {
      page: p,
      page_size: itemsPerPage,
      search: search.value || undefined
    })
    if (currentRequest === requestId.value) {
      plans.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } catch (e) {
    if (currentRequest === requestId.value) {
      loadError.value = true
      loadErrorStatus.value = Number(e?.response?.status || 0)
      if (loadErrorStatus.value === 403) {
        plans.value = []
        total.value = 0
      }
      log.error("request failed", e)
    }
  } finally {
    if (currentRequest === requestId.value) {
      hasLoaded.value = true
      loading.value = false
    }
  }
}

function onSearch() {
  clearTimeout(searchDebounce.value)
  searchDebounce.value = setTimeout(() => {
    loadPlans({ page: 1, itemsPerPage: pageSize.value })
  }, 400)
}

async function createPlan() {
  if (creating.value) return
  creating.value = true
  try {
    await testPlanService.create({
      name: newPlan.value.name,
      description: newPlan.value.description,
      space_id: spaceId.value
    })
    openDialog.value = false
    newPlan.value = { name: '', description: '' }
    loadPlans({ page: page.value, itemsPerPage: pageSize.value })
  } catch (e) {
    log.error("request failed", e)
  } finally {
    creating.value = false
  }
}

async function deletePlan(id) {
  if (!confirm('Delete this test plan?')) return
  try {
    await testPlanService.delete(id)
    loadPlans({ page: page.value, itemsPerPage: pageSize.value })
  } catch (e) {
    log.error("request failed", e)
  }
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
