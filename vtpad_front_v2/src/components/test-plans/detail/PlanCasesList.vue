<template>
  <v-card>
    <v-card-title class="d-flex align-center">
      <span>Cases in Plan</span>
      <v-spacer />
      <v-chip size="small" color="primary">{{ cases.length }}</v-chip>
    </v-card-title>
    <v-divider />
    <v-card-text class="pa-0">
      <v-list density="compact">
        <v-list-item
          v-for="tc in cases"
          :key="tc.id"
          class="case-item"
          @click="$emit('view-case', tc.id)"
        >
          <template #prepend>
            <v-icon :color="typeColor(tc.type)">{{ typeIcon(tc.type) }}</v-icon>
          </template>
          <v-list-item-title>{{ tc.title }}</v-list-item-title>
          <v-list-item-subtitle>
            <v-chip size="x-small" :color="statusColor(tc.status)">{{ tc.status }}</v-chip>
            <span v-if="tc.suite" class="text-caption text-medium-emphasis ml-2">
              {{ tc.suite.name }}
            </span>
          </v-list-item-subtitle>
          <template #append>
            <v-btn
              v-if="removableIds.includes(tc.id)"
              icon="mdi-close"
              size="x-small"
              variant="text"
              color="error"
              density="compact"
              @click.stop="$emit('remove-case', tc.id)"
            />
          </template>
        </v-list-item>
      </v-list>
      <v-empty-state
        v-if="cases.length === 0"
        icon="mdi-test-tube-off"
        text="No cases in this plan yet. Add suites, sections, or individual cases."
      />
    </v-card-text>
  </v-card>
</template>

<script setup>
defineProps({
  cases: { type: Array, default: () => [] },
  removableIds: { type: Array, default: () => [] }
})

defineEmits(['view-case', 'remove-case'])

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
  cursor: pointer;
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}
.case-item:last-child {
  border-bottom: none;
}
</style>
