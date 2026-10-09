<template>
  <v-menu :close-on-content-click="false">
    <template #activator="{ props: menuProps }">
      <v-btn v-bind="menuProps" class="user-right--btn" text="Rights" color="amber" />
    </template>
    <v-card min-width="280" class="pa-3">
      <v-card-title class="text-subtitle-1 px-1">Space access</v-card-title>
      <v-checkbox
        v-for="right in rights"
        :key="right.name"
        v-model="selectedRights"
        :value="right.name"
        :label="right.title"
        density="compact"
        hide-details
      />
      <v-btn class="mt-3" color="primary" block :loading="saving" @click="updateRight">Save rights</v-btn>
    </v-card>
  </v-menu>
</template>

<script setup>
import { ref, watch } from 'vue'
import { spaceService } from '@/services'
import { useSpaceCapabilitiesStore } from '@/stores/spaceCapabilities'

const props = defineProps({
  userRight: { type: Object, default: () => ({}) },
  userId: { type: String, required: true },
  spaceId: { type: String, required: true }
})

const emit = defineEmits(['updateUserRightEmit'])
const capabilities = useSpaceCapabilitiesStore()
const saving = ref(false)

const rights = [
  { title: 'Read only', name: 'readOnly' },
  { title: 'Edit test suites and plans', name: 'editPads' },
  { title: 'Edit test cases and sections', name: 'editItems' },
  { title: 'Edit test runs and results', name: 'editRuns' },
  { title: 'Manage bugs', name: 'manageBugs' },
  { title: 'Edit Tech Docs', name: 'editTechDocs' },
  { title: 'Edit tags', name: 'editTags' },
  { title: 'Close or reopen bugs', name: 'closeBugs' },
  { title: 'Edit notes', name: 'editNotes' }
]
const selectedRights = ref([])

watch(() => props.userRight, (val) => {
  if (!val) return
  const rightsObject = typeof val === 'string' ? JSON.parse(val || '{}') : val
  selectedRights.value = rights.filter(({ name }) => {
    const defaultValue = ['manageBugs', 'editTechDocs'].includes(name)
    return (rightsObject?.[name] ?? defaultValue) === true
  }).map(({ name }) => name)
}, { immediate: true })

async function updateRight() {
  const selected = new Set(selectedRights.value)
  const rightObj = Object.fromEntries(rights.map(({ name }) => [name, selected.has(name)]))
  saving.value = true
  try {
    await spaceService.updateUser(props.spaceId, props.userId, rightObj)
    await capabilities.load(props.spaceId, { force: true })
    emit('updateUserRightEmit')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
</style>
