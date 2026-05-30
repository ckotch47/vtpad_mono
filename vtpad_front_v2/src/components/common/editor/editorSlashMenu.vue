<template>
  <div class="editor-slash-menu">
    <v-list density="compact" class="py-1">
      <v-list-item
        v-for="(item, index) in items"
        :key="item.title"
        :class="{ 'bg-primary': index === selectedIndex }"
        class="px-3 py-1"
        @click="selectItem(index)"
        @mouseenter="selectedIndex = index"
      >
        <template #prepend>
          <v-icon :icon="item.icon" size="small" class="mr-2" />
        </template>
        <v-list-item-title class="text-body-2">{{ item.title }}</v-list-item-title>
        <v-list-item-subtitle class="text-caption">{{ item.description }}</v-list-item-subtitle>
      </v-list-item>
    </v-list>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  command: { type: Function, required: true }
})

const selectedIndex = ref(0)

watch(() => props.items, () => { selectedIndex.value = 0 })

function selectItem(index) {
  const item = props.items[index]
  if (item) props.command(item)
}

function onKeyDown({ event }) {
  if (event.key === 'ArrowUp') {
    selectedIndex.value = (selectedIndex.value + props.items.length - 1) % props.items.length
    return true
  }
  if (event.key === 'ArrowDown') {
    selectedIndex.value = (selectedIndex.value + 1) % props.items.length
    return true
  }
  if (event.key === 'Enter') {
    selectItem(selectedIndex.value)
    return true
  }
  return false
}

defineExpose({ onKeyDown })
</script>

<style scoped>
.editor-slash-menu {
  background: rgb(var(--v-theme-surface));
  border: 1px solid rgba(var(--v-border-color), 0.35);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  overflow: hidden;
  min-width: 220px;
}
</style>
