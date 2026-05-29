<route lang="json">
{
  "meta": {
    "layout": "spaces",
    "tabValue": "tech-docs"
  }
}
</route>

<template>
  <v-container class="mx-auto custom-container max-width-1500 tech-doc-page">
    <page-header-component title="Tech Docs" />
    <v-row no-gutters class="fill-height tech-doc-layout">
      <!-- Sidebar -->
      <v-col cols="12" md="3" class="sidebar-col">
        <tech-doc-sidebar
          ref="sidebarRef"
          v-model:query="treeQuery"
          :items="flatFilteredPages"
          :loading="treeLoading"
          :active-id="activeId"
          @select="onTreeSelect"
          @create="openCreate"
          @create-subpage="openCreateSubpage"
          @rename="renameDoc"
          @delete="deleteDocById"
        />
      </v-col>

      <!-- Content -->
      <v-col cols="12" md="9" class="content-col">
        <tech-doc-content
          :doc="selectedDoc"
          :editing="editing"
          :is-creating="isCreating"
          :save-loading="saveLoading"
          :form="editForm"
          :doc-types="docTypes"
          :flat-pages="flatPages"
          :path="selectedPath"
          :type-color="typeColor"
          @create="openCreate"
          @edit="startEdit"
          @create-subpage="openCreateSubpage"
          @delete="deleteDoc"
          @cancel="cancelEdit"
          @save="save"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useTechDocs } from '@/composables/useTechDocs'
import TechDocSidebar from '@/components/tech-docs/TechDocSidebar.vue'
import TechDocContent from '@/components/tech-docs/TechDocContent.vue'

const sidebarRef = ref(null)

const techDocs = useTechDocs()
const {
  treeLoading,
  treeQuery,
  flatFilteredPages,
  flatPages,
  selectedDoc,
  activeId,
  editing,
  isCreating,
  saveLoading,
  editForm,
  docTypes,
  selectedPath,
  onTreeSelect,
  startEdit,
  openCreate,
  openCreateSubpage,
  renameDoc,
  deleteDocById,
  cancelEdit,
  save,
  deleteDoc,
  typeColor,
  treeContainerRef,
} = techDocs

watch(() => sidebarRef.value?.containerRef, (el) => {
  if (el) treeContainerRef.value = el
})
</script>

<style scoped>
.tech-doc-page {
  padding-top: 0;
}
.tech-doc-layout {
  min-height: calc(100vh - 170px);
}
.sidebar-col {
  border-right: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  max-width: 300px;
}
.content-col {
  height: 100%;
  overflow: hidden;
}
</style>
