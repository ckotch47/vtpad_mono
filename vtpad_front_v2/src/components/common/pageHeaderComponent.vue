<template>
  <div class="d-flex justify-space-between align-center mb-4">
    <div>
      <h1 class="text-h4 font-weight-bold">{{ title }}</h1>
      <p v-if="subtitle" class="text-subtitle-2 text-medium-emphasis mt-1">{{ subtitle }}</p>
    </div>
    <div v-if="$slots.actions" class="d-flex align-center gap-2">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' }
})
</script>
