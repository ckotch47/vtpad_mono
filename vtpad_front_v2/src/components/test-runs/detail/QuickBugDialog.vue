<template>
  <v-dialog :model-value="modelValue" max-width="560" @update:model-value="$emit('update:modelValue', $event)">
    <v-card>
      <v-card-title>Create Bug</v-card-title>
      <v-card-text>
        <v-text-field :model-value="bug.title" label="Title" required autofocus @update:model-value="updateBug('title', $event)" />
        <v-textarea :model-value="bug.steps" label="Steps to Reproduce" rows="3" @update:model-value="updateBug('steps', $event)" />
        <v-textarea :model-value="bug.expected" label="Expected Result" rows="2" @update:model-value="updateBug('expected', $event)" />
        <v-textarea :model-value="bug.actual" label="Actual Result" rows="2" @update:model-value="updateBug('actual', $event)" />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="$emit('update:modelValue', false)">Cancel</v-btn>
        <v-btn color="error" @click="$emit('create')">Create Bug</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Boolean, default: false },
  bug: { type: Object, default: () => ({ title: '', steps: '', expected: '', actual: '' }) }
})

const emit = defineEmits(['update:modelValue', 'update:bug', 'create'])

function updateBug(key, value) {
  emit('update:bug', { ...props.bug, [key]: value })
}
</script>
