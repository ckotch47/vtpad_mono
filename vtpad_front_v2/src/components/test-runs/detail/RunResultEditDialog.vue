<template>
  <v-dialog :model-value="modelValue" max-width="600" scrollable @update:model-value="$emit('update:modelValue', $event)">
    <v-card v-if="result">
      <v-card-title class="d-flex align-center">
        <span>Update Result</span>
        <v-spacer />
        <v-btn v-if="result.status === 'failed'" color="error" size="small" prepend-icon="mdi-bug" @click="$emit('create-bug')">
          Create Bug
        </v-btn>
      </v-card-title>
      <v-divider />
      <v-card-text>
        <div class="text-subtitle-1 font-weight-medium mb-3">{{ result.testcase?.title }}</div>
        <v-select
          :model-value="result.status"
          :items="['not_run','passed','failed','blocked','skipped']"
          label="Status"
          class="mb-2"
          @update:model-value="updateField('status', $event)"
        />
        <v-text-field
          :model-value="result.duration_seconds"
          label="Duration (seconds)"
          type="number"
          class="mb-2"
          @update:model-value="updateField('duration_seconds', $event)"
        />
        <v-textarea :model-value="result.comment" label="Comment" rows="2" class="mb-2" @update:model-value="updateField('comment', $event)" />
        <v-combobox
          :model-value="result.linked_bug_ids"
          :items="spaceBugs"
          item-title="short_name"
          item-value="short_name"
          label="Linked Bugs"
          multiple
          chips
          closable-chips
          clearable
          :return-object="false"
          @update:model-value="updateField('linked_bug_ids', $event)"
        />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="$emit('update:modelValue', false)">Cancel</v-btn>
        <v-btn color="primary" @click="$emit('save')">Save</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Boolean, default: false },
  result: { type: Object, default: null },
  spaceBugs: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue', 'update:result', 'save', 'create-bug'])

function updateField(key, value) {
  emit('update:result', { ...props.result, [key]: value })
}
</script>
