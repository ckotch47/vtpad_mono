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
  const allCasesLoading = ref(false)
  const allCasesError = ref('')
  const testCasesLoading = ref(false)
  const testCasesError = ref('')
  const loader = ref(true)
  const suiteError = ref('')
  const caseSearch = ref('')
  const openAddCase = ref(false)
  const openAddExistingCase = ref(false)
  const existingCases = ref([])
  const selectedExistingCases = ref([])
  const existingCaseSearch = ref('')
  const existingSearchDebounce = ref(null)
  const newCase = ref({ title: '', type: 'manual', steps: '' })
  const creatingCase = ref(false)
  const moveCaseOpen = ref(false)
  const moveCaseItem = ref(null)
  const moveCaseTargetSectionId = ref(null)
  const movingCase = ref(false)
  const moveCaseError = ref('')
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
  let caseListRequestId = 0
  let allCasesRequestId = 0

  const defaultSection = computed(() => ({
    id: null,
    name: 'Default',
    isDefault: true,
    test_case_count: allCases.value.filter(tc => tc.section_id == null).length,
  }))

  const hasDefaultSection = computed(() =>
    flatSections.value.length === 0 || defaultSection.value.test_case_count > 0
  )

  const filteredTestCases = computed(() => {
    const q = String(caseSearch.value ?? '').toLowerCase().trim()
    if (!q) return testCases.value
    return testCases.value.filter(tc =>
      tc.title?.toLowerCase().includes(q) ||
      tc.short_name?.toLowerCase().includes(q)
    )
  })

  const filteredExistingCases = computed(() => {
    const q = String(existingCaseSearch.value ?? '').toLowerCase().trim()
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
    const requestedSuiteId = suiteId.value
    if (!requestedSuiteId) {
      suiteError.value = 'Test suite was not found or you do not have access to it.'
      loader.value = false
      return
    }
    testSuiteService.getById(requestedSuiteId).then(res => {
      if (String(suiteId.value) !== String(requestedSuiteId)) return
      suite.value = res.data
      breadcrumbItems.value = [
        { title: 'Test Suites', to: `/space/${spaceId.value}/test-suites` },
        { title: suite.value.name }
      ]
      suiteError.value = ''
      loader.value = false
    }).catch(() => {
      if (String(suiteId.value) !== String(requestedSuiteId)) return
      suite.value = {}
      suiteError.value = 'Test suite was not found or you do not have access to it.'
      loader.value = false
    })
  }

  function loadSections() {
    const requestedSuiteId = suiteId.value
    sectionService.getTree(requestedSuiteId).then(res => {
      if (String(suiteId.value) !== String(requestedSuiteId)) return
      sectionTree.value = res.data
      flatSections.value = flattenTree(res.data)
      if (flatSections.value.length === 0 && !selectedSection.value) {
        onDefaultSectionSelect()
      }
    }).catch(() => {
      if (String(suiteId.value) !== String(requestedSuiteId)) return
      sectionTree.value = []
      flatSections.value = []
    })
  }

  function loadAllCases() {
    const requestedSuiteId = suiteId.value
    const currentRequestId = ++allCasesRequestId
    allCasesLoading.value = true
    allCasesError.value = ''
    if (selectedSection.value?.isDefault) {
      testCasesLoading.value = true
      testCasesError.value = ''
      testCases.value = []
    }
    testCaseService.listBySuite(requestedSuiteId).then(res => {
      if (String(suiteId.value) !== String(requestedSuiteId) || currentRequestId !== allCasesRequestId) return
      allCases.value = res.data
      allCasesError.value = ''
      if (selectedSection.value?.isDefault) {
        testCases.value = unassignedCases()
        testCasesLoading.value = false
        testCasesError.value = ''
      }
    }).catch(() => {
      if (String(suiteId.value) !== String(requestedSuiteId) || currentRequestId !== allCasesRequestId) return
      allCases.value = []
      allCasesError.value = 'Could not load test cases for this section.'
      if (selectedSection.value?.isDefault) {
        testCases.value = []
        testCasesLoading.value = false
        testCasesError.value = allCasesError.value
      }
    }).finally(() => {
      if (currentRequestId === allCasesRequestId) allCasesLoading.value = false
    })
  }

  function flattenTree(nodes, list = [], level = 0, parentId = null) {
    for (const n of nodes || []) {
      list.push({ id: n.id, name: n.name, level, parentId, test_case_count: n.test_case_count || 0 })
      flattenTree(n.children, list, level + 1, n.id)
    }
    return list
  }

  function onSectionsReordered(orderedSections) {
    flatSections.value = orderedSections
  }

  function onSectionSelect(id) {
    selectedSection.value = flatSections.value.find(s => s.id === id) || { id, name: 'Section' }
    loadTestCases(id)
  }

  function onDefaultSectionSelect() {
    caseListRequestId += 1
    selectedSection.value = defaultSection.value
    testCasesError.value = allCasesError.value
    testCasesLoading.value = allCasesLoading.value
    testCases.value = allCasesLoading.value ? [] : unassignedCases()
  }

  function unassignedCases() {
    return allCases.value.filter(tc => tc.section_id == null)
  }

  function loadTestCases(sectionId) {
    const requestedSuiteId = suiteId.value
    const currentRequestId = ++caseListRequestId
    if (sectionId == null) {
      testCasesError.value = allCasesError.value
      testCasesLoading.value = allCasesLoading.value
      testCases.value = allCasesLoading.value ? [] : unassignedCases()
      return
    }

    testCasesError.value = ''
    testCasesLoading.value = true
    testCases.value = []
    testCaseService.listBySection(sectionId).then(res => {
      if (String(suiteId.value) !== String(requestedSuiteId) || currentRequestId !== caseListRequestId) return
      testCases.value = res.data
      testCasesLoading.value = false
      if (openAddExistingCase.value) {
        loadExistingCases(existingCaseSearch.value)
      }
    }).catch(() => {
      if (String(suiteId.value) === String(requestedSuiteId) && currentRequestId === caseListRequestId) {
        testCases.value = []
        testCasesLoading.value = false
        testCasesError.value = 'Could not load test cases for this section.'
      }
    })
  }

  function retrySelectedSection() {
    if (!selectedSection.value) return
    if (selectedSection.value.isDefault) {
      loadAllCases()
      return
    }
    loadTestCases(selectedSection.value.id)
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
      testCasesLoading.value = false
      testCasesError.value = ''
      loadSections()
      loadAllCases()
    })
  }

  function openMoveCaseDialog(testCase) {
    moveCaseItem.value = testCase
    moveCaseTargetSectionId.value = testCase.section_id ?? null
    moveCaseError.value = ''
    moveCaseOpen.value = true
  }

  async function moveCaseToSection(targetSectionId) {
    if (!moveCaseItem.value || movingCase.value) return
    movingCase.value = true
    moveCaseError.value = ''
    try {
      await testCaseService.move(moveCaseItem.value.id, suiteId.value, targetSectionId)
      moveCaseOpen.value = false
      moveCaseItem.value = null
      loadSections()
      loadAllCases()
      if (targetSectionId == null) onDefaultSectionSelect()
      else onSectionSelect(targetSectionId)
    } catch (error) {
      moveCaseError.value = error?.response?.data?.detail || 'Could not move this test case. Please try again.'
    } finally {
      movingCase.value = false
    }
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
        section_id: selectedSection.value.isDefault ? null : selectedSection.value.id
      })
    )
    Promise.all(promises).then(() => {
      openAddExistingCase.value = false
      loadAllCases()
      if (!selectedSection.value?.isDefault) {
        loadTestCases(selectedSection.value.id)
      }
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
      section_id: selectedSection.value.isDefault ? null : selectedSection.value.id
    }).then(() => {
      openAddCase.value = false
      newCase.value = { title: '', type: 'manual', steps: '' }
      loadAllCases()
      if (!selectedSection.value?.isDefault) {
        loadTestCases(selectedSection.value.id)
      }
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
    caseListRequestId += 1
    allCasesRequestId += 1
    loader.value = true
    suiteError.value = ''
    suite.value = {}
    sectionTree.value = []
    flatSections.value = []
    selectedSection.value = null
    testCases.value = []
    allCases.value = []
    allCasesLoading.value = false
    allCasesError.value = ''
    testCasesLoading.value = false
    testCasesError.value = ''
    breadcrumbItems.value = []
    loadSuite()
    loadSections()
    loadAllCases()
  }

  watch(suiteId, (nextSuiteId, previousSuiteId) => {
    if (nextSuiteId && nextSuiteId !== previousSuiteId) init()
  })

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
    onSectionsReordered,
    selectedSection,
    defaultSection,
    hasDefaultSection,
    testCases,
    allCases,
    testCasesLoading,
    testCasesError,
    loader,
    suiteError,
    caseSearch,
    openAddCase,
    openAddExistingCase,
    existingCases,
    selectedExistingCases,
    existingCaseSearch,
    newCase,
    creatingCase,
    moveCaseOpen,
    moveCaseItem,
    moveCaseTargetSectionId,
    movingCase,
    moveCaseError,
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
    onDefaultSectionSelect,
    loadTestCases,
    retrySelectedSection,
    caseCountByType,
    typeIcon,
    typeColor,
    statusColor,
    openSectionDialog,
    openRenameDialog,
    saveSection,
    deleteSection,
    openMoveCaseDialog,
    moveCaseToSection,
    loadExistingCases,
    addExistingCases,
    addTestCase,
    openCaseDialog,
    createRun,
    init,
  }
}
