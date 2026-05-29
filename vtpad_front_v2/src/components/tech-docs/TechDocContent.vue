<template>
  <!-- Empty state -->
  <v-card v-if="!doc && !editing" flat class="fill-height d-flex align-center justify-center">
    <v-card-text class="text-center">
      <v-icon size="80" color="grey-lighten-2">mdi-book-open-variant</v-icon>
      <div class="text-h5 text-grey mt-4">Tech Documentation</div>
      <div class="text-body-1 text-grey mt-2">Select a page or create one</div>
      <v-btn color="primary" class="mt-6" prepend-icon="mdi-plus" @click="$emit('create')">
        Create first page
      </v-btn>
    </v-card-text>
  </v-card>

  <!-- View mode -->
  <v-card v-else-if="doc && !editing" flat class="content-card">
    <v-toolbar density="comfortable" color="surface">
      <div class="ml-2">
        <v-breadcrumbs v-if="path.length" :items="path" density="compact" class="pa-0" />
        <div class="text-h6">{{ doc.title }}</div>
        <div v-if="doc.version" class="text-caption text-grey">v{{ doc.version }}</div>
      </div>
      <v-spacer />
      <v-chip size="small" :color="typeColor(doc.doc_type)" class="mr-2">{{ doc.doc_type }}</v-chip>
      <v-btn icon="mdi-pencil" size="small" variant="text" @click="$emit('edit')" />
      <v-btn icon="mdi-plus" size="small" variant="text" @click="$emit('create-subpage')" />
      <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="$emit('delete')" />
    </v-toolbar>
    <v-divider />
    <v-card-text v-if="doc.source_url" class="pb-0">
      <v-alert type="info" variant="tonal" density="compact" class="mb-2">
        <a :href="doc.source_url" target="_blank" class="text-decoration-none">{{ doc.source_url }}</a>
      </v-alert>
    </v-card-text>
    <v-card-text class="content-body">
      <editor-component
        v-if="doc.content"
        :key="`readonly-${doc.id}`"
        :text="doc.content"
        :edit="false"
        :show-menu-fixed="false"
        :show-menu-bubble="false"
        :show-menu-floating="false"
        max-height="none"
        min-height="auto"
      />
      <div v-else class="text-grey text-center py-10">
        <v-icon size="48">mdi-text-box-outline</v-icon>
        <div class="mt-2">No content yet</div>
        <v-btn variant="text" color="primary" @click="$emit('edit')">Add content</v-btn>
      </div>
    </v-card-text>
  </v-card>

  <!-- Edit mode -->
  <v-card v-else-if="editing" flat class="content-card">
    <v-toolbar density="comfortable" color="surface">
      <v-btn icon="mdi-close" size="small" variant="text" @click="$emit('cancel')" />
      <v-toolbar-title class="text-subtitle-1">{{ isCreating ? 'New Page' : 'Edit Page' }}</v-toolbar-title>
      <v-spacer />
      <v-btn color="primary" size="small" :loading="saveLoading" @click="$emit('save')">Save</v-btn>
    </v-toolbar>
    <v-divider />
    <v-card-text class="content-body">
      <v-row dense>
        <v-col cols="12" md="6">
          <v-text-field v-model="form.title" label="Title *" density="compact" hide-details class="mb-3" />
        </v-col>
        <v-col cols="12" md="3">
          <v-select
            v-model="form.doc_type"
            :items="docTypes"
            item-title="title"
            item-value="value"
            label="Type"
            density="compact"
            hide-details
            class="mb-3"
          />
        </v-col>
        <v-col cols="12" md="3">
          <v-text-field v-model="form.version" label="Version" density="compact" hide-details class="mb-3" />
        </v-col>
      </v-row>
      <v-row dense>
        <v-col cols="12" md="6">
          <v-text-field v-model="form.source_url" label="Source URL" density="compact" hide-details class="mb-3" />
        </v-col>
        <v-col cols="12" md="6" v-if="isCreating">
          <v-select
            v-model="form.parent_id"
            :items="flatPages"
            item-title="title"
            item-value="id"
            label="Parent page"
            density="compact"
            hide-details
            clearable
            class="mb-3"
          />
        </v-col>
      </v-row>
      <div class="text-subtitle-2 mb-2">Content</div>
      <editor-component
        :key="isCreating ? 'create' : (doc?.id || 'edit')"
        :text="form.content || ''"
        :edit="true"
        :show-menu-fixed="true"
        max-height="calc(100vh - 360px)"
        min-height="420px"
        place-holder-editor="Enter documentation content..."
        @editor-update="form.content = $event"
      />
    </v-card-text>
  </v-card>
</template>

<script setup>
import EditorComponent from '@/components/common/editor/editorComponent.vue'

defineProps({
  doc: { type: Object, default: null },
  editing: { type: Boolean, default: false },
  isCreating: { type: Boolean, default: false },
  saveLoading: { type: Boolean, default: false },
  form: { type: Object, required: true },
  docTypes: { type: Array, default: () => [] },
  flatPages: { type: Array, default: () => [] },
  path: { type: Array, default: () => [] },
  typeColor: { type: Function, default: () => 'grey' },
})

defineEmits(['create', 'edit', 'create-subpage', 'delete', 'cancel', 'save'])
</script>

<style scoped>
.content-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.content-body {
  flex: 1;
  overflow: hidden;
  padding: 20px 24px 28px;
}
</style>
