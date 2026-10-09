<template>
  <v-dialog v-model="isOpen" max-width="1100" :persistent="saving" scrollable>
    <v-card
      data-keyboard-save-scope
      :data-keyboard-escape-confirm="isDirty ? 'Discard unsaved case template changes?' : null"
      :data-keyboard-escape-saving="saving ? 'true' : null"
    >
      <v-card-title class="d-flex align-center">
        <span>Case templates</span>
        <v-spacer />
        <v-btn icon variant="text" aria-label="Close case templates" :disabled="saving" @click="isOpen = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-row>
          <v-col cols="4" class="template-list-column">
            <div class="d-flex align-center mb-3">
              <div class="text-subtitle-2">Templates in this space</div>
              <v-spacer />
              <v-btn size="small" variant="text" prepend-icon="mdi-plus" :disabled="saving" @click="startNew">
                New
              </v-btn>
            </div>

            <v-progress-linear v-if="loadingList" indeterminate color="primary" aria-label="Loading templates" />
            <v-alert v-if="listError" type="error" variant="tonal" density="compact" class="mb-3" role="alert">
              Templates could not be loaded.
              <v-btn size="small" variant="text" @click="loadTemplates">Retry</v-btn>
            </v-alert>
            <v-alert v-else-if="!loadingList && !templates.length" type="info" variant="tonal" density="compact">
              No templates yet. Create one to reuse case content in this space.
            </v-alert>
            <v-list v-else density="compact" nav aria-label="Case templates">
              <v-list-item
                v-for="template in templates"
                :key="template.id"
                :active="selectedId === template.id"
                :title="template.name"
                :subtitle="`Version ${template.current_version} · ${template.version_count} ${template.version_count === 1 ? 'version' : 'versions'}`"
                :disabled="saving"
                @click="selectTemplate(template.id)"
              >
                <template #append>
                  <v-icon v-if="selectedId === template.id" size="small">mdi-pencil-outline</v-icon>
                </template>
              </v-list-item>
            </v-list>
          </v-col>

          <v-col cols="8">
            <v-alert v-if="saveError" type="error" variant="tonal" density="compact" class="mb-4" role="alert">
              The template could not be saved. Check its name and fields, then try again.
            </v-alert>
            <div class="d-flex align-center mb-3">
              <div class="text-h6">{{ selectedId ? 'Edit template' : 'New template' }}</div>
              <v-spacer />
              <v-chip v-if="selectedTemplate" size="small" variant="tonal">
                Current version {{ selectedTemplate.current_version }}
              </v-chip>
            </div>
            <v-progress-linear v-if="selectedTemplateLoading" indeterminate color="primary" aria-label="Loading template" />
            <v-alert v-if="loadTemplateError" type="error" variant="tonal" density="compact" class="mb-4" role="alert">
              This template could not be loaded.
              <v-btn size="small" variant="text" @click="selectTemplate(selectedId)">Retry</v-btn>
            </v-alert>
            <div v-if="!selectedId && !creatingNew" class="text-body-2 text-medium-emphasis template-empty-editor">
              Select a template to edit it, or choose New.
            </div>
            <v-form v-else-if="creatingNew || (selectedId && selectedTemplate)" ref="formRef" @submit.prevent="saveTemplate">
              <v-text-field
                v-model="draft.name"
                label="Template name"
                :rules="[requiredRule]"
                maxlength="120"
                counter="120"
                required
              />
              <v-text-field v-model="draft.description" label="Description (optional)" />
              <v-text-field
                v-model="draft.fields.title"
                label="Default case title"
                :rules="[requiredRule]"
                maxlength="500"
                required
              />
              <v-row>
                <v-col cols="4">
                  <v-select v-model="draft.fields.type" :items="caseTypes" label="Case type" />
                </v-col>
                <v-col cols="4">
                  <v-select v-model="draft.fields.priority" :items="priorityOptions" item-title="title" item-value="value" label="Priority" />
                </v-col>
                <v-col cols="4">
                  <v-text-field
                    v-model="draft.fields.estimated_duration_seconds"
                    label="Estimate (seconds)"
                    type="number"
                    min="0"
                    step="1"
                    clearable
                    :rules="[nonNegativeIntegerRule]"
                  />
                </v-col>
              </v-row>

              <div class="text-subtitle-1 mb-2">Description</div>
              <editor-component
                :text="draft.fields.text"
                :edit="true"
                :show-menu-fixed="true"
                accessible-label="Template description"
                place-holder-editor="Describe the case..."
                @editor-update="draft.fields.text = $event"
              />
              <template v-if="draft.fields.type === 'checklist'">
                <div class="text-subtitle-1 mt-4 mb-2">Checks</div>
                <editor-component
                  :text="draft.fields.steps"
                  :edit="true"
                  :show-menu-fixed="true"
                  accessible-label="Template checks"
                  place-holder-editor="Add checks, one per list item..."
                  @editor-update="draft.fields.steps = $event"
                />
              </template>
              <template v-else>
                <div class="text-subtitle-1 mt-4 mb-2">Preconditions</div>
                <editor-component
                  :text="draft.fields.preconditions"
                  :edit="true"
                  :show-menu-fixed="true"
                  accessible-label="Template preconditions"
                  place-holder-editor="Enter preconditions..."
                  @editor-update="draft.fields.preconditions = $event"
                />
                <div class="text-subtitle-1 mt-4 mb-2">Steps</div>
                <editor-component
                  :text="draft.fields.steps"
                  :edit="true"
                  :show-menu-fixed="true"
                  accessible-label="Template steps"
                  place-holder-editor="Enter steps..."
                  @editor-update="draft.fields.steps = $event"
                />
                <div class="text-subtitle-1 mt-4 mb-2">Expected results</div>
                <editor-component
                  :text="draft.fields.expected_results"
                  :edit="true"
                  :show-menu-fixed="true"
                  accessible-label="Template expected results"
                  place-holder-editor="Enter expected results..."
                  @editor-update="draft.fields.expected_results = $event"
                />
                <div class="text-subtitle-1 mt-4 mb-2">Postconditions</div>
                <editor-component
                  :text="draft.fields.postconditions"
                  :edit="true"
                  :show-menu-fixed="true"
                  accessible-label="Template postconditions"
                  place-holder-editor="Enter postconditions..."
                  @editor-update="draft.fields.postconditions = $event"
                />
              </template>
              <div v-if="draft.fields.type === 'checklist'" class="text-caption text-medium-emphasis mt-3">
                Checklist templates preserve the shared steps field; one run result covers the whole checklist.
              </div>
              <div class="d-flex justify-end ga-2 mt-6">
                <v-btn variant="text" :disabled="saving" @click="resetDraft">Cancel</v-btn>
                <v-btn color="primary" type="submit" :loading="saving" :disabled="saving">
                  {{ selectedId ? 'Save new version' : 'Create template' }}
                </v-btn>
              </div>
            </v-form>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import EditorComponent from '@/components/common/editor/editorComponent.vue'
import { testCaseTemplateService } from '@/services'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  spaceId: { type: String, required: true }
})
const emit = defineEmits(['update:modelValue'])

const isOpen = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value)
})
const templates = ref([])
const selectedId = ref(null)
const selectedTemplate = ref(null)
const selectedTemplateLoading = ref(false)
const loadTemplateError = ref(false)
const loadingList = ref(false)
const listError = ref(false)
const saveError = ref(false)
const saving = ref(false)
const creatingNew = ref(false)
const formRef = ref(null)
const emptyFields = () => ({
  title: '', text: '', preconditions: '', steps: '', expected_results: '', postconditions: '',
  type: 'manual', priority: 'P2', estimated_duration_seconds: null
})
const emptyDraft = () => ({ name: '', description: '', fields: emptyFields() })
const draft = ref(emptyDraft())
const isDirty = computed(() => {
  if (creatingNew.value) return JSON.stringify(draft.value) !== JSON.stringify(emptyDraft())
  if (!selectedTemplate.value) return false
  const saved = {
    name: selectedTemplate.value.name || '',
    description: selectedTemplate.value.description || '',
    fields: cloneFields(selectedTemplate.value.fields)
  }
  return JSON.stringify(draft.value) !== JSON.stringify(saved)
})
const caseTypes = ['manual', 'checklist', 'automated']
const priorityOptions = [
  { title: 'P0 · Blocker', value: 'P0' },
  { title: 'P1 · High', value: 'P1' },
  { title: 'P2 · Normal', value: 'P2' },
  { title: 'P3 · Low', value: 'P3' }
]
const requiredRule = value => (typeof value === 'string' && value.trim()) || 'This field is required'
const nonNegativeIntegerRule = value => value === '' || value === null || value === undefined ||
  (Number.isInteger(Number(value)) && Number(value) >= 0) || 'Enter a whole number greater than or equal to zero'

function cloneFields(fields) {
  return { ...emptyFields(), ...(fields || {}) }
}

async function loadTemplates() {
  if (!props.spaceId) return
  loadingList.value = true
  listError.value = false
  try {
    const response = await testCaseTemplateService.listBySpace(props.spaceId, { page: 1, page_size: 100 })
    templates.value = response.data?.items || []
    if (selectedId.value && !templates.value.some(item => item.id === selectedId.value)) resetDraft()
  } catch (_) {
    listError.value = true
  } finally {
    loadingList.value = false
  }
}

function startNew() {
  selectedId.value = null
  selectedTemplate.value = null
  selectedTemplateLoading.value = false
  loadTemplateError.value = false
  creatingNew.value = true
  draft.value = emptyDraft()
  saveError.value = false
}

async function selectTemplate(templateId) {
  selectedId.value = templateId
  creatingNew.value = false
  selectedTemplate.value = null
  selectedTemplateLoading.value = true
  loadTemplateError.value = false
  saveError.value = false
  try {
    const response = await testCaseTemplateService.getById(props.spaceId, templateId)
    if (selectedId.value !== templateId) return
    selectedTemplate.value = response.data
    draft.value = {
      name: response.data.name || '',
      description: response.data.description || '',
      fields: cloneFields(response.data.fields)
    }
  } catch (_) {
    if (selectedId.value === templateId) loadTemplateError.value = true
  } finally {
    if (selectedId.value === templateId) selectedTemplateLoading.value = false
  }
}

function resetDraft() {
  selectedId.value = null
  selectedTemplate.value = null
  selectedTemplateLoading.value = false
  loadTemplateError.value = false
  creatingNew.value = false
  saveError.value = false
  draft.value = emptyDraft()
}

async function saveTemplate() {
  const validation = await formRef.value?.validate()
  if ((validation && !validation.valid) || (selectedId.value && !selectedTemplate.value)) return
  saving.value = true
  saveError.value = false
  const estimatedDuration = draft.value.fields.estimated_duration_seconds
  const payload = {
    name: draft.value.name.trim(),
    description: draft.value.description?.trim() || null,
    fields: {
      ...draft.value.fields,
      estimated_duration_seconds: estimatedDuration === '' || estimatedDuration === null || estimatedDuration === undefined
        ? null
        : Number(estimatedDuration)
    }
  }
  try {
    const response = selectedId.value
      ? await testCaseTemplateService.update(props.spaceId, selectedId.value, payload)
      : await testCaseTemplateService.create(props.spaceId, payload)
    selectedTemplate.value = response.data
    selectedId.value = response.data.id
    creatingNew.value = false
    draft.value = {
      name: response.data.name,
      description: response.data.description || '',
      fields: cloneFields(response.data.fields)
    }
    await loadTemplates()
  } catch (_) {
    saveError.value = true
  } finally {
    saving.value = false
  }
}

watch(isOpen, open => {
  if (open) {
    resetDraft()
    loadTemplates()
  }
})
</script>

<style scoped>
.template-list-column {
  border-right: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.template-empty-editor {
  min-height: 240px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}
</style>
