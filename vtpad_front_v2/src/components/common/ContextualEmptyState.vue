<template>
  <v-empty-state :icon="icon" :title="title" :text="text" class="contextual-empty-state">
    <template v-if="actionLabel" #actions>
      <v-btn color="primary" variant="tonal" :prepend-icon="actionIcon" @click="$emit('action')">
        {{ actionLabel }}
      </v-btn>
    </template>
  </v-empty-state>
</template>

<script setup>
defineProps({
  icon: { type: String, default: 'mdi-inbox-outline' },
  title: { type: String, required: true },
  text: { type: String, required: true },
  actionLabel: { type: String, default: '' },
  actionIcon: { type: String, default: '' },
})

defineEmits(['action'])
</script>

<style scoped>
.contextual-empty-state {
  min-height: 180px;
}
</style>
