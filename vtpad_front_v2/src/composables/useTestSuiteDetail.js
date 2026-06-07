import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { testSuiteService, sectionService, testCaseService, testRunService } from '@/services'

export function useTestSuiteDetail() {
  const route = useRoute()
  const router = useRouter()

  const spaceId = computed(() => route.params.spaceId)
  const suiteId = computed(() => route.params.suiteId)

  const suite = ref({})
  const sectionTree = ref([])
  const flatSections = ref([])
  const selectedSection = ref(null)
  const testCases = ref([])
  const allCases = ref([])
  const loader = ref(true)
  const caseSearch = ref('')
  const openAddCase = ref(false)
  const openAddExistingCase = ref(false)
  const existingCases = ref([])
  const selectedExistingCases = ref([])
  const existingCaseSearch = ref('')
  const existingSearchDebounce = ref(null)
  const newCase = ref({ title: '', type: 'manual', steps: '' })
  const creatingCase = ref(false)
  const sectionDialog = ref({
    open: false,
    isRename: false,
    id: null,
    parentId: null,
    name: '',
    description: ''
  })
  const caseDialogOpen = ref(false)
  const selectedCase = ref(null)
  const breadcrumbItems = ref([])

  const filteredTestCases = computed(() => {
    const q = caseSearch.value.toLowerCase().trim()
    if (!q) return testCases.value
    return testCases.value.filter(tc =>
      tc.title?.toLowerCase().includes(q) ||
      tc.short_name?.toLowerCase().includes(q)
    )
  })

  const filteredExistingCases = computed(() => {
    const q = existingCaseSearch.value.toLowerCase().trim()
    if (!q) return existingCases.value
    return existingCases.value.filter(tc => {
      const haystack = [
        tc.title,
        tc.short_name,
        tc.text,
        tc.steps,
        tc.expected_results,
        tc.preconditions,
        tc.postconditions,
        tc.external_id,
        tc.link,
        tc.type,
        tc.status,
      ].filter(Boolean).join(' ').toLowerCase()
      return haystack.includes(q)
    })
  })

  function loadSuite() {
    testSuiteService.getById(suiteId.value).then(res => {
      suite.value = res.data
      breadcrumbItems.value = [
        { title: 'Test Suites', to: `/space/${spaceId.value}/test-suites` },
        { title: suite.value.name }
      ]
      loader.value = false
    })
  }

  function loadSections() {
    sectionService.getTree(suiteId.value).then(res => {
      sectionTree.value = res.data
      flatSections.value = flattenTree(res.data)
    })
  }

  function loadAllCases() {
    testCaseService.listBySuite(suiteId.value).then(res => {
      allCases.value = res.data
    }).catch(() => {
      allCases.value = []
    })
  }

  function flattenTree(nodes, list = [], level = 0) {
    for (const n of nodes || []) {
      list.push({ id: n.id, name: n.name, level, test_case_count: n.test_case_count || 0 })
      flattenTree(n.children, list, level + 1)
    }
    return list
  }

  function onSectionSelect(id) {
    selectedSection.value = flatSections.value.find(s => s.id === id) || { id, name: 'Section' }
    loadTestCases(id)
  }

  function loadTestCases(sectionId) {
    testCaseService.listBySection(sectionId).then(res => {
      testCases.value = res.data
      if (openAddExistingCase.value) {
        loadExistingCases(existingCaseSearch.value)
      }
    })
  }

  function caseCountByType(type) {
    return allCases.value.filter(tc => tc.type === type).length
  }

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

  function openSectionDialog(parentId = null) {
    sectionDialog.value = {
      open: true,
      isRename: false,
      id: null,
      parentId,
      name: '',
      description: ''
    }
  }

  function openRenameDialog(item) {
    sectionDialog.value = {
      open: true,
      isRename: true,
      id: item.id,
      parentId: null,
      name: item.name,
      description: item.description || ''
    }
  }

  function saveSection() {
    if (sectionDialog.value.isRename) {
      sectionService.update(sectionDialog.value.id, {
        name: sectionDialog.value.name,
        description: sectionDialog.value.description || null
      }).then(() => {
        sectionDialog.value.open = false
        loadSections()
      })
    } else {
      sectionService.create({
        name: sectionDialog.value.name,
        description: sectionDialog.value.description || null,
        suite_id: suiteId.value,
        parent_id: sectionDialog.value.parentId
      }).then(() => {
        sectionDialog.value.open = false
        loadSections()
      })
    }
  }

  function deleteSection(id) {
    if (!confirm('Delete this section? Test cases will remain but become unassigned.')) return
    sectionService.delete(id).then(() => {
      selectedSection.value = null
      testCases.value = []
      loadSections()
      loadAllCases()
    })
  }

  function removeCaseFromSection(id) {
    testCaseService.update(id, {
      section_id: null,
      suite_id: null
    }).then(() => {
      loadTestCases(selectedSection.value.id)
      loadAllCases()
    })
  }

  function loadExistingCases(search = '') {
    testCaseService.listBySpace(spaceId.value, {
      search: search || undefined,
      page: 1,
      page_size: 500,
    }).then(res => {
      const currentIds = new Set(testCases.value.map(tc => tc.id))
      existingCases.value = (res.data.items || []).filter(tc => !currentIds.has(tc.id))
      selectedExistingCases.value = []
    }).catch(() => {
      existingCases.value = []
    })
  }

  function scheduleExistingCasesLoad() {
    if (!openAddExistingCase.value) return
    clearTimeout(existingSearchDebounce.value)
    existingSearchDebounce.value = setTimeout(() => {
      loadExistingCases(existingCaseSearch.value)
    }, 250)
  }

  function addExistingCases() {
    const promises = selectedExistingCases.value.map(id =>
      testCaseService.update(id, {
        suite_id: suiteId.value,
        section_id: selectedSection.value.id
      })
    )
    Promise.all(promises).then(() => {
      openAddExistingCase.value = false
      loadTestCases(selectedSection.value.id)
      loadAllCases()
    })
  }

  function addTestCase() {
    creatingCase.value = true
    testCaseService.create({
      title: newCase.value.title,
      type: newCase.value.type,
      steps: newCase.value.steps,
      space_id: spaceId.value,
      suite_id: suiteId.value,
      section_id: selectedSection.value.id
    }).then(() => {
      openAddCase.value = false
      newCase.value = { title: '', type: 'manual', steps: '' }
      loadTestCases(selectedSection.value.id)
      loadAllCases()
    }).finally(() => {
      creatingCase.value = false
    })
  }

  function openCaseDialog(id) {
    testCaseService.getById(id).then(res => {
      selectedCase.value = res.data
      caseDialogOpen.value = true
    })
  }

  function createRun() {
    testRunService.create({
      name: `Run for ${suite.value.name}`,
      space_id: spaceId.value,
      suite_id: suiteId.value
    }).then(res => {
      router.push(`/space/${spaceId.value}/test-runs/${res.data.id}`)
    })
  }

  function init() {
    loadSuite()
    loadSections()
    loadAllCases()
  }

  watch(openAddExistingCase, (open) => {
    if (open) {
      loadExistingCases(existingCaseSearch.value)
    } else {
      clearTimeout(existingSearchDebounce.value)
    }
  })

  watch(existingCaseSearch, scheduleExistingCasesLoad)

  return {
    spaceId,
    suiteId,
    suite,
    sectionTree,
    flatSections,
    selectedSection,
    testCases,
    allCases,
    loader,
    caseSearch,
    openAddCase,
    openAddExistingCase,
    existingCases,
    selectedExistingCases,
    existingCaseSearch,
    newCase,
    creatingCase,
    sectionDialog,
    caseDialogOpen,
    selectedCase,
    breadcrumbItems,
    filteredTestCases,
    filteredExistingCases,
    loadSuite,
    loadSections,
    loadAllCases,
    flattenTree,
    onSectionSelect,
    loadTestCases,
    caseCountByType,
    typeIcon,
    typeColor,
    statusColor,
    openSectionDialog,
    openRenameDialog,
    saveSection,
    deleteSection,
    removeCaseFromSection,
    loadExistingCases,
    addExistingCases,
    addTestCase,
    openCaseDialog,
    createRun,
    init,
  }
}
