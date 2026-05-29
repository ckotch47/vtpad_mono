<template>
  <div>
    <v-row align="center" class="mb-2">
      <v-col>
        <h1 class="text-h4 font-weight-bold">Test Plans</h1>
      </v-col>
      <v-col cols="auto">
        <v-btn color="primary" prepend-icon="mdi-plus" @click="openDialog = true">
          New Plan
        </v-btn>
      </v-col>
    </v-row>

    <v-data-table-server
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
import { useRoute, useRouter } from 'vue-router'
import { testPlanService } from '@/services'

const route = useRoute()
const router = useRouter()

const spaceId = computed(() => route.params.spaceId)

const plans = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(25)
const loading = ref(false)
const openDialog = ref(false)
const newPlan = ref({ name: '', description: '' })

const headers = computed(() => [
  { title: 'Name', key: 'name', sortable: false },
  { title: 'Cases', key: 'case_count', sortable: false },
  { title: 'Description', key: 'description', sortable: false },
  { title: 'Created', key: 'created_at', sortable: false },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
])

async function loadPlans({ page: p, itemsPerPage }) {
  if (!spaceId.value || spaceId.value === 'undefined') return
  loading.value = true
  page.value = p
  pageSize.value = itemsPerPage
  try {
    const res = await testPlanService.listBySpace(spaceId.value, { page: p, page_size: itemsPerPage })
    plans.value = res.data.items
    total.value = res.data.total
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
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
    console.error(e)
  }
}

async function deletePlan(id) {
  if (!confirm('Delete this test plan?')) return
  try {
    await testPlanService.delete(id)
    loadPlans({ page: page.value, itemsPerPage: pageSize.value })
  } catch (e) {
    console.error(e)
  }
}
</script>
