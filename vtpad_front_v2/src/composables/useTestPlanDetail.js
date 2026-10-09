import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { testPlanService, testCaseService, testRunService, testSuiteService } from '@/services'
import { useLogger } from './useLogger'

const CASES_PAGE_SIZE = 50

export function useTestPlanDetail() {
  const log = useLogger('useTestPlanDetail')
  const route = useRoute()
  const router = useRouter()

  const spaceId = computed(() => route.params.spaceId)
  const planId = computed(() => route.params.planId)

  const plan = ref({})
  const cases = ref([])
  const runs = ref([])
  const loader = ref(true)

  const allSuites = ref([])
  const editSuiteIds = ref([])
  const editFilters = ref({ priorities: [], tags: [], custom_fields: [] })
  const savingSuites = ref(false)
  const previewResult = ref(null)
  const previewError = ref('')
  const previewingSelection = ref(false)
  const previewRequestId = ref(0)

  const availableCases = ref([])
  const casesPage = ref(1)
  const casesHasMore = ref(true)
  const loadingCases = ref(false)
  const casesLoadError = ref(false)
  const casesLoadErrorStatus = ref(0)
  const casesRequestId = ref(0)

  const selectedCases = ref([])
  const caseSearch = ref('')
  const savingCases = ref(false)
  const searchDebounce = ref(null)

  const caseDialogOpen = ref(false)
  const selectedCase = ref(null)

  const suiteIdsChanged = computed(() => {
    const current = plan.value.suite_ids || []
    if (editSuiteIds.value.length !== current.length) return true
    return editSuiteIds.value.some(id => !current.includes(id)) || current.some(id => !editSuiteIds.value.includes(id))
  })
  const filtersChanged = computed(() => JSON.stringify(editFilters.value) !== JSON.stringify({
    priorities: plan.value.filters?.priorities || [],
    tags: plan.value.filters?.tags || [],
    custom_fields: plan.value.filters?.custom_fields || [],
  }))
  const selectionChanged = computed(() => suiteIdsChanged.value || filtersChanged.value)
  watch(
    () => JSON.stringify({ suite_ids: editSuiteIds.value, filters: editFilters.value, case_ids: plan.value.case_ids || [] }),
    () => {
      previewRequestId.value += 1
      previewResult.value = null
      previewError.value = ''
      previewingSelection.value = false
    }
  )

  const filteredAvailableCases = computed(() => {
    const plannedIds = new Set((plan.value.case_ids || []))
    return availableCases.value.filter(tc => !plannedIds.has(tc.id))
  })

  const caseMap = computed(() => {
    const map = {}
    for (const c of cases.value) {
      map[c.id] = c
    }
    return map
  })

  async function loadPlan() {
    loader.value = true
    try {
      const [planRes, casesRes] = await Promise.all([
        testPlanService.getById(planId.value),
        testPlanService.getCases(planId.value)
      ])
      plan.value = planRes.data
      cases.value = casesRes.data
      editSuiteIds.value = [...(planRes.data.suite_ids || [])]
      editFilters.value = {
        priorities: [...(planRes.data.filters?.priorities || [])],
        tags: [...(planRes.data.filters?.tags || [])],
        custom_fields: (planRes.data.filters?.custom_fields || []).map(item => ({ ...item })),
      }
      previewResult.value = null
      previewError.value = ''

      const runsRes = await testRunService.listBySpace(spaceId.value, { page: 1, page_size: 100 })
      runs.value = (runsRes.data.items || []).filter(r => r.plan_id === planId.value)
    } catch (e) {
      log.error('loadPlan failed', e)
    } finally {
      loader.value = false
    }
  }

  async function loadSuites() {
    try {
      const res = await testSuiteService.listBySpace(spaceId.value, { page: 1, page_size: 1000 })
      allSuites.value = res.data.items || []
    } catch (e) {
      log.error('loadSuites failed', e)
    }
  }

  async function saveSuites() {
    savingSuites.value = true
    try {
      await testPlanService.update(planId.value, { suite_ids: editSuiteIds.value, filters: editFilters.value })
      await loadPlan()
    } catch (e) {
      log.error('saveSuites failed', e)
    } finally {
      savingSuites.value = false
    }
  }

  function resetSuiteIds() {
    editSuiteIds.value = [...(plan.value.suite_ids || [])]
    editFilters.value = {
      priorities: [...(plan.value.filters?.priorities || [])],
      tags: [...(plan.value.filters?.tags || [])],
      custom_fields: (plan.value.filters?.custom_fields || []).map(item => ({ ...item })),
    }
    previewResult.value = null
    previewError.value = ''
  }

  async function previewSelection() {
    if (previewingSelection.value) return
    const requestId = ++previewRequestId.value
    const draft = {
      space_id: spaceId.value,
      suite_ids: [...editSuiteIds.value],
      case_ids: [...(plan.value.case_ids || [])],
      filters: JSON.parse(JSON.stringify(editFilters.value)),
    }
    const draftKey = JSON.stringify(draft)
    previewingSelection.value = true
    previewError.value = ''
    try {
      const response = await testPlanService.previewSelection(draft)
      const currentDraftKey = JSON.stringify({
        space_id: spaceId.value,
        suite_ids: editSuiteIds.value,
        case_ids: plan.value.case_ids || [],
        filters: editFilters.value,
      })
      if (requestId === previewRequestId.value && currentDraftKey === draftKey) previewResult.value = response.data
    } catch (e) {
      if (requestId === previewRequestId.value) previewError.value = e?.response?.data?.detail || 'Selection preview could not be loaded.'
    } finally {
      if (requestId === previewRequestId.value) previewingSelection.value = false
    }
  }

  async function doLoadCases(requestedSpaceId, page, search) {
    const res = await testCaseService.listBySpace(requestedSpaceId, {
      page,
      page_size: CASES_PAGE_SIZE,
      search: search || undefined,
    })
    return res.data.items || []
  }

  async function loadMoreCases() {
    if (loadingCases.value || !casesHasMore.value) return
    const currentRequest = casesRequestId.value
    const requestedSpaceId = String(spaceId.value)
    const requestedSearch = caseSearch.value
    const requestedPage = casesPage.value
    loadingCases.value = true
    casesLoadError.value = false
    try {
      const items = await doLoadCases(requestedSpaceId, requestedPage, requestedSearch)
      if (currentRequest !== casesRequestId.value || requestedSpaceId !== String(spaceId.value) || requestedSearch !== caseSearch.value) return
      availableCases.value.push(...items)
      casesPage.value += 1
      if (items.length < CASES_PAGE_SIZE) {
        casesHasMore.value = false
      }
    } catch (e) {
      if (currentRequest !== casesRequestId.value || requestedSpaceId !== String(spaceId.value) || requestedSearch !== caseSearch.value) return
      casesLoadError.value = true
      casesLoadErrorStatus.value = Number(e?.response?.status || 0)
      if (casesLoadErrorStatus.value === 403) {
        availableCases.value = []
        casesHasMore.value = false
      }
      log.error('loadMoreCases failed', e)
    } finally {
      if (currentRequest === casesRequestId.value) loadingCases.value = false
    }
  }

  async function reloadCasesWithSearch() {
    clearTimeout(searchDebounce.value)
    const currentRequest = ++casesRequestId.value
    const requestedSpaceId = String(spaceId.value)
    const requestedSearch = caseSearch.value
    searchDebounce.value = setTimeout(async () => {
      availableCases.value = []
      casesPage.value = 1
      casesHasMore.value = true
      loadingCases.value = true
      casesLoadError.value = false
      casesLoadErrorStatus.value = 0
      try {
        const items = await doLoadCases(requestedSpaceId, 1, requestedSearch)
        if (currentRequest !== casesRequestId.value || requestedSpaceId !== String(spaceId.value) || requestedSearch !== caseSearch.value) return
        availableCases.value = items
        casesPage.value = 2
        if (items.length < CASES_PAGE_SIZE) {
          casesHasMore.value = false
        }
      } catch (e) {
        if (currentRequest !== casesRequestId.value || requestedSpaceId !== String(spaceId.value) || requestedSearch !== caseSearch.value) return
        casesLoadError.value = true
        casesLoadErrorStatus.value = Number(e?.response?.status || 0)
        if (casesLoadErrorStatus.value === 403) {
          availableCases.value = []
          casesHasMore.value = false
        }
        log.error('reloadCasesWithSearch failed', e)
      } finally {
        if (currentRequest === casesRequestId.value) loadingCases.value = false
      }
    }, 300)
  }

  watch(caseSearch, reloadCasesWithSearch)
  watch(spaceId, (nextSpaceId, previousSpaceId) => {
    if (!nextSpaceId || nextSpaceId === previousSpaceId) return
    clearTimeout(searchDebounce.value)
    casesRequestId.value += 1
    availableCases.value = []
    casesPage.value = 1
    casesHasMore.value = true
    loadingCases.value = false
    casesLoadError.value = false
    casesLoadErrorStatus.value = 0
    caseSearch.value = ''
    selectedCases.value = []
    loadMoreCases()
  })

  async function removeCase(caseId) {
    const current = (plan.value.case_ids || []).filter(id => id !== caseId)
    try {
      await testPlanService.update(planId.value, { case_ids: current })
      await loadPlan()
    } catch (e) {
      log.error('removeCase failed', e)
    }
  }

  function isCaseInPlan(caseId) {
    return cases.value.some(c => c.id === caseId)
  }

  async function addIndividualCases() {
    savingCases.value = true
    try {
      const current = plan.value.case_ids || []
      const merged = [...new Set([...current, ...selectedCases.value])]
      await testPlanService.update(planId.value, { case_ids: merged })
      selectedCases.value = []
      await loadPlan()
    } catch (e) {
      log.error('addIndividualCases failed', e)
    } finally {
      savingCases.value = false
    }
  }

  function selectAllAvailable() {
    const availableIds = filteredAvailableCases.value.map(tc => tc.id)
    const newSelection = new Set([...selectedCases.value, ...availableIds])
    selectedCases.value = Array.from(newSelection)
  }

  function deselectAll() {
    selectedCases.value = []
  }

  async function createRun() {
    try {
      const res = await testRunService.create({
        name: `Run for ${plan.value.name}`,
        space_id: spaceId.value,
        plan_id: planId.value
      })
      router.push(`/space/${spaceId.value}/test-runs/${res.data.id}`)
    } catch (e) {
      log.error('createRun failed', e)
    }
  }

  function openCaseDialog(id) {
    testCaseService.getById(id).then(res => {
      selectedCase.value = res.data
      caseDialogOpen.value = true
    })
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

  function runStatusColor(status) {
    const map = { draft: 'grey', active: 'primary', completed: 'success' }
    return map[status] || 'grey'
  }

  function init() {
    loadPlan()
    loadSuites()
    loadMoreCases()
  }

  return {
    spaceId,
    planId,
    plan,
    cases,
    runs,
    loader,
    allSuites,
    editSuiteIds,
    editFilters,
    savingSuites,
    suiteIdsChanged,
    filtersChanged,
    selectionChanged,
    previewResult,
    previewError,
    previewingSelection,
    availableCases,
    casesPage,
    casesHasMore,
    loadingCases,
    casesLoadError,
    casesLoadErrorStatus,
    selectedCases,
    caseSearch,
    savingCases,
    filteredAvailableCases,
    caseMap,
    caseDialogOpen,
    selectedCase,
    loadPlan,
    loadSuites,
    saveSuites,
    resetSuiteIds,
    previewSelection,
    loadMoreCases,
    removeCase,
    isCaseInPlan,
    addIndividualCases,
    selectAllAvailable,
    deselectAll,
    createRun,
    openCaseDialog,
    typeIcon,
    typeColor,
    statusColor,
    runStatusColor,
    init,
  }
}
