<template>
  <v-dialog :model-value="modelValue" max-width="450" @update:model-value="$emit('update:modelValue', $event)">
    <v-card>
      <v-card-title>{{ title }}</v-card-title>
      <v-card-text>
        <v-text-field :model-value="name" label="Name" required autofocus @update:model-value="$emit('update:name', $event)" />
        <v-textarea :model-value="description" label="Description (optional)" rows="2" @update:model-value="$emit('update:description', $event)" />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="$emit('update:modelValue', false)">Cancel</v-btn>
        <v-btn color="primary" @click="$emit('save')">{{ isRename ? 'Save' : 'Add' }}</v-btn>
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
  description: { type: String, default: '' }
})

const title = computed(() => {
  if (props.isRename) return 'Rename Section'
  return 'Add Section'
})

defineEmits(['update:modelValue', 'update:name', 'update:description', 'save'])
</script>
