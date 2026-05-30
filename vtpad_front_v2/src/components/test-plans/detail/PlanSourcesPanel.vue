<template>
  <!-- Cases -->
  <v-card class="mb-4">
    <v-card-title class="d-flex align-center">
      <v-icon class="mr-2">mdi-test-tube</v-icon>
      Cases
      <v-spacer />
      <v-chip size="small" color="primary">{{ (plan.case_ids || []).length }}</v-chip>
    </v-card-title>
    <v-divider />
    <v-card-text>
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

      <v-list density="compact" style="max-height: 320px; overflow-y: auto;">
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
            <span v-if="tc.suite" class="text-caption text-medium-emphasis ml-1">{{ tc.suite.name }}</span>
            <span v-else class="text-caption text-medium-emphasis ml-1">No suite</span>
          </v-list-item-subtitle>
        </v-list-item>

        <v-list-item v-if="loadingCases" class="justify-center">
          <v-progress-circular indeterminate size="24" color="primary" />
        </v-list-item>

        <v-list-item v-else-if="casesHasMore" class="justify-center pa-0">
          <v-btn
            v-element-visibility="loadMoreCases"
            variant="text"
            size="small"
            block
            @click="loadMoreCases"
          >
            Load more
          </v-btn>
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
          :to="`/space/${plan.space_id}/test-runs/${run.id}`"
        >
          <v-list-item-title>{{ run.name }}</v-list-item-title>
          <v-list-item-subtitle>
            <v-chip size="x-small" :color="runStatusColor(run.status)">{{ run.status }}</v-chip>
          </v-list-item-subtitle>
        </v-list-item>
      </v-list>
      <v-empty-state v-else icon="mdi-play-circle-outline" text="No runs yet. Create one from the button above." />
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { vElementVisibility } from '@vueuse/components'

const props = defineProps({
  plan: { type: Object, required: true },
  loadingCases: { type: Boolean, default: false },
  casesHasMore: { type: Boolean, default: false },
  selectedCases: { type: Array, default: () => [] },
  caseSearch: { type: String, default: '' },
  savingCases: { type: Boolean, default: false },
  filteredAvailableCases: { type: Array, default: () => [] },
  runs: { type: Array, default: () => [] },
  isCaseInPlan: { type: Function, default: () => false },
})

const emit = defineEmits([
  'update:selectedCases',
  'update:caseSearch',
  'add-cases',
  'select-all-available',
  'deselect-all',
  'load-more-cases',
])

const localCaseSearch = computed({
  get: () => props.caseSearch,
  set: (v) => emit('update:caseSearch', v),
})

const localSelectedCases = computed({
  get: () => props.selectedCases,
  set: (v) => emit('update:selectedCases', v),
})

function loadMoreCases() {
  emit('load-more-cases')
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
