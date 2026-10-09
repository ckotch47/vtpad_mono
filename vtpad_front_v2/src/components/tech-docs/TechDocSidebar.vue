<template>
  <v-card flat class="sidebar-card">
    <v-toolbar density="compact" color="surface">
      <v-icon class="ml-2">mdi-book-open-variant</v-icon>
      <v-toolbar-title class="text-subtitle-2">Pages</v-toolbar-title>
      <v-spacer />
      <v-btn v-if="canEdit && errorStatus !== 403" icon="mdi-plus" size="small" variant="text" aria-label="Create page" title="Create page" @click="$emit('create')" />
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
    <v-card-text ref="containerRef" class="pa-0 tree-container" :aria-busy="loading">
      <list-loading-skeleton
        v-if="initialLoading"
        variant="tree"
        :rows="6"
        label="documentation pages"
      />
      <v-progress-linear v-if="loading && hasLoaded" indeterminate color="primary" height="2" aria-hidden="true" />
      <v-alert v-if="error" type="error" variant="tonal" density="compact" class="ma-2" role="alert">
        {{ errorStatus === 403 ? 'You do not have permission to view documentation pages.' : items.length ? 'Pages could not be refreshed. The previous tree is still shown.' : 'Documentation pages could not be loaded.' }}
        <v-btn v-if="errorStatus !== 403" size="small" variant="text" @click="$emit('retry')">Retry</v-btn>
      </v-alert>
      <v-list v-if="!initialLoading" density="compact" class="tech-doc-list">
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
            <v-menu v-if="canEdit" location="end" :close-on-content-click="true">
              <template v-slot:activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon="mdi-dots-vertical"
                  size="x-small"
                  variant="text"
                  density="compact"
                  class="tree-action-btn"
                  :aria-label="`More actions for ${item.title}`"
                  :title="`More actions for ${item.title}`"
                />
              </template>
              <v-list density="compact" min-width="140">
                <v-list-item v-if="canEdit" prepend-icon="mdi-plus" title="Add subpage" @click="$emit('create-subpage', item.id)" />
                <v-list-item v-if="canEdit" prepend-icon="mdi-pencil" title="Rename" @click="$emit('rename', item.id)" />
                <v-divider />
                <v-list-item v-if="canEdit" prepend-icon="mdi-delete" title="Delete" class="text-error" @click="$emit('delete', item.id)" />
              </v-list>
            </v-menu>
          </template>
        </v-list-item>
      </v-list>
      <contextual-empty-state
        v-if="!initialLoading && !error && !items.length"
        class="ma-2"
        :icon="localQuery ? 'mdi-filter-off-outline' : 'mdi-book-open-page-variant-outline'"
        :title="localQuery ? 'No matching pages' : 'No documentation pages yet'"
        :text="localQuery ? 'Clear the search to see all pages.' : canEdit ? 'Create a documentation page to get started.' : 'You have read-only access to Tech Docs in this space.'"
        :action-label="localQuery ? 'Clear search' : ''"
        @action="localQuery = ''"
      />
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import ListLoadingSkeleton from '@/components/common/ListLoadingSkeleton.vue'

const props = defineProps({
  canEdit: { type: Boolean, default: false },
  items: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  error: { type: Boolean, default: false },
  errorStatus: { type: Number, default: 0 },
  query: { type: String, default: '' },
  activeId: { type: Array, default: () => [] },
})

const hasLoaded = ref(false)
const initialLoading = computed(() => props.loading && !hasLoaded.value)

watch(() => props.loading, (isLoading) => {
  if (!isLoading) hasLoaded.value = true
})

const emit = defineEmits(['update:query', 'select', 'create', 'create-subpage', 'rename', 'delete', 'retry'])

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
.tech-doc-list-item:hover .tree-action-btn,
.tech-doc-list-item:focus-within .tree-action-btn,
.tree-action-btn:focus-visible {
  opacity: 1;
}
.tree-action-btn:focus-visible {
  outline: 2px solid rgb(var(--v-theme-primary));
  outline-offset: 2px;
}
</style>
