<template>
  <!-- Empty state -->
  <v-card v-if="!doc && !editing" flat class="fill-height d-flex align-center justify-center">
    <v-card-text class="text-center">
      <v-icon size="80" color="grey-lighten-2">mdi-book-open-variant</v-icon>
      <div class="text-h5 text-grey mt-4">Tech Documentation</div>
      <v-progress-circular v-if="pagesLoading" indeterminate color="primary" class="mt-4" aria-label="Loading documentation pages" />
      <v-alert v-else-if="pagesError" type="error" variant="tonal" density="compact" class="mt-4" role="alert">
        Documentation pages could not be loaded.
      </v-alert>
      <div v-else class="text-body-1 text-grey mt-2">
        {{ hasPages ? 'Select a page from the list or create a page' : 'No documentation pages yet' }}
      </div>
      <div v-if="pagesError" class="mt-4">
        <v-btn color="primary" variant="tonal" @click="$emit('retry-load')">Retry</v-btn>
      </div>
      <v-btn v-else-if="!pagesLoading" color="primary" class="mt-6" prepend-icon="mdi-plus" @click="$emit('create')">
        {{ hasPages ? 'Create page' : 'Create first page' }}
      </v-btn>
    </v-card-text>
  </v-card>

  <!-- View mode -->
  <v-card v-else-if="doc && !editing" flat class="content-card">
    <v-toolbar density="comfortable" color="surface">
      <div class="ml-2">
        <v-breadcrumbs v-if="path.length" :items="path" density="compact" class="pa-0" />
        <div v-if="!path.length" class="text-h6">{{ doc.title }}</div>
        <div v-if="doc.version" class="text-caption text-grey">v{{ doc.version }}</div>
      </div>
      <v-spacer />
      <v-chip size="small" :color="typeColor(doc.doc_type)" class="mr-2">{{ doc.doc_type }}</v-chip>
      <v-btn icon="mdi-pencil" size="small" variant="text" aria-label="Edit page" title="Edit page" @click="$emit('edit')" />
      <v-btn icon="mdi-plus" size="small" variant="text" aria-label="Create subpage" title="Create subpage" @click="$emit('create-subpage')" />
      <v-btn icon="mdi-delete" size="small" variant="text" color="error" aria-label="Delete page" title="Delete page" @click="$emit('delete')" />
    </v-toolbar>
    <v-divider />
    <v-card-text v-if="doc.source_url" class="pb-0 source-url-section">
      <v-alert type="info" variant="tonal" density="compact" class="mb-2 source-url-alert">
        <v-tooltip :text="doc.source_url" location="top">
          <template #activator="{ props }">
            <a
              v-if="safeSourceUrl"
              v-bind="props"
              :href="safeSourceUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="source-url text-decoration-none"
            >
              {{ doc.source_url }}
            </a>
            <span v-else v-bind="props" class="source-url text-medium-emphasis">{{ doc.source_url }}</span>
          </template>
        </v-tooltip>
      </v-alert>
    </v-card-text>
    <v-card-text class="content-body">
      <div ref="readonlyContentRef">
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
      </div>
      <div v-if="!doc.content" class="text-grey text-center py-10">
        <v-icon size="48">mdi-text-box-outline</v-icon>
        <div class="mt-2">No content yet</div>
        <v-btn variant="text" color="primary" @click="$emit('edit')">Add content</v-btn>
      </div>
      <v-card variant="tonal" class="mt-5">
        <v-card-title class="text-subtitle-1 d-flex align-center">
          Linked test cases
          <v-spacer />
          <v-btn v-if="!editingLinks" size="small" variant="text" @click="editingLinks = true">Edit links</v-btn>
        </v-card-title>
        <v-card-text>
          <template v-if="editingLinks">
            <v-autocomplete
              v-model="linkedCaseIds"
              :items="availableCases"
              item-title="title"
              item-value="id"
              label="Test cases"
              multiple
              chips
              closable-chips
              :loading="linksLoading"
            />
            <div class="d-flex justify-end ga-2"><v-btn size="small" variant="text" @click="cancelLinks">Cancel</v-btn><v-btn size="small" color="primary" :loading="linksSaving" @click="saveLinks">Save links</v-btn></div>
          </template>
          <template v-else>
            <v-chip v-for="testcase in linkedCases" :key="testcase.id" class="mr-1 mb-1" :to="`/space/${spaceId}/test-cases/${testcase.id}`">{{ testcase.title }}</v-chip>
            <span v-if="!linkedCases.length" class="text-medium-emphasis">No test cases linked</span>
          </template>
        </v-card-text>
      </v-card>
    </v-card-text>
  </v-card>

  <!-- Edit mode -->
  <v-card v-else-if="editing" flat class="content-card">
    <v-toolbar density="comfortable" color="surface">
      <v-btn icon="mdi-close" size="small" variant="text" aria-label="Cancel page editing" title="Cancel page editing" @click="$emit('cancel')" />
      <v-toolbar-title class="text-subtitle-1">{{ isCreating ? 'New Page' : 'Edit Page' }}</v-toolbar-title>
      <v-spacer />
      <v-btn color="primary" size="small" :loading="saveLoading" @click="$emit('save')">Save</v-btn>
    </v-toolbar>
    <v-divider />
    <v-card-text class="content-body">
      <v-row dense>
        <v-col cols="12" md="6">
          <v-text-field v-model="localForm.title" label="Title *" density="compact" hide-details class="mb-3" />
        </v-col>
        <v-col cols="12" md="3">
          <v-select
            v-model="localForm.doc_type"
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
          <v-text-field v-model="localForm.version" label="Version" density="compact" hide-details class="mb-3" />
        </v-col>
      </v-row>
      <v-row dense>
        <v-col cols="12" md="6">
          <v-text-field v-model="localForm.source_url" label="Source URL" density="compact" hide-details class="mb-3" />
        </v-col>
        <v-col cols="12" md="6" v-if="isCreating">
          <v-select
            v-model="localForm.parent_id"
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
        :text="localForm.content || ''"
        :edit="true"
        :show-menu-fixed="true"
        max-height="calc(100vh - 360px)"
        min-height="420px"
        place-holder-editor="Enter documentation content..."
        @editor-update="localForm.content = $event"
      />
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import EditorComponent from '@/components/common/editor/editorComponent.vue'
import { techDocService, testCaseService } from '@/services'

const route = useRoute()
const spaceId = computed(() => route.params.spaceId)

const props = defineProps({
  doc: { type: Object, default: null },
  editing: { type: Boolean, default: false },
  isCreating: { type: Boolean, default: false },
  saveLoading: { type: Boolean, default: false },
  form: { type: Object, required: true },
  docTypes: { type: Array, default: () => [] },
  flatPages: { type: Array, default: () => [] },
  pagesLoading: { type: Boolean, default: false },
  pagesError: { type: Boolean, default: false },
  path: { type: Array, default: () => [] },
  typeColor: { type: Function, default: () => 'grey' },
})

const hasPages = computed(() => props.flatPages.length > 0)

const linkedCases = ref([])
const availableCases = ref([])
const linkedCaseIds = ref([])
const linksLoading = ref(false)
const linksSaving = ref(false)
const editingLinks = ref(false)

async function loadLinks() {
  if (!props.doc?.id) return
  linksLoading.value = true
  try {
    const [linked, all] = await Promise.all([
      techDocService.getTestCases(props.doc.id),
      testCaseService.listBySpace(spaceId.value, { page: 1, page_size: 500, status: 'active' }),
    ])
    linkedCases.value = linked.data.items || linked.data || []
    linkedCaseIds.value = linkedCases.value.map((testcase) => testcase.id)
    availableCases.value = all.data.items || all.data || []
  } catch (_) { linkedCases.value = []; availableCases.value = [] } finally { linksLoading.value = false }
}

function cancelLinks() { linkedCaseIds.value = linkedCases.value.map((testcase) => testcase.id); editingLinks.value = false }

async function saveLinks() {
  linksSaving.value = true
  try { await techDocService.updateTestCases(props.doc.id, linkedCaseIds.value); await loadLinks(); editingLinks.value = false } finally { linksSaving.value = false }
}

const emit = defineEmits(['create', 'edit', 'create-subpage', 'delete', 'cancel', 'save', 'retry-load', 'update:form'])

const localForm = reactive({ ...props.form })

watch(() => props.form, (form) => {
  Object.assign(localForm, form)
}, { deep: true })

watch(localForm, (form) => {
  emit('update:form', { ...form })
}, { deep: true })

const readonlyContentRef = ref(null)
let renderSeq = 0
let mermaidPromise = null

const safeSourceUrl = computed(() => {
  const value = props.doc?.source_url?.trim()
  if (!value) return null

  try {
    const url = new URL(value)
    return ['http:', 'https:'].includes(url.protocol) ? url.href : null
  } catch {
    return null
  }
})

async function getMermaid() {
  if (!mermaidPromise) {
    mermaidPromise = import('mermaid').then((mod) => {
      const api = mod.default
      api.initialize({
        startOnLoad: false,
        securityLevel: 'strict',
        theme: 'default',
      })
      return api
    })
  }
  return mermaidPromise
}

async function renderMermaidInReadonly() {
  if (!props.doc?.content || props.editing) return
  const root = readonlyContentRef.value
  if (!root) return

  const mySeq = ++renderSeq
  await nextTick()
  await new Promise(resolve => requestAnimationFrame(resolve))
  if (mySeq !== renderSeq) return

  const codeNodes = root.querySelectorAll('pre code.language-mermaid')
  if (!codeNodes.length) return

  const mermaid = await getMermaid()

  codeNodes.forEach((codeNode) => {
    const preNode = codeNode.closest('pre')
    if (!preNode) return
    const mermaidNode = document.createElement('pre')
    mermaidNode.className = 'mermaid'
    mermaidNode.textContent = codeNode.textContent || ''
    preNode.replaceWith(mermaidNode)
  })

  try {
    await mermaid.run({ nodes: root.querySelectorAll('pre.mermaid') })
  } catch (error) {
    console.error('Mermaid render failed', error)
  }
}

watch(
  () => [props.doc?.id, props.doc?.content, props.editing],
  () => {
    renderMermaidInReadonly()
  },
  { immediate: true }
)

watch(() => props.doc?.id, () => { editingLinks.value = false; loadLinks() }, { immediate: true })

onBeforeUnmount(() => {
  renderSeq += 1
})
</script>

<style scoped>
.content-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.source-url-section {
  flex: 0 0 auto;
}

.content-body {
  flex: 1 1 auto;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
  padding: 20px 24px 28px;
}

:deep(pre.mermaid) {
  background: transparent;
  border: 0;
  padding: 0;
  margin: 16px 0;
}

:deep(pre.mermaid svg) {
  max-width: 100%;
  height: auto;
}

.source-url-alert :deep(.v-alert__content) {
  min-width: 0;
}

.source-url {
  display: block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
