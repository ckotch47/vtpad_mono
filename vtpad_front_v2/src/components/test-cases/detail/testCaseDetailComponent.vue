<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>

  <div v-else>
    <v-container fluid class="pb-0">
      <breadcrumbs-component :items="breadcrumbItems" />
    </v-container>
    <v-toolbar density="compact">
      <v-btn icon @click="$router.back()">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <v-toolbar-title>{{ testcase.title }}</v-toolbar-title>
      <v-spacer />
      <v-chip size="small" :color="typeColor(testcase.type)" class="mr-2">{{ testcase.type }}</v-chip>
      <v-chip size="small" :color="statusColor(testcase.status)">{{ testcase.status }}</v-chip>
      <v-btn
        icon
        class="ml-2"
        :to="`/space/${spaceId}/test-cases/${caseId}/edit`"
      >
        <v-icon>mdi-pencil</v-icon>
      </v-btn>
    </v-toolbar>

    <v-container fluid>
      <v-tabs v-model="activeTab" class="mb-4">
        <v-tab value="details">Details</v-tab>
        <v-tab value="history">Run History</v-tab>
      </v-tabs>

      <v-window v-model="activeTab">
        <v-window-item value="details">
          <v-row>
            <v-col cols="12" md="8">
              <v-card class="mb-4">
                <v-card-title>Description</v-card-title>
                <v-card-text>
                  <editor-component
                    :text="testcase.text || ''"
                    :edit="false"
                    :show-menu-bubble="false"
                    :show-menu-floating="false"
                    :show-menu-fixed="false"
                  />
                </v-card-text>
              </v-card>

              <v-card class="mb-4">
                <v-card-title>Preconditions</v-card-title>
                <v-card-text>
                  <editor-component
                    :text="testcase.preconditions || ''"
                    :edit="false"
                    :show-menu-bubble="false"
                    :show-menu-floating="false"
                    :show-menu-fixed="false"
                  />
                </v-card-text>
              </v-card>

              <v-card class="mb-4">
                <v-card-title>Steps</v-card-title>
                <v-card-text>
                  <editor-component
                    :text="testcase.steps || ''"
                    :edit="false"
                    :show-menu-bubble="false"
                    :show-menu-floating="false"
                    :show-menu-fixed="false"
                  />
                </v-card-text>
              </v-card>

              <v-card class="mb-4">
                <v-card-title>Expected Results</v-card-title>
                <v-card-text>
                  <editor-component
                    :text="testcase.expected_results || ''"
                    :edit="false"
                    :show-menu-bubble="false"
                    :show-menu-floating="false"
                    :show-menu-fixed="false"
                  />
                </v-card-text>
              </v-card>
            </v-col>

            <v-col cols="12" md="4">
              <v-card>
                <v-card-title>Info</v-card-title>
                <v-card-text>
                  <v-list density="compact">
                    <v-list-item>
                      <v-list-item-title>ID</v-list-item-title>
                      <v-list-item-subtitle>{{ testcase.id }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Short Name</v-list-item-title>
                      <v-list-item-subtitle>{{ testcase.short_name || '-' }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>External ID</v-list-item-title>
                      <v-list-item-subtitle>{{ testcase.external_id || '-' }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Link</v-list-item-title>
                      <v-list-item-subtitle>
                        <a v-if="testcase.link" :href="testcase.link" target="_blank">{{ testcase.link }}</a>
                        <span v-else>-</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Created</v-list-item-title>
                      <v-list-item-subtitle>{{ formatDate(testcase.created_at) }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Updated</v-list-item-title>
                      <v-list-item-subtitle>{{ formatDate(testcase.updated_at) }}</v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>

              <v-card class="mt-4">
                <v-card-title>Versions</v-card-title>
                <v-card-text>
                  <v-list density="compact">
                    <v-list-item v-for="ver in versions" :key="ver.id">
                      <v-list-item-title>v{{ ver.version_number }}</v-list-item-title>
                      <v-list-item-subtitle>{{ formatDate(ver.created_at) }}</v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-window-item>

        <v-window-item value="history">
          <v-card>
            <v-card-title>Run History</v-card-title>
            <v-card-text>
              <v-data-table-server
                v-model:items-per-page="historyPageSize"
                :headers="historyHeaders"
                :items="runHistory"
                :items-length="historyTotal"
                :loading="historyLoading"
                item-value="id"
                @update:options="loadRunHistory"
              >
                <template v-slot:item.status="{ item }">
                  <v-chip size="small" :color="resultStatusColor(item.status)">{{ item.status }}</v-chip>
                </template>
                <template v-slot:item.run_name="{ item }">
                  <router-link :to="`/space/${spaceId}/test-runs/${item.run_id}`">
                    {{ item.run_name }}
                  </router-link>
                </template>
                <template v-slot:item.executed_at="{ item }">
                  {{ formatDate(item.executed_at) }}
                </template>
              </v-data-table-server>
            </v-card-text>
          </v-card>
        </v-window-item>
      </v-window>
    </v-container>
  </div>
</template>

<script setup>
import {ref, computed, onMounted} from 'vue'
import { useLogger } from '@/composables/useLogger'
import { useRoute } from 'vue-router'
import { useApi } from '@/composables/useApi'
import EditorComponent from '@/components/common/editor/editorComponent.vue'
import BreadcrumbsComponent from '@/components/common/breadcrumbsComponent.vue'

const log = useLogger('app')
const route = useRoute()
const api = useApi()

const spaceId = computed(() => route.params.spaceId)
const caseId = route.params.caseId

const loader = ref(true)
const testcase = ref({})
const versions = ref([])
const activeTab = ref('details')
const runHistory = ref([])
const historyTotal = ref(0)
const historyPageSize = ref(25)
const historyLoading = ref(false)
const breadcrumbItems = ref([])

const historyHeaders = computed(() => [
  { title: 'Run', key: 'run_name', sortable: false },
  { title: 'Status', key: 'status', sortable: false },
  { title: 'Duration (s)', key: 'duration_seconds', sortable: false },
  { title: 'Comment', key: 'comment', sortable: false },
  { title: 'Executed', key: 'executed_at', sortable: false }
])

function loadCase() {
  api.get(`/api/v2/test-case/${caseId}`).then(res => {
    testcase.value = res.data
    versions.value = res.data.versions || []
    breadcrumbItems.value = [
      { title: 'Test Cases', to: `/space/${spaceId.value}/test-cases` },
      { title: res.data.title }
    ]
    loader.value = false
  }).catch(() => { loader.value = false })
}

async function loadRunHistory({ page, itemsPerPage }) {
  historyLoading.value = true
  try {
    const res = await api.get(`/api/v2/test-case/${caseId}/runs`, {
      params: { page, page_size: itemsPerPage }
    })
    runHistory.value = res.data.items
    historyTotal.value = res.data.total
  } catch (e) {
    log.error("request failed", e)
  } finally {
    historyLoading.value = false
  }
}

function typeColor(type) {
  const map = { manual: 'primary', checklist: 'warning', automated: 'success' }
  return map[type] || 'grey'
}

function statusColor(status) {
  const map = { active: 'success', draft: 'grey', deprecated: 'error' }
  return map[status] || 'grey'
}

function resultStatusColor(status) {
  const map = { passed: 'success', failed: 'error', blocked: 'warning', skipped: 'grey', not_run: 'grey' }
  return map[status] || 'grey'
}

function formatDate(date) {
  return date ? new Date(date).toLocaleDateString() : ''
}

onMounted(() => {
  loadCase()
})
</script>
