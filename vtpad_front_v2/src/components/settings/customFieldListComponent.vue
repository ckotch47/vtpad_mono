<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>
  <div v-if="!loader" class="mx-auto my-2">
    <div class="d-flex justify-space-between align-center mb-4">
      <h2>Custom Fields</h2>
      <v-btn color="primary" @click="showCreateDialog = true">Add Field</v-btn>
    </div>

    <v-card v-if="fields.length">
      <v-list>
        <v-list-item v-for="field in fields" :key="field.id">
          <template #prepend>
            <v-icon>mdi-form-textbox</v-icon>
          </template>
          <v-list-item-title>{{ field.name }}</v-list-item-title>
          <v-list-item-subtitle>
            Type: {{ field.field_type }} | Entity: {{ field.entity_type }}
            <span v-if="field.required">| Required</span>
            <span v-if="field.options?.length">| Options: {{ field.options.join(', ') }}</span>
          </v-list-item-subtitle>
          <template #append>
          <v-btn icon variant="text" @click="editField(field)">
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
          <v-btn icon variant="text" color="red" @click="deleteField(field.id)">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </v-list>
    </v-card>
    <v-card v-else class="pa-4">
      <p>No custom fields yet.</p>
    </v-card>
  </div>

  <v-dialog v-model="showCreateDialog" max-width="500">
    <v-card>
      <v-card-title>{{ editingId ? 'Edit' : 'Add' }} Custom Field</v-card-title>
      <v-card-text>
        <v-form ref="cfForm" v-model="formValid">
          <v-text-field v-model="form.name" label="Name" :rules="[v => !!v || 'Name is required']" required />
          <v-select v-model="form.field_type" :items="fieldTypes" label="Field Type" :rules="[v => !!v || 'Field type is required']" required />
          <v-select v-model="form.entity_type" :items="entityTypes" label="Entity Type" :rules="[v => !!v || 'Entity type is required']" required />
          <v-textarea
            v-model="optionsText"
            label="Options (one per line, for select/multiselect)"
            rows="3"
            :rules="optionsRules"
            :hint="optionsHint"
            persistent-hint
          />
          <v-switch
            v-model="form.required"
            label="Required"
            color="primary"
            hide-details="auto"
            :disabled="form.entity_type === 'testrun'"
          />
          <div v-if="form.entity_type === 'testrun'" class="text-caption text-medium-emphasis mt-1">
            Required custom fields are currently available for test cases only.
          </div>
          <v-text-field v-model.number="form.sort" label="Sort order" type="number" />
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="closeDialog">Cancel</v-btn>
        <v-btn color="primary" :disabled="!formValid" @click="saveField">{{ editingId ? 'Update' : 'Create' }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { customFieldService } from '@/services'

const route = useRoute()
const spaceId = computed(() => route.params.spaceId)

const loader = ref(true)
const fields = ref([])
const showCreateDialog = ref(false)
const editingId = ref(null)
const formValid = ref(false)
const form = ref({
  name: '',
  field_type: 'text',
  entity_type: 'testcase',
  options: [],
  required: false,
  sort: 0
})
const cfForm = ref(null)
const originalOptions = ref([])
const fieldTypes = ['text', 'select', 'multiselect', 'number', 'date', 'checkbox']
const entityTypes = ['testcase', 'testrun']

const optionsHint = computed(() => ['select', 'multiselect'].includes(form.value.field_type)
  ? 'Add at least one unique option, one per line.'
  : 'Only used for select and multiselect fields.')
const optionsRules = computed(() => ['select', 'multiselect'].includes(form.value.field_type)
  ? [validateSelectOptions]
  : [])

const optionsText = computed({
  get() {
    return form.value.options.join('\n')
  },
  set(val) {
    form.value.options = val.split('\n').map(s => s.trim()).filter(Boolean)
  }
})

function loadFields() {
  loader.value = true
  customFieldService.list(spaceId.value).then(res => {
    fields.value = res.data
    loader.value = false
  }).catch(() => {
    loader.value = false
  })
}

function editField(field) {
  editingId.value = field.id
  form.value = {
    name: field.name,
    field_type: field.field_type,
    entity_type: field.entity_type,
    options: field.options || [],
    required: Boolean(field.required),
    sort: field.sort || 0
  }
  originalOptions.value = [...(field.options || [])]
  showCreateDialog.value = true
}

function validateSelectOptions(value) {
  const options = (value || '').split('\n').map(option => option.trim()).filter(Boolean)
  const unchangedLegacyEmptyOptions = editingId.value
    && originalOptions.value.length === 0
    && options.length === 0
  if (unchangedLegacyEmptyOptions) return true
  if (!options.length) return 'Add at least one option'
  if (new Set(options).size !== options.length) return 'Options must be unique'
  return true
}

function closeDialog() {
  showCreateDialog.value = false
  editingId.value = null
  form.value = { name: '', field_type: 'text', entity_type: 'testcase', options: [], required: false, sort: 0 }
  formValid.value = false
  originalOptions.value = []
  nextTick(() => cfForm.value?.resetValidation())
}

function saveField() {
  if (form.value.entity_type === 'testrun') form.value.required = false
  const payload = {
    ...form.value,
    space_id: spaceId.value
  }
  if (editingId.value) {
    // Keep unrelated edits possible for legacy select fields that predate
    // option validation; omit options when their empty value is unchanged.
    if (originalOptions.value.length === 0 && form.value.options.length === 0) delete payload.options
    customFieldService.update(editingId.value, payload).then(() => {
      closeDialog()
      loadFields()
    })
  } else {
    customFieldService.create(payload).then(() => {
      closeDialog()
      loadFields()
    })
  }
}

function deleteField(id) {
  if (!confirm('Delete this custom field?')) return
  customFieldService.delete(id).then(() => {
    loadFields()
  })
}

onMounted(loadFields)
</script>
