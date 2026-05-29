<template>
  <v-card v-if="selectedSection">
    <v-card-title class="d-flex align-center flex-wrap py-3">
      <v-icon class="mr-2">mdi-test-tube</v-icon>
      {{ selectedSection.name }}
      <v-chip size="small" class="ml-2" color="primary">{{ filteredTestCases.length }}</v-chip>
      <v-spacer />
      <v-text-field
        :model-value="caseSearch"
        label="Search cases"
        prepend-inner-icon="mdi-magnify"
        density="compact"
        hide-details
        variant="outlined"
        class="mr-2 mt-2 mt-md-0"
        style="max-width: 260px"
        clearable
        @update:model-value="$emit('update:caseSearch', $event)"
      />
      <v-btn size="small" variant="outlined" prepend-icon="mdi-playlist-plus" class="mr-2 mt-2 mt-md-0" @click="$emit('open-add-existing')">
        Existing
      </v-btn>
      <v-btn size="small" color="primary" prepend-icon="mdi-plus" class="mt-2 mt-md-0" @click="$emit('open-add-new')">
        New
      </v-btn>
    </v-card-title>
    <v-divider />
    <v-card-text class="pa-0">
      <v-list density="compact">
        <v-list-item
          v-for="tc in filteredTestCases"
          :key="tc.id"
          class="case-item"
          @click="$emit('view-case', tc.id)"
        >
          <template #prepend>
            <v-icon :color="typeColor(tc.type)">{{ typeIcon(tc.type) }}</v-icon>
          </template>
          <v-list-item-title class="font-weight-medium">{{ tc.title }}</v-list-item-title>
          <v-list-item-subtitle>
            <v-chip size="x-small" :color="statusColor(tc.status)" class="mr-1">{{ tc.status }}</v-chip>
            <span v-if="tc.short_name" class="text-caption text-medium-emphasis">{{ tc.short_name }}</span>
          </v-list-item-subtitle>
          <template #append>
            <v-btn icon="mdi-link-off" size="x-small" variant="text" color="grey" title="Remove from section" @click.prevent="$emit('remove-case', tc.id)" />
          </template>
        </v-list-item>
      </v-list>
      <v-empty-state v-if="filteredTestCases.length === 0" icon="mdi-test-tube-off" text="No test cases in this section" />
    </v-card-text>
  </v-card>

  <v-card v-else class="text-center pa-10" variant="outlined">
    <v-icon size="64" color="grey-lighten-1">mdi-shape-outline</v-icon>
    <div class="text-h6 text-grey mt-4">Select a section to view test cases</div>
    <div class="text-body-2 text-grey mt-1">Choose a section from the left panel or create a new one</div>
  </v-card>

  <!-- Add Existing Cases Dialog -->
  <v-dialog :model-value="openAddExistingCase" max-width="560" @update:model-value="$emit('update:openAddExistingCase', $event)">
    <v-card>
      <v-card-title>Add Existing Test Cases</v-card-title>
      <v-card-text>
        <v-text-field
          :model-value="existingCaseSearch"
          label="Search"
          prepend-inner-icon="mdi-magnify"
          density="compact"
          hide-details
          class="mb-3"
          clearable
          autofocus
          @update:model-value="$emit('update:existingCaseSearch', $event)"
        />
        <v-list density="compact" style="max-height: 400px; overflow-y: auto;">
          <v-list-item v-for="tc in filteredExistingCases" :key="tc.id" :value="tc.id">
            <template #prepend>
              <v-checkbox-btn :model-value="selectedExistingCases" :value="tc.id" @update:model-value="$emit('update:selectedExistingCases', $event)" />
            </template>
            <v-list-item-title>{{ tc.title }}</v-list-item-title>
            <v-list-item-subtitle>
              <v-chip size="x-small" :color="typeColor(tc.type)">{{ tc.type }}</v-chip>
              <span class="text-caption text-medium-emphasis ml-1">{{ tc.status }}</span>
            </v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="$emit('update:openAddExistingCase', false)">Cancel</v-btn>
        <v-btn color="primary" :disabled="selectedExistingCases.length === 0" @click="$emit('add-existing-cases')">
          Add {{ selectedExistingCases.length ? `(${selectedExistingCases.length})` : '' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Add New Test Case Dialog -->
  <v-dialog :model-value="openAddCase" max-width="500" @update:model-value="$emit('update:openAddCase', $event)">
    <v-card>
      <v-card-title>Add Test Case</v-card-title>
      <v-card-text>
        <v-text-field :model-value="newCase.title" label="Title" required autofocus @update:model-value="updateNewCase('title', $event)" />
        <v-select
          :model-value="newCase.type"
          :items="[{title:'Manual', value:'manual'}, {title:'Checklist', value:'checklist'}, {title:'Automated', value:'automated'}]"
          item-title="title"
          item-value="value"
          label="Type"
          @update:model-value="updateNewCase('type', $event)"
        />
        <v-textarea :model-value="newCase.steps" label="Steps" rows="3" @update:model-value="updateNewCase('steps', $event)" />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="$emit('update:openAddCase', false)" :disabled="creatingCase">Cancel</v-btn>
        <v-btn color="primary" :loading="creatingCase" :disabled="creatingCase" @click="$emit('add-new-case')">Add</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
const props = defineProps({
  selectedSection: { type: Object, default: null },
  filteredTestCases: { type: Array, default: () => [] },
  caseSearch: { type: String, default: '' },
  openAddCase: { type: Boolean, default: false },
  openAddExistingCase: { type: Boolean, default: false },
  existingCases: { type: Array, default: () => [] },
  selectedExistingCases: { type: Array, default: () => [] },
  existingCaseSearch: { type: String, default: '' },
  newCase: { type: Object, default: () => ({ title: '', type: 'manual', steps: '' }) },
  creatingCase: { type: Boolean, default: false },
  filteredExistingCases: { type: Array, default: () => [] }
})

const emit = defineEmits([
  'update:caseSearch', 'view-case', 'remove-case',
  'update:openAddCase', 'open-add-new',
  'update:openAddExistingCase', 'open-add-existing',
  'update:selectedExistingCases', 'update:existingCaseSearch', 'add-existing-cases',
  'update:newCase', 'add-new-case'
])

function updateNewCase(key, value) {
  emit('update:newCase', { ...props.newCase, [key]: value })
}

function typeIcon(type) {
  const map = { manual: 'mdi-hand-back-right-outline', checklist: 'mdi-check-box-outline', automated: 'mdi-robot' }
  return map[type] || 'mdi-test-tube'
}

function typeColor(type) {
  const map = { manual: 'info', checklist: 'success', automated: 'warning' }
  return map[type] || 'grey'
}

function statusColor(status) {
  const map = { draft: 'grey', active: 'success', deprecated: 'error' }
  return map[status] || 'grey'
}
</script>

<style scoped>
.case-item {
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}
.case-item:last-child {
  border-bottom: none;
}
</style>
