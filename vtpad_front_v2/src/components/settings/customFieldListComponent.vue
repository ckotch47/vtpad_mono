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
          <v-textarea v-model="optionsText" label="Options (one per line, for select/multiselect)" rows="3" />
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
  sort: 0
})
const cfForm = ref(null)
const fieldTypes = ['text', 'select', 'multiselect', 'number', 'date', 'checkbox']
const entityTypes = ['testcase', 'testrun']

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
    sort: field.sort || 0
  }
  showCreateDialog.value = true
}

function closeDialog() {
  showCreateDialog.value = false
  editingId.value = null
  form.value = { name: '', field_type: 'text', entity_type: 'testcase', options: [], sort: 0 }
  formValid.value = false
  nextTick(() => cfForm.value?.resetValidation())
}

function saveField() {
  const payload = {
    ...form.value,
    space_id: spaceId.value
  }
  if (editingId.value) {
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
