import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useLogger } from '@/composables/useLogger'
import { useRoute, useRouter } from 'vue-router'
import { techDocService } from '@/services'

export function useTechDocs() {
  const log = useLogger('tech-docs')
  const route = useRoute()
  const router = useRouter()

  const spaceId = computed(() => route.params.spaceId)

  const treeLoading = ref(true)
  const tree = ref([])
  const treeQuery = ref('')
  const treeContainerRef = ref(null)
  const selectedDoc = ref(null)
  const activeId = ref([])
  const editing = ref(false)
  const isCreating = ref(false)
  const saveLoading = ref(false)
  const editForm = ref({
    title: '',
    content: '',
    doc_type: 'other',
    source_url: '',
    version: '',
    parent_id: null,
  })
  const docTypes = [
    { title: 'API Doc', value: 'api_doc' },
    { title: 'PRD', value: 'prd' },
    { title: 'Manual', value: 'manual' },
    { title: 'Wiki', value: 'wiki' },
    { title: 'Migration', value: 'migration' },
    { title: 'Other', value: 'other' },
  ]

  const flatPages = computed(() => flattenTree(tree.value))
  const filteredTree = computed(() => {
    const query = treeQuery.value?.trim().toLowerCase()
    if (!query) return tree.value
    return filterTree(tree.value, query)
  })
  const flatFilteredPages = computed(() => flattenTreeForList(filteredTree.value))
  const selectedPath = computed(() => {
    if (!selectedDoc.value?.id) return []
    const path = getNodePath(tree.value, selectedDoc.value.id)
    return path.map(title => ({ title }))
  })

  watch(() => route.query.doc, (val) => {
    if (val) {
      activeId.value = [val]
      loadDoc(val)
    } else {
      selectedDoc.value = null
      activeId.value = []
    }
  }, { immediate: true })

  onMounted(async () => {
    await loadTree()
    if (route.query.doc) {
      activeId.value = [route.query.doc]
      await loadDoc(route.query.doc)
    }
    scheduleTreeScrollReset()
  })

  async function loadTree() {
    treeLoading.value = true
    try {
      const res = await techDocService.getTree(spaceId.value)
      tree.value = res.data || []
    } catch (e) {
      log.error('request failed', e)
    } finally {
      treeLoading.value = false
      await nextTick()
      scheduleTreeScrollReset()
    }
  }

  async function loadDoc(docId) {
    try {
      const res = await techDocService.getById(docId)
      selectedDoc.value = res.data
    } catch (e) {
      log.error('request failed', e)
      selectedDoc.value = null
    }
  }

  function onTreeSelect(ids) {
    const id = ids[0]
    if (id) {
      if (editing.value && !confirm('Discard unsaved changes?')) return
      editing.value = false
      activeId.value = [id]
      loadDoc(id)
      router.replace({ query: { doc: id } })
    }
  }

  function startEdit() {
    if (!selectedDoc.value) return
    isCreating.value = false
    editForm.value = {
      title: selectedDoc.value.title || '',
      content: selectedDoc.value.content || '',
      doc_type: selectedDoc.value.doc_type || 'other',
      source_url: selectedDoc.value.source_url || '',
      version: selectedDoc.value.version || '',
      parent_id: selectedDoc.value.parent_id || null,
    }
    editing.value = true
  }

  function openCreate() {
    isCreating.value = true
    editForm.value = {
      title: '',
      content: '',
      doc_type: 'other',
      source_url: '',
      version: '',
      parent_id: null,
    }
    selectedDoc.value = null
    activeId.value = []
    editing.value = true
    resetTreeScroll()
  }

  function openCreateSubpage(parentId = null) {
    isCreating.value = true
    editForm.value = {
      title: '',
      content: '',
      doc_type: 'other',
      source_url: '',
      version: '',
      parent_id: parentId || selectedDoc.value?.id || null,
    }
    editing.value = true
  }

  async function renameDoc(docId) {
    await loadDoc(docId)
    startEdit()
  }

  async function deleteDocById(docId) {
    const doc = findDocInTree(tree.value, docId)
    const title = doc?.title || 'this page'
    if (!confirm(`Delete "${title}"?\n\nSubpages will become root-level pages.`)) return
    try {
      await techDocService.delete(docId)
      if (selectedDoc.value?.id === docId) {
        selectedDoc.value = null
        activeId.value = []
        router.replace({ query: {} })
      }
      await loadTree()
    } catch (e) {
      log.error('request failed', e)
      alert(e.response?.data?.detail || 'Failed to delete')
    }
  }

  function findDocInTree(nodes, id) {
    for (const node of nodes) {
      if (node.id === id) return node
      if (node.children) {
        const found = findDocInTree(node.children, id)
        if (found) return found
      }
    }
    return null
  }

  function cancelEdit() {
    if (!confirm('Discard unsaved changes?')) return
    editing.value = false
    if (route.query.doc) {
      loadDoc(route.query.doc)
    }
  }

  async function save() {
    if (!editForm.value.title) {
      alert('Title is required')
      return
    }
    saveLoading.value = true
    try {
      if (isCreating.value) {
        const res = await techDocService.create({
          ...editForm.value,
          space_id: spaceId.value,
        })
        editing.value = false
        await loadTree()
        router.replace({ query: { doc: res.data.id } })
      } else {
        await techDocService.update(selectedDoc.value.id, editForm.value)
        editing.value = false
        await loadDoc(selectedDoc.value.id)
        await loadTree()
      }
    } catch (e) {
      log.error('request failed', e)
      alert('Failed to save: ' + (e.response?.data?.detail || e.message))
    } finally {
      saveLoading.value = false
    }
  }

  async function deleteDoc() {
    if (!selectedDoc.value) return
    if (!confirm(`Delete "${selectedDoc.value.title}"?`)) return
    try {
      await techDocService.delete(selectedDoc.value.id)
      selectedDoc.value = null
      activeId.value = []
      router.replace({ query: {} })
      await loadTree()
    } catch (e) {
      log.error('request failed', e)
      alert(e.response?.data?.detail || 'Failed to delete')
    }
  }

  function typeColor(type) {
    const map = { api_doc: 'blue', prd: 'purple', manual: 'green', wiki: 'orange', migration: 'red', other: 'grey' }
    return map[type] || 'grey'
  }

  function flattenTree(nodes, level = 0) {
    let result = []
    for (const node of nodes) {
      result.push({ id: node.id, title: '\u00A0\u00A0'.repeat(level) + node.title })
      if (node.children) {
        result = result.concat(flattenTree(node.children, level + 1))
      }
    }
    return result
  }

  function flattenTreeForList(nodes, level = 0) {
    const result = []
    for (const node of nodes) {
      result.push({
        id: node.id,
        title: node.title,
        level,
        hasChildren: Boolean(node.children?.length),
      })
      if (node.children?.length) {
        result.push(...flattenTreeForList(node.children, level + 1))
      }
    }
    return result
  }

  function resetTreeScroll() {
    const el = treeContainerRef.value?.$el || treeContainerRef.value
    if (!el) return
    const candidates = [el, ...el.querySelectorAll('*')]
    for (const node of candidates) {
      if (!(node instanceof HTMLElement)) continue
      const style = window.getComputedStyle(node)
      const isScrollable = ['auto', 'scroll'].includes(style.overflowY) && node.scrollHeight > node.clientHeight
      if (isScrollable || node === el) {
        node.scrollTop = 0
      }
    }
  }

  function scheduleTreeScrollReset() {
    setTimeout(() => resetTreeScroll(), 0)
    setTimeout(() => resetTreeScroll(), 120)
    setTimeout(() => resetTreeScroll(), 400)
  }

  function filterTree(nodes, query) {
    const result = []
    for (const node of nodes) {
      const children = node.children ? filterTree(node.children, query) : []
      const selfMatch = (node.title || '').toLowerCase().includes(query)
      if (selfMatch || children.length) {
        result.push({ ...node, children })
      }
    }
    return result
  }

  function getNodePath(nodes, id, path = []) {
    for (const node of nodes) {
      const nextPath = [...path, node.title]
      if (node.id === id) return nextPath
      if (node.children?.length) {
        const childPath = getNodePath(node.children, id, nextPath)
        if (childPath.length) return childPath
      }
    }
    return []
  }

  return {
    treeLoading,
    tree,
    treeQuery,
    treeContainerRef,
    selectedDoc,
    activeId,
    editing,
    isCreating,
    saveLoading,
    editForm,
    docTypes,
    flatPages,
    flatFilteredPages,
    selectedPath,
    loadTree,
    loadDoc,
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
    findDocInTree,
  }
}
