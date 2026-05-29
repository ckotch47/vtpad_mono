<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>
  <div v-if="!loader" class="mx-auto my-2">
    <div class="d-flex justify-space-between align-center mb-4">
      <h2>Milestones</h2>
      <v-btn color="primary" @click="showCreateDialog = true">Add Milestone</v-btn>
    </div>

    <v-card v-if="milestones.length">
      <v-list>
        <v-list-item v-for="milestone in milestones" :key="milestone.id">
          <template #prepend>
            <v-icon :color="milestone.status === 'closed' ? 'grey' : 'primary'">mdi-flag</v-icon>
          </template>
          <v-list-item-title>
            {{ milestone.title }}
            <v-chip v-if="milestone.status === 'closed'" size="small" color="grey" class="ml-2">Closed</v-chip>
          </v-list-item-title>
          <v-list-item-subtitle>
            <span v-if="milestone.start_date">Start: {{ formatDate(milestone.start_date) }}</span>
            <span v-if="milestone.end_date" class="ml-2">End: {{ formatDate(milestone.end_date) }}</span>
          </v-list-item-subtitle>
          <template #append>
            <v-btn v-if="milestone.status !== 'closed'" color="success" size="small" class="mr-2" @click="closeMilestone(milestone.id)">Close</v-btn>
            <v-btn icon variant="text" @click="editMilestone(milestone)">
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
            <v-btn icon variant="text" color="red" @click="deleteMilestone(milestone.id)">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </v-list>
    </v-card>
    <v-card v-else class="pa-4">
      <p>No milestones yet.</p>
    </v-card>
  </div>

  <v-dialog v-model="showCreateDialog" max-width="500">
    <v-card>
      <v-card-title>{{ editingId ? 'Edit' : 'Add' }} Milestone</v-card-title>
      <v-card-text>
        <v-form ref="msForm" v-model="formValid">
          <v-text-field v-model="form.title" label="Title" :rules="[v => !!v || 'Title is required']" required />
          <v-textarea v-model="form.description" label="Description" rows="2" />
          <v-text-field v-model="form.start_date" label="Start date (YYYY-MM-DD)" />
          <v-text-field v-model="form.end_date" label="End date (YYYY-MM-DD)" />
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="closeDialog">Cancel</v-btn>
        <v-btn color="primary" :disabled="!formValid" @click="saveMilestone">{{ editingId ? 'Update' : 'Create' }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { milestoneService } from '@/services'

const route = useRoute()
const spaceId = computed(() => route.params.spaceId)

const loader = ref(true)
const milestones = ref([])
const showCreateDialog = ref(false)
const editingId = ref(null)
const formValid = ref(false)
const form = ref({
  title: '',
  description: '',
  start_date: '',
  end_date: ''
})
const msForm = ref(null)

function loadMilestones() {
  loader.value = true
  milestoneService.list(spaceId.value).then(res => {
    milestones.value = res.data
    loader.value = false
  }).catch(() => {
    loader.value = false
  })
}

function editMilestone(milestone) {
  editingId.value = milestone.id
  form.value = {
    title: milestone.title,
    description: milestone.description || '',
    start_date: milestone.start_date || '',
    end_date: milestone.end_date || ''
  }
  showCreateDialog.value = true
}

function closeDialog() {
  showCreateDialog.value = false
  editingId.value = null
  form.value = { title: '', description: '', start_date: '', end_date: '' }
  formValid.value = false
  nextTick(() => msForm.value?.resetValidation())
}

function saveMilestone() {
  const payload = {
    ...form.value,
    space_id: spaceId.value
  }
  if (editingId.value) {
    milestoneService.update(editingId.value, payload).then(() => {
      closeDialog()
      loadMilestones()
    })
  } else {
    milestoneService.create(payload).then(() => {
      closeDialog()
      loadMilestones()
    })
  }
}

function closeMilestone(id) {
  milestoneService.close(id).then(() => {
    loadMilestones()
  })
}

function deleteMilestone(id) {
  if (!confirm('Delete this milestone?')) return
  milestoneService.delete(id).then(() => {
    loadMilestones()
  })
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}

onMounted(loadMilestones)
</script>
