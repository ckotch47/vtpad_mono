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
        <v-card data-keyboard-save-scope>
          <v-card-title class="d-flex align-center">
            <v-btn icon variant="text" @click="$router.back()">
              <v-icon>mdi-arrow-left</v-icon>
            </v-btn>
            <span class="ml-2">Edit Test Case</span>
            <v-spacer />
            <v-btn color="primary" data-keyboard-save-action :loading="saving" :disabled="saving || customFieldForm?.loading" @click="save">Save</v-btn>
          </v-card-title>

          <v-card-text>
            <v-alert v-if="saveError" type="error" variant="tonal" density="compact" class="mb-4" role="alert">
              The test case could not be saved. Check the fields and try again.
            </v-alert>
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
              <v-col cols="4">
                <v-select
                  v-model="form.priority"
                  :items="priorityOptions"
                  item-title="title"
                  item-value="value"
                  label="Priority"
                />
              </v-col>
              <v-col cols="8">
                <v-combobox
                  v-model="form.tags"
                  :items="tagOptions"
                  :loading="tagOptionsLoading"
                  label="Tags"
                  multiple
                  chips
                  closable-chips
                  clearable
                  hint="Choose an existing tag or enter a new one"
                  persistent-hint
                />
                <div v-if="tagOptionsError" class="text-caption text-warning">Existing tags could not be loaded. You can still enter tag labels.</div>
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

            <v-text-field
              v-model="form.estimated_duration_seconds"
              label="Estimated duration (seconds)"
              type="number"
              min="0"
              step="1"
              clearable
              hint="Leave empty when no estimate is available. Zero is a valid estimate."
              persistent-hint
              class="mb-4"
            />

            <div class="text-subtitle-1 mb-2">Description</div>
            <editor-component
              :text="form.text || ''"
              :edit="true"
              :show-menu-fixed="true"
              accessible-label="Description"
              place-holder-editor="Enter description..."
              @editor-update="form.text = $event"
            />

            <template v-if="form.type === 'checklist'">
              <div class="d-flex align-center mt-4 mb-2">
                <div class="text-subtitle-1">Checks</div>
                <v-chip size="x-small" color="success" class="ml-2">Checklist</v-chip>
              </div>
              <editor-component
                :text="form.steps || ''"
                :edit="true"
                :show-menu-fixed="true"
                accessible-label="Checks"
                place-holder-editor="Add checks, one per list item..."
                @editor-update="form.steps = $event"
              />
              <div class="text-caption text-medium-emphasis mt-2">Checks are reviewed together; a run stores one result for the whole checklist.</div>
            </template>

            <template v-else>
              <div class="text-subtitle-1 mt-4 mb-2">Preconditions</div>
              <editor-component
                :text="form.preconditions || ''"
                :edit="true"
                :show-menu-fixed="true"
                accessible-label="Preconditions"
                place-holder-editor="Enter preconditions..."
                @editor-update="form.preconditions = $event"
              />

              <div class="text-subtitle-1 mt-4 mb-2">Steps</div>
              <editor-component
                :text="form.steps || ''"
                :edit="true"
                :show-menu-fixed="true"
                accessible-label="Steps"
                place-holder-editor="Enter steps..."
                @editor-update="form.steps = $event"
              />

            <div class="text-subtitle-1 mt-4 mb-2">Expected Results</div>
              <editor-component
                :text="form.expected_results || ''"
                :edit="true"
                :show-menu-fixed="true"
                accessible-label="Expected Results"
                place-holder-editor="Enter expected results..."
                @editor-update="form.expected_results = $event"
              />
            </template>
            <custom-field-values-component
              ref="customFieldForm"
              v-model="form.custom_fields"
              :space-id="spaceId"
              entity-type="testcase"
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
defineOptions({ name: 'TestCaseEditPage' })

import {ref, watch, onMounted, computed} from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '@/composables/useApi'
import EditorComponent from '@/components/common/editor/editorComponent.vue'
import CustomFieldValuesComponent from '@/components/custom-fields/customFieldValuesComponent.vue'
import { testCaseService } from '@/services'

const route = useRoute()
const router = useRouter()
const api = useApi()

const spaceId = computed(() => route.params.spaceId)
const caseId = route.params.caseId
const draftKey = `case-draft-${caseId}`

const loader = ref(true)
const testcase = ref({})
const versions = ref([])
const form = ref({})
const tagOptions = ref([])
const tagOptionsLoading = ref(false)
const tagOptionsError = ref(false)
const saving = ref(false)
const saveError = ref(false)
const customFieldForm = ref(null)
const priorityOptions = [
  { title: 'P0 · Blocker', value: 'P0' },
  { title: 'P1 · High', value: 'P1' },
  { title: 'P2 · Normal', value: 'P2' },
  { title: 'P3 · Low', value: 'P3' }
]
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
            form.value = {
              ...parsed,
              priority: parsed.priority || 'P2',
              tags: Array.isArray(parsed.tags) ? parsed.tags : [],
              custom_fields: Array.isArray(parsed.custom_fields) ? parsed.custom_fields : (res.data.custom_fields || [])
            }
            hasDraft.value = true
            loader.value = false
            return
          }
        }
      } catch (e) {
        // ignore parse error
      }
    }
    form.value = {
      ...res.data,
      priority: res.data.priority || 'P2',
      tags: Array.isArray(res.data.tags) ? [...res.data.tags] : [],
      custom_fields: Array.isArray(res.data.custom_fields) ? [...res.data.custom_fields] : []
    }
    loader.value = false
  }).catch(() => { loader.value = false })
  loadTagOptions()
}

async function loadTagOptions() {
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

async function save() {
  const fieldsValidation = await customFieldForm.value?.validate()
  if (fieldsValidation && !fieldsValidation.valid) return
  saving.value = true
  saveError.value = false
  const estimatedDuration = form.value.estimated_duration_seconds
  const payload = {
    ...form.value,
    priority: form.value.priority || 'P2',
    tags: normalizeTags(form.value.tags),
    estimated_duration_seconds: estimatedDuration === '' || estimatedDuration === null || estimatedDuration === undefined
      ? null
      : Number(estimatedDuration)
  }
  api.patch(`/api/v2/test-case/${caseId}`, payload).then(() => {
    localStorage.removeItem(draftKey)
    router.push(`/space/${spaceId.value}/test-cases/${caseId}`)
  }).catch(() => {
    saveError.value = true
  }).finally(() => {
    saving.value = false
  })
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
