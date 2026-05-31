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
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openDialog = true">
        New Plan
      </v-btn>
    </v-toolbar>

    <v-data-table-server
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
      <template v-slot:item.name="{ item }">
        <span class="font-weight-medium">{{ item.name }}</span>
      </template>
      <template v-slot:item.case_count="{ item }">
        <v-chip size="small" color="primary">{{ (item.case_ids || []).length }}</v-chip>
      </template>
      <template v-slot:item.description="{ item }">
        <span class="text-medium-emphasis">{{ item.description || '—' }}</span>
      </template>
      <template v-slot:item.created_at="{ item }">
        {{ formatDate(item.created_at) }}
      </template>
      <template v-slot:item.actions="{ item }">
        <v-btn icon size="small" variant="text" @click.stop="deletePlan(item.id)">
          <v-icon color="error">mdi-delete</v-icon>
        </v-btn>
      </template>
    </v-data-table-server>

    <!-- Create Dialog -->
    <v-dialog v-model="openDialog" max-width="500">
      <v-card>
        <v-card-title>Create Test Plan</v-card-title>
        <v-card-text>
          <v-text-field v-model="newPlan.name" label="Name" required autofocus />
          <v-textarea v-model="newPlan.description" label="Description" rows="2" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="openDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="createPlan">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useLogger } from '@/composables/useLogger'
import { useRoute } from 'vue-router'
import { testPlanService } from '@/services'

const log = useLogger('app')
const route = useRoute()

const spaceId = computed(() => route.params.spaceId)

const plans = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(25)
const loading = ref(false)
const search = ref('')
const searchDebounce = ref(null)
const openDialog = ref(false)
const newPlan = ref({ name: '', description: '' })

const headers = computed(() => [
  { title: 'Name', key: 'name', sortable: false },
  { title: 'Cases', key: 'case_count', sortable: false, width: '120px' },
  { title: 'Description', key: 'description', sortable: false },
  { title: 'Created', key: 'created_at', sortable: false, width: '160px' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end', width: '100px' }
])

async function loadPlans({ page: p, itemsPerPage }) {
  if (!spaceId.value || spaceId.value === 'undefined') return
  loading.value = true
  page.value = p
  pageSize.value = itemsPerPage
  try {
    const res = await testPlanService.listBySpace(spaceId.value, {
      page: p,
      page_size: itemsPerPage,
      search: search.value || undefined
    })
    plans.value = res.data.items
    total.value = res.data.total
  } catch (e) {
    log.error("request failed", e)
  } finally {
    loading.value = false
  }
}

function onSearch() {
  clearTimeout(searchDebounce.value)
  searchDebounce.value = setTimeout(() => {
    loadPlans({ page: 1, itemsPerPage: pageSize.value })
  }, 400)
}

async function createPlan() {
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
</style>
