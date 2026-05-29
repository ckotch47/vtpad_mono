<template>
  <v-card flat class="sidebar-card">
    <v-toolbar density="compact" color="surface">
      <v-icon class="ml-2">mdi-book-open-variant</v-icon>
      <v-toolbar-title class="text-subtitle-2">Pages</v-toolbar-title>
      <v-spacer />
      <v-btn icon="mdi-plus" size="small" variant="text" @click="$emit('create')" />
    </v-toolbar>
    <v-card-text class="pa-2 pb-0 tech-doc-list">
      <v-text-field
        v-model="localQuery"
        density="compact"
        variant="outlined"
        hide-details
        clearable
        prepend-inner-icon="mdi-magnify"
        placeholder="Search pages"
      />
    </v-card-text>
    <v-divider />
    <v-card-text ref="containerRef" class="pa-0 tree-container">
      <v-skeleton-loader v-if="loading" type="list-item@5" />
      <v-list v-else density="compact" class="tech-doc-list">
        <v-list-item
          v-for="item in items"
          :key="item.id"
          :active="activeId.includes(item.id)"
          rounded="sm"
          class="tech-doc-list-item"
          @click="$emit('select', [item.id])"
        >
          <template v-slot:prepend>
            <div class="d-flex align-center">
              <div :style="{ width: `${item.level * 14}px` }" />
              <v-icon size="small" :color="item.hasChildren ? 'primary' : 'grey'">
                {{ item.hasChildren ? 'mdi-folder-outline' : 'mdi-file-document-outline' }}
              </v-icon>
            </div>
          </template>
          <v-list-item-title class="text-body-2" :class="{ 'font-weight-medium': activeId.includes(item.id) }">
            {{ item.title }}
          </v-list-item-title>
          <template v-slot:append>
            <v-menu location="end" :close-on-content-click="true">
              <template v-slot:activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon="mdi-dots-vertical"
                  size="x-small"
                  variant="text"
                  density="compact"
                  class="tree-action-btn"
                />
              </template>
              <v-list density="compact" min-width="140">
                <v-list-item prepend-icon="mdi-plus" title="Add subpage" @click="$emit('create-subpage', item.id)" />
                <v-list-item prepend-icon="mdi-pencil" title="Rename" @click="$emit('rename', item.id)" />
                <v-divider />
                <v-list-item prepend-icon="mdi-delete" title="Delete" class="text-error" @click="$emit('delete', item.id)" />
              </v-list>
            </v-menu>
          </template>
        </v-list-item>
      </v-list>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  query: { type: String, default: '' },
  activeId: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:query', 'select', 'create', 'create-subpage', 'rename', 'delete'])

const containerRef = ref(null)
const localQuery = computed({
  get: () => props.query,
  set: (v) => emit('update:query', v),
})

watch(() => props.items, () => {
  // scroll reset handled by parent via container ref
}, { flush: 'post' })

defineExpose({ containerRef })
</script>

<style scoped>
.sidebar-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.tree-container {
  flex: 1;
  overflow-y: auto;
  display: block;
}
.tech-doc-list {
  padding-top: 0 !important;
  flex: 0 0 auto !important;
  align-self: flex-start !important;
  width: 100%;
}
.tech-doc-list-item {
  min-height: 32px;
}
.tree-action-btn {
  opacity: 0;
  transition: opacity 0.15s;
}
:deep(.v-treeview-node__root:hover) .tree-action-btn {
  opacity: 1;
}
</style>
