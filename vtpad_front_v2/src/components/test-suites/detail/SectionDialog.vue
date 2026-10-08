<template>
  <v-dialog :model-value="modelValue" max-width="450" @update:model-value="$emit('update:modelValue', $event)">
    <v-card
      data-keyboard-save-scope
      :data-keyboard-escape-confirm="isDirty ? 'Discard section changes?' : null"
      :data-keyboard-escape-saving="saving ? 'true' : null"
    >
      <v-card-title>{{ title }}</v-card-title>
      <v-card-text>
        <v-text-field :model-value="name" label="Name" required autofocus @update:model-value="$emit('update:name', $event)" />
        <v-textarea :model-value="description" label="Description (optional)" rows="2" @update:model-value="$emit('update:description', $event)" />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="$emit('update:modelValue', false)">Cancel</v-btn>
        <v-btn color="primary" data-keyboard-save-action :loading="saving" :disabled="saving || !name.trim()" @click="$emit('save')">{{ isRename ? 'Save' : 'Add' }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  modelValue: { type: Boolean, default: false },
  isRename: { type: Boolean, default: false },
  name: { type: String, default: '' },
  description: { type: String, default: '' },
  saving: { type: Boolean, default: false },
  isDirty: { type: Boolean, default: false }
})

const title = computed(() => {
  if (props.isRename) return 'Rename Section'
  return 'Add Section'
})

defineEmits(['update:modelValue', 'update:name', 'update:description', 'save'])
</script>
