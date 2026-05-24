<route>
{
  meta: {
    layout: "spaces",
    tabValue: "tech-docs"
  }
}
</route>

<template>
  <v-container fluid class="pa-0 fill-height">
    <v-row no-gutters class="fill-height">
      <!-- Sidebar -->
      <v-col cols="12" md="3" class="sidebar-col">
        <v-card flat class="sidebar-card">
          <v-toolbar density="compact" color="surface">
            <v-icon class="ml-2">mdi-book-open-variant</v-icon>
            <v-toolbar-title class="text-subtitle-2">Pages</v-toolbar-title>
            <v-spacer />
            <v-btn icon="mdi-plus" size="small" variant="text" @click="openCreate" />
          </v-toolbar>
          <v-divider />
          <v-card-text class="pa-0 tree-container">
            <v-skeleton-loader v-if="treeLoading" type="list-item@5" />
            <v-treeview
              v-else
              :items="tree"
              item-title="title"
              item-value="id"
              item-children="children"
              activatable
              :activated="activeId"
              @update:activated="onTreeSelect"
              density="compact"
              class="tech-doc-tree"
            >
              <template v-slot:prepend="{ item }">
                <v-icon size="small" :color="item.children?.length ? 'primary' : 'grey'">
                  {{ item.children?.length ? 'mdi-folder-outline' : 'mdi-file-document-outline' }}
                </v-icon>
              </template>
              <template v-slot:title="{ item }">
                <span class="text-body-2" :class="{ 'font-weight-medium': activeId.includes(item.id) }">
                  {{ item.title }}
                </span>
              </template>
              <template v-slot:append="{ item }">
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
                    <v-list-item prepend-icon="mdi-plus" title="Add subpage" @click="openCreateSubpage(item.id)" />
                    <v-list-item prepend-icon="mdi-pencil" title="Rename" @click="renameDoc(item.id)" />
                    <v-divider />
                    <v-list-item prepend-icon="mdi-delete" title="Delete" class="text-error" @click="deleteDocById(item.id)" />
                  </v-list>
                </v-menu>
              </template>
            </v-treeview>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Content -->
      <v-col cols="12" md="9" class="content-col">
        <!-- Empty state -->
        <v-card v-if="!selectedDoc && !editing" flat class="fill-height d-flex align-center justify-center">
          <v-card-text class="text-center">
            <v-icon size="80" color="grey-lighten-2">mdi-book-open-variant</v-icon>
            <div class="text-h5 text-grey mt-4">Tech Documentation</div>
            <div class="text-body-1 text-grey mt-2">Select a page or create one</div>
            <v-btn color="primary" class="mt-6" prepend-icon="mdi-plus" @click="openCreate">
              Create first page
            </v-btn>
          </v-card-text>
        </v-card>

        <!-- View mode -->
        <v-card v-else-if="selectedDoc && !editing" flat class="content-card">
          <v-toolbar density="comfortable" color="surface">
            <div class="ml-2">
              <div class="text-h6">{{ selectedDoc.title }}</div>
              <div v-if="selectedDoc.version" class="text-caption text-grey">
                v{{ selectedDoc.version }}
              </div>
            </div>
            <v-spacer />
            <v-chip size="small" :color="typeColor(selectedDoc.doc_type)" class="mr-2">
              {{ selectedDoc.doc_type }}
            </v-chip>
            <v-btn icon="mdi-pencil" size="small" variant="text" @click="startEdit" />
            <v-btn icon="mdi-plus" size="small" variant="text" @click="openCreateSubpage" />
            <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteDoc" />
          </v-toolbar>
          <v-divider />
          <v-card-text v-if="selectedDoc.source_url" class="pb-0">
            <v-alert type="info" variant="tonal" density="compact" class="mb-2">
              <a :href="selectedDoc.source_url" target="_blank" class="text-decoration-none">{{ selectedDoc.source_url }}</a>
            </v-alert>
          </v-card-text>
          <v-card-text class="content-body">
            <div v-if="selectedDoc.content" v-html="selectedDoc.content" class="tech-doc-content" />
            <div v-else class="text-grey text-center py-10">
              <v-icon size="48">mdi-text-box-outline</v-icon>
              <div class="mt-2">No content yet</div>
              <v-btn variant="text" color="primary" @click="startEdit">Add content</v-btn>
            </div>
          </v-card-text>
        </v-card>

        <!-- Edit mode -->
        <v-card v-else-if="editing" flat class="content-card">
          <v-toolbar density="comfortable" color="surface">
            <v-btn icon="mdi-close" size="small" variant="text" @click="cancelEdit" />
            <v-toolbar-title class="text-subtitle-1">{{ isCreating ? 'New Page' : 'Edit Page' }}</v-toolbar-title>
            <v-spacer />
            <v-btn color="primary" size="small" @click="save">Save</v-btn>
          </v-toolbar>
          <v-divider />
          <v-card-text class="content-body">
            <v-row dense>
              <v-col cols="12" md="6">
                <v-text-field v-model="editForm.title" label="Title *" density="compact" hide-details class="mb-3" />
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="editForm.doc_type"
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
                <v-text-field v-model="editForm.version" label="Version" density="compact" hide-details class="mb-3" />
              </v-col>
            </v-row>
            <v-row dense>
              <v-col cols="12" md="6">
                <v-text-field v-model="editForm.source_url" label="Source URL" density="compact" hide-details class="mb-3" />
              </v-col>
              <v-col cols="12" md="6" v-if="isCreating">
                <v-select
                  v-model="editForm.parent_id"
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
              :key="isCreating ? 'create' : (selectedDoc?.id || 'edit')"
              :text="editForm.content || ''"
              :edit="true"
              :show-menu-fixed="true"
              place-holder-editor="Enter documentation content..."
              @editor-update="editForm.content = $event"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { techDocService } from '@/services'
import EditorComponent from "@/components/common/editor/editorComponent.vue";

export default {
  name: 'TechDocsWikiPage',
  components: { EditorComponent },
  data: () => ({
    treeLoading: true,
    tree: [],
    selectedDoc: null,
    activeId: [],
    editing: false,
    isCreating: false,
    editForm: {
      title: '',
      content: '',
      doc_type: 'other',
      source_url: '',
      version: '',
      parent_id: null,
    },
    docTypes: [
      { title: 'API Doc', value: 'api_doc' },
      { title: 'PRD', value: 'prd' },
      { title: 'Manual', value: 'manual' },
      { title: 'Wiki', value: 'wiki' },
      { title: 'Migration', value: 'migration' },
      { title: 'Other', value: 'other' },
    ],
  }),
  computed: {
    spaceId() {
      return this.$route.params.spaceId
    },
    flatPages() {
      return this.flattenTree(this.tree)
    },
  },
  watch: {
    '$route.query.doc': {
      handler(val) {
        if (val) {
          this.activeId = [val]
          this.loadDoc(val)
        } else {
          this.selectedDoc = null
          this.activeId = []
        }
      },
      immediate: true,
    },
  },
  async mounted() {
    await this.loadTree()
    if (this.$route.query.doc) {
      this.activeId = [this.$route.query.doc]
      await this.loadDoc(this.$route.query.doc)
    }
  },
  methods: {
    async loadTree() {
      this.treeLoading = true
      try {
        const res = await techDocService.getTree(this.spaceId)
        this.tree = res.data || []
      } catch (e) {
        console.error(e)
      } finally {
        this.treeLoading = false
      }
    },
    async loadDoc(docId) {
      try {
        const res = await techDocService.getById(docId)
        this.selectedDoc = res.data
      } catch (e) {
        console.error(e)
        this.selectedDoc = null
      }
    },
    onTreeSelect(ids) {
      const id = ids[0]
      if (id) {
        this.editing = false
        this.activeId = [id]
        this.loadDoc(id)
        this.$router.replace({ query: { doc: id } })
      }
    },
    startEdit() {
      if (!this.selectedDoc) return
      this.isCreating = false
      this.editForm = {
        title: this.selectedDoc.title || '',
        content: this.selectedDoc.content || '',
        doc_type: this.selectedDoc.doc_type || 'other',
        source_url: this.selectedDoc.source_url || '',
        version: this.selectedDoc.version || '',
        parent_id: this.selectedDoc.parent_id || null,
      }
      this.editing = true
    },
    openCreate() {
      this.isCreating = true
      this.editForm = {
        title: '',
        content: '',
        doc_type: 'other',
        source_url: '',
        version: '',
        parent_id: null,
      }
      this.selectedDoc = null
      this.activeId = []
      this.editing = true
    },
    openCreateSubpage(parentId = null) {
      this.isCreating = true
      this.editForm = {
        title: '',
        content: '',
        doc_type: 'other',
        source_url: '',
        version: '',
        parent_id: parentId || this.selectedDoc?.id || null,
      }
      this.editing = true
    },
    async renameDoc(docId) {
      await this.loadDoc(docId)
      this.startEdit()
    },
    async deleteDocById(docId) {
      const doc = this.findDocInTree(this.tree, docId)
      const title = doc?.title || 'this page'
      if (!confirm(`Delete "${title}"?\n\nSubpages will become root-level pages.`)) return
      try {
        await techDocService.delete(docId)
        if (this.selectedDoc?.id === docId) {
          this.selectedDoc = null
          this.activeId = []
          this.$router.replace({ query: {} })
        }
        await this.loadTree()
      } catch (e) {
        console.error(e)
        alert(e.response?.data?.detail || 'Failed to delete')
      }
    },
    findDocInTree(nodes, id) {
      for (const node of nodes) {
        if (node.id === id) return node
        if (node.children) {
          const found = this.findDocInTree(node.children, id)
          if (found) return found
        }
      }
      return null
    },
    cancelEdit() {
      this.editing = false
      if (this.$route.query.doc) {
        this.loadDoc(this.$route.query.doc)
      }
    },
    async save() {
      if (!this.editForm.title) {
        alert('Title is required')
        return
      }
      try {
        if (this.isCreating) {
          const res = await techDocService.create({
            ...this.editForm,
            space_id: this.spaceId,
          })
          this.editing = false
          await this.loadTree()
          this.$router.replace({ query: { doc: res.data.id } })
        } else {
          await techDocService.update(this.selectedDoc.id, this.editForm)
          this.editing = false
          await this.loadDoc(this.selectedDoc.id)
          await this.loadTree()
        }
      } catch (e) {
        console.error(e)
        alert('Failed to save: ' + (e.response?.data?.detail || e.message))
      }
    },
    async deleteDoc() {
      if (!this.selectedDoc) return
      if (!confirm(`Delete "${this.selectedDoc.title}"?`)) return
      try {
        await techDocService.delete(this.selectedDoc.id)
        this.selectedDoc = null
        this.activeId = []
        this.$router.replace({ query: {} })
        await this.loadTree()
      } catch (e) {
        console.error(e)
        alert(e.response?.data?.detail || 'Failed to delete')
      }
    },
    typeColor(type) {
      const map = { api_doc: 'blue', prd: 'purple', manual: 'green', wiki: 'orange', migration: 'red', other: 'grey' }
      return map[type] || 'grey'
    },
    flattenTree(nodes, level = 0) {
      let result = []
      for (const node of nodes) {
        result.push({ id: node.id, title: '\u00A0\u00A0'.repeat(level) + node.title })
        if (node.children) {
          result = result.concat(this.flattenTree(node.children, level + 1))
        }
      }
      return result
    },
  },
}
</script>

<style scoped>
.sidebar-col {
  border-right: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  max-width: 300px;
}
.sidebar-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.tree-container {
  flex: 1;
  overflow-y: auto;
}
.content-col {
  height: 100%;
  overflow: hidden;
}
.content-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.content-body {
  flex: 1;
  overflow-y: auto;
}
.tech-doc-content {
  font-size: 1rem;
  line-height: 1.6;
}
.tech-doc-content h1, .tech-doc-content h2, .tech-doc-content h3 {
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}
.tech-doc-content p {
  margin-bottom: 0.75rem;
}
.tech-doc-content ul, .tech-doc-content ol {
  margin-left: 1.5rem;
  margin-bottom: 0.75rem;
}
.tech-doc-tree :deep(.v-treeview-node__root) {
  min-height: 32px;
}
.tech-action-btn {
  opacity: 0;
  transition: opacity 0.15s;
}
:deep(.v-treeview-node__root:hover) .tree-action-btn {
  opacity: 1;
}
</style>
