<template>
  <!-- Suites -->
  <v-card class="mb-4">
    <v-card-title class="d-flex align-center">
      <v-icon class="mr-2">mdi-folder-open</v-icon>
      Suites
      <v-spacer />
      <v-chip size="small" color="primary">{{ (plan.suite_ids || []).length }}</v-chip>
    </v-card-title>
    <v-divider />
    <v-card-text>
      <v-select
        v-model="localEditSuiteIds"
        :items="allSuites"
        item-title="name"
        item-value="id"
        label="Select suites"
        multiple
        chips
        clearable
        hide-details
      />
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn size="small" variant="text" :disabled="!suiteIdsChanged" @click="$emit('reset-suites')">
        Reset
      </v-btn>
      <v-btn color="primary" :disabled="!suiteIdsChanged" :loading="savingSuites" @click="$emit('save-suites')">
        Save Suites
      </v-btn>
    </v-card-actions>
  </v-card>

  <!-- Sections -->
  <v-card class="mb-4">
    <v-card-title class="d-flex align-center">
      <v-icon class="mr-2">mdi-folder-multiple</v-icon>
      Sections
      <v-spacer />
      <v-chip size="small" color="primary">{{ (plan.section_ids || []).length }}</v-chip>
    </v-card-title>
    <v-divider />
    <v-card-text>
      <div v-if="(plan.section_ids || []).length" class="mb-3">
        <div class="text-caption text-medium-emphasis mb-1">Current sections</div>
        <div class="d-flex flex-wrap ga-1">
          <v-chip
            v-for="sid in plan.section_ids"
            :key="sid"
            size="small"
            closable
            @click:close="$emit('remove-section', sid)"
          >
            {{ sectionName(sid) }}
          </v-chip>
        </div>
      </div>
      <v-divider v-if="(plan.section_ids || []).length" class="mb-3" />
      <v-select
        v-model="localSectionSourceSuite"
        :items="allSuites"
        item-title="name"
        item-value="id"
        label="Select suite"
        hide-details
        class="mb-3"
      />
      <v-select
        v-model="localEditSectionIds"
        :items="sourceSections"
        item-title="name"
        item-value="id"
        label="Select sections to add"
        multiple
        chips
        clearable
        hide-details
        :disabled="!localSectionSourceSuite"
      />
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn color="primary" :disabled="localEditSectionIds.length === 0" :loading="savingSections" @click="$emit('save-sections')">
        Add Sections
      </v-btn>
    </v-card-actions>
  </v-card>

  <!-- Individual Cases -->
  <v-card class="mb-4">
    <v-card-title class="d-flex align-center">
      <v-icon class="mr-2">mdi-test-tube</v-icon>
      Individual Cases
      <v-spacer />
      <v-chip size="small" color="primary">{{ (plan.case_ids || []).length }}</v-chip>
    </v-card-title>
    <v-divider />
    <v-card-text>
      <v-select
        v-model="localCaseSourceSuites"
        :items="allSuites"
        item-title="name"
        item-value="id"
        label="Select suites"
        multiple
        chips
        clearable
        hide-details
        class="mb-3"
      />

      <v-select
        v-model="localCaseSourceSections"
        :items="caseSourceSectionsList"
        item-title="name"
        item-value="id"
        label="Select sections"
        multiple
        chips
        clearable
        hide-details
        class="mb-3"
        :disabled="caseSourceSectionsList.length === 0"
      />

      <v-text-field
        v-model="localCaseSearch"
        label="Search cases"
        prepend-inner-icon="mdi-magnify"
        density="compact"
        hide-details
        variant="outlined"
        class="mb-2"
        clearable
      />

      <div class="d-flex align-center mb-2">
        <v-btn size="small" variant="text" prepend-icon="mdi-checkbox-multiple-marked" :disabled="filteredAvailableCases.length === 0" @click="$emit('select-all-available')">
          Select All
        </v-btn>
        <v-btn size="small" variant="text" prepend-icon="mdi-checkbox-multiple-blank-outline" :disabled="localSelectedCases.length === 0" @click="$emit('deselect-all')">
          Deselect All
        </v-btn>
        <v-spacer />
        <span class="text-caption text-medium-emphasis">{{ localSelectedCases.length }} selected</span>
      </div>

      <v-list density="compact" style="max-height: 280px; overflow-y: auto;">
        <v-list-item
          v-for="tc in filteredAvailableCases"
          :key="tc.id"
          :disabled="isCaseInPlan(tc.id)"
        >
          <template #prepend>
            <v-checkbox-btn
              v-model="localSelectedCases"
              :value="tc.id"
              :disabled="isCaseInPlan(tc.id)"
            />
          </template>
          <v-list-item-title>{{ tc.title }}</v-list-item-title>
          <v-list-item-subtitle>
            <v-chip size="x-small" :color="typeColor(tc.type)">{{ tc.type }}</v-chip>
            <span class="text-caption text-medium-emphasis ml-1">{{ tc.suite?.name }}</span>
          </v-list-item-subtitle>
        </v-list-item>
      </v-list>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn color="primary" :disabled="localSelectedCases.length === 0" :loading="savingCases" @click="$emit('add-cases')">
        Add {{ localSelectedCases.length ? `(${localSelectedCases.length})` : '' }}
      </v-btn>
    </v-card-actions>
  </v-card>

  <!-- Runs -->
  <v-card>
    <v-card-title>Runs from this Plan</v-card-title>
    <v-card-text>
      <v-list v-if="runs.length" density="compact">
        <v-list-item
          v-for="run in runs"
          :key="run.id"
          :to="`/space/${spaceId}/test-runs/${run.id}`"
        >
          <v-list-item-title>{{ run.name }}</v-list-item-title>
          <v-list-item-subtitle>
            <v-chip size="x-small" :color="runStatusColor(run.status)">{{ run.status }}</v-chip>
          </v-list-item-subtitle>
        </v-list-item>
      </v-list>
      <v-empty-state v-else icon="mdi-play-circle-outline" text="No runs yet" />
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  plan: { type: Object, default: () => ({}) },
  allSuites: { type: Array, default: () => [] },
  allSections: { type: Array, default: () => [] },
  editSuiteIds: { type: Array, default: () => [] },
  savingSuites: { type: Boolean, default: false },
  suiteIdsChanged: { type: Boolean, default: false },
  sectionSourceSuite: { type: String, default: null },
  sourceSections: { type: Array, default: () => [] },
  editSectionIds: { type: Array, default: () => [] },
  savingSections: { type: Boolean, default: false },
  caseSourceSuites: { type: Array, default: () => [] },
  caseSourceSections: { type: Array, default: () => [] },
  caseSourceSectionsList: { type: Array, default: () => [] },
  availableCases: { type: Array, default: () => [] },
  selectedCases: { type: Array, default: () => [] },
  caseSearch: { type: String, default: '' },
  savingCases: { type: Boolean, default: false },
  filteredAvailableCases: { type: Array, default: () => [] },
  runs: { type: Array, default: () => [] },
  caseMap: { type: Object, default: () => ({}) },
  isCaseInPlan: { type: Function, default: () => false },
})

const emit = defineEmits([
  'update:editSuiteIds', 'save-suites', 'reset-suites',
  'update:sectionSourceSuite', 'update:editSectionIds', 'save-sections', 'remove-section',
  'update:caseSourceSuites', 'update:caseSourceSections', 'update:caseSearch',
  'update:selectedCases', 'add-cases', 'remove-case',
  'select-all-available', 'deselect-all',
])

function proxy(propName) {
  const eventName = `update:${propName}`
  return computed({
    get: () => props[propName],
    set: (val) => emit(eventName, val)
  })
}

const localEditSuiteIds = proxy('editSuiteIds')
const localSectionSourceSuite = proxy('sectionSourceSuite')
const localEditSectionIds = proxy('editSectionIds')
const localCaseSourceSuites = proxy('caseSourceSuites')
const localCaseSourceSections = proxy('caseSourceSections')
const localCaseSearch = proxy('caseSearch')
const localSelectedCases = proxy('selectedCases')

const route = useRoute()
const spaceId = computed(() => route.params.spaceId)

function sectionName(sectionId) {
  const found = props.allSections.find(s => s.id === sectionId)
  return found?.name || sectionId
}

function typeColor(type) {
  const map = { manual: 'info', checklist: 'success', automated: 'warning' }
  return map[type] || 'grey'
}

function runStatusColor(status) {
  const map = { draft: 'grey', active: 'primary', completed: 'success' }
  return map[status] || 'grey'
}
</script>
