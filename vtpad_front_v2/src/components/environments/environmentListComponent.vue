<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>
  <div v-if="!loader" class="mx-auto my-2">
    <div class="d-flex justify-space-between align-center mb-4">
      <h2>Environments</h2>
      <v-btn v-if="canManageRuns" color="primary" @click="showCreateDialog = true">Add Environment</v-btn>
    </div>

    <v-card v-if="environments.length">
      <v-list>
        <v-list-item v-for="env in environments" :key="env.id">
          <template #prepend>
            <v-icon>mdi-desktop-classic</v-icon>
          </template>
          <v-list-item-title>{{ env.name }}</v-list-item-title>
          <v-list-item-subtitle>
            <span v-if="env.os">OS: {{ env.os }}</span>
            <span v-if="env.browser" class="ml-2">Browser: {{ env.browser }}</span>
            <span v-if="env.url" class="ml-2">URL: {{ env.url }}</span>
          </v-list-item-subtitle>
          <template #append>
            <v-btn v-if="canManageRuns" icon variant="text" @click="editEnvironment(env)">
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
            <v-btn v-if="canManageRuns" icon variant="text" color="red" @click="deleteEnvironment(env.id)">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </v-list>
    </v-card>
    <v-card v-else class="pa-4">
      <p>{{ canManageRuns ? 'No environments yet.' : 'No environments are available in this space.' }}</p>
    </v-card>
  </div>

  <v-dialog v-model="showCreateDialog" max-width="500">
    <v-card>
      <v-card-title>{{ editingId ? 'Edit' : 'Add' }} Environment</v-card-title>
      <v-card-text>
        <v-form ref="envForm" v-model="formValid">
          <v-text-field v-model="form.name" label="Name" :rules="[v => !!v || 'Name is required']" required />
          <v-text-field v-model="form.os" label="OS" />
          <v-text-field v-model="form.browser" label="Browser" />
          <v-text-field v-model="form.url" label="URL" />
          <v-textarea v-model="variablesText" label="Variables (JSON)" rows="3" />
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="closeDialog">Cancel</v-btn>
        <v-btn color="primary" :disabled="!formValid" @click="saveEnvironment">{{ editingId ? 'Update' : 'Create' }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { environmentService } from '@/services'
import { useSpaceCapabilitiesStore } from '@/stores/spaceCapabilities'

const route = useRoute()
const spaceId = computed(() => route.params.spaceId)
const capabilityStore = useSpaceCapabilitiesStore()
const canManageRuns = computed(() => capabilityStore.can(spaceId.value, 'runs'))

const loader = ref(true)
const environments = ref([])
const showCreateDialog = ref(false)
const editingId = ref(null)
const formValid = ref(false)
const form = ref({
  name: '',
  os: '',
  browser: '',
  url: '',
  variables: {}
})
const envForm = ref(null)

const variablesText = computed({
  get() {
    return JSON.stringify(form.value.variables, null, 2)
  },
  set(val) {
    try {
      form.value.variables = JSON.parse(val)
    } catch {
      form.value.variables = {}
    }
  }
})

function loadEnvironments() {
  loader.value = true
  environmentService.list(spaceId.value).then(res => {
    environments.value = res.data
    loader.value = false
  }).catch(() => {
    loader.value = false
  })
}

function editEnvironment(env) {
  editingId.value = env.id
  form.value = {
    name: env.name,
    os: env.os || '',
    browser: env.browser || '',
    url: env.url || '',
    variables: env.variables || {}
  }
  showCreateDialog.value = true
}

function closeDialog() {
  showCreateDialog.value = false
  editingId.value = null
  form.value = { name: '', os: '', browser: '', url: '', variables: {} }
  formValid.value = false
  nextTick(() => envForm.value?.resetValidation())
}

function saveEnvironment() {
  const payload = {
    ...form.value,
    space_id: spaceId.value
  }
  if (editingId.value) {
    environmentService.update(editingId.value, payload).then(() => {
      closeDialog()
      loadEnvironments()
    })
  } else {
    environmentService.create(payload).then(() => {
      closeDialog()
      loadEnvironments()
    })
  }
}

function deleteEnvironment(id) {
  if (!confirm('Delete this environment?')) return
  environmentService.delete(id).then(() => {
    loadEnvironments()
  })
}

watch(spaceId, id => {
  if (!id) return
  capabilityStore.load(id)
  loadEnvironments()
}, { immediate: true })
</script>
