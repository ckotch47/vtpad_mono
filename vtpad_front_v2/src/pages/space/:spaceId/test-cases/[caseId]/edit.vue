<route>
{
  meta: {
    layout: "spaces",
    tabValue: "test-cases"
  }
}
</route>

<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>

  <v-container v-else fluid class="pa-6">
    <v-row>
      <v-col cols="12" md="9">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-btn icon variant="text" @click="$router.back()">
              <v-icon>mdi-arrow-left</v-icon>
            </v-btn>
            <span class="ml-2">Edit Test Case</span>
            <v-spacer />
            <v-btn color="primary" @click="save">Save</v-btn>
          </v-card-title>

          <v-card-text>
            <v-text-field
              v-model="form.title"
              label="Title"
              required
              class="mb-4"
            />

            <v-row class="mb-4">
              <v-col cols="4">
                <v-select
                  v-model="form.type"
                  :items="['manual','checklist','automated']"
                  label="Type"
                />
              </v-col>
              <v-col cols="4">
                <v-select
                  v-model="form.status"
                  :items="['draft','active','deprecated']"
                  label="Status"
                />
              </v-col>
              <v-col cols="4">
                <v-text-field v-model="form.short_name" label="Short Name" />
              </v-col>
            </v-row>

            <v-row class="mb-4">
              <v-col cols="6">
                <v-text-field v-model="form.external_id" label="External ID" />
              </v-col>
              <v-col cols="6">
                <v-text-field v-model="form.link" label="Link" />
              </v-col>
            </v-row>

            <div class="text-subtitle-1 mb-2">Description</div>
            <editor-component
              :text="form.text || ''"
              :edit="true"
              :show-menu-fixed="true"
              place-holder-editor="Enter description..."
              @editor-update="form.text = $event"
            />

            <div class="text-subtitle-1 mt-4 mb-2">Preconditions</div>
            <editor-component
              :text="form.preconditions || ''"
              :edit="true"
              :show-menu-fixed="true"
              place-holder-editor="Enter preconditions..."
              @editor-update="form.preconditions = $event"
            />

            <div class="text-subtitle-1 mt-4 mb-2">Steps</div>
            <editor-component
              :text="form.steps || ''"
              :edit="true"
              :show-menu-fixed="true"
              place-holder-editor="Enter steps..."
              @editor-update="form.steps = $event"
            />

            <div class="text-subtitle-1 mt-4 mb-2">Expected Results</div>
            <editor-component
              :text="form.expected_results || ''"
              :edit="true"
              :show-menu-fixed="true"
              place-holder-editor="Enter expected results..."
              @editor-update="form.expected_results = $event"
            />
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>Info</v-card-title>
          <v-card-text>
            <v-list density="compact">
              <v-list-item>
                <v-list-item-title>ID</v-list-item-title>
                <v-list-item-subtitle>{{ testcase.id }}</v-list-item-subtitle>
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
  </v-container>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '@/composables/useApi'
import EditorComponent from '@/components/common/editor/editorComponent.vue'

const route = useRoute()
const router = useRouter()
const api = useApi()

const spaceId = route.params.spaceId
const caseId = route.params.caseId
const draftKey = `case-draft-${caseId}`

const loader = ref(true)
const testcase = ref({})
const versions = ref([])
const form = ref({})
const hasDraft = ref(false)
let autoSaveTimer = null

function loadCase() {
  api.get(`/api/v2/test-case/${caseId}`).then(res => {
    testcase.value = res.data
    versions.value = res.data.versions || []
    const draft = localStorage.getItem(draftKey)
    if (draft) {
      try {
        const parsed = JSON.parse(draft)
        if (parsed._savedAt && new Date(parsed._savedAt) > new Date(res.data.updated_at)) {
          if (confirm('You have an unsaved draft. Restore it?')) {
            form.value = parsed
            hasDraft.value = true
            loader.value = false
            return
          }
        }
      } catch (e) {
        // ignore parse error
      }
    }
    form.value = { ...res.data }
    loader.value = false
  }).catch(() => { loader.value = false })
}

function scheduleAutoSave() {
  clearTimeout(autoSaveTimer)
  autoSaveTimer = setTimeout(() => {
    saveDraft()
  }, 3000)
}

function saveDraft() {
  const draft = { ...form.value, _savedAt: new Date().toISOString() }
  localStorage.setItem(draftKey, JSON.stringify(draft))
}

function save() {
  api.patch(`/api/v2/test-case/${caseId}`, form.value).then(() => {
    localStorage.removeItem(draftKey)
    router.push(`/space/${spaceId}/test-cases/${caseId}`)
  })
}

function formatDate(date) {
  return date ? new Date(date).toLocaleDateString() : ''
}

watch(form, () => {
  scheduleAutoSave()
}, { deep: true })

onMounted(() => {
  loadCase()
})
</script>
