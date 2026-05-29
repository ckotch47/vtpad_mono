<template>
  <v-dialog :model-value="modelValue" max-width="900" scrollable @update:model-value="$emit('update:modelValue', $event)">
    <v-card v-if="testCase">
      <v-card-title class="d-flex align-center py-3">
        <span class="text-truncate" style="max-width: 500px">{{ testCase.title }}</span>
        <v-spacer />
        <v-chip size="small" :color="typeColor(testCase.type)" class="mr-1">{{ testCase.type }}</v-chip>
        <v-chip size="small" :color="statusColor(testCase.status)">{{ testCase.status }}</v-chip>
        <v-btn
          icon="mdi-pencil"
          size="small"
          variant="text"
          class="ml-2"
          :to="`/space/${spaceId}/test-cases/${testCase.id}/edit`"
          @click="$emit('edit')"
        />
        <v-btn icon="mdi-close" size="small" variant="text" @click="$emit('update:modelValue', false)" />
      </v-card-title>
      <v-divider />
      <v-card-text class="py-4">
        <div v-if="testCase.text">
          <div class="text-subtitle-2 text-medium-emphasis mb-2">Description</div>
          <editor-component :text="testCase.text" :edit="false" />
        </div>
        <div v-if="testCase.preconditions" class="mt-4">
          <div class="text-subtitle-2 text-medium-emphasis mb-2">Preconditions</div>
          <editor-component :text="testCase.preconditions" :edit="false" />
        </div>
        <div v-if="testCase.steps" class="mt-4">
          <div class="text-subtitle-2 text-medium-emphasis mb-2">Steps</div>
          <editor-component :text="testCase.steps" :edit="false" />
        </div>
        <div v-if="testCase.expected_results" class="mt-4">
          <div class="text-subtitle-2 text-medium-emphasis mb-2">Expected Results</div>
          <editor-component :text="testCase.expected_results" :edit="false" />
        </div>
        <div v-if="!hasContent(testCase)" class="text-center text-grey py-8">
          No content
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import EditorComponent from '@/components/common/editor/editorComponent.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  testCase: { type: Object, default: null }
})

defineEmits(['update:modelValue', 'edit'])

const route = useRoute()
const spaceId = computed(() => route.params.spaceId)

function hasContent(tc) {
  return tc?.text || tc?.preconditions || tc?.steps || tc?.expected_results
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
