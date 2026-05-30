import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { testPlanService, testCaseService, testRunService } from '@/services'
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

  const availableCases = ref([])
  const casesPage = ref(1)
  const casesHasMore = ref(true)
  const loadingCases = ref(false)

  const selectedCases = ref([])
  const caseSearch = ref('')
  const savingCases = ref(false)
  const searchDebounce = ref(null)

  const caseDialogOpen = ref(false)
  const selectedCase = ref(null)

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

      const runsRes = await testRunService.listBySpace(spaceId.value, { page: 1, page_size: 100 })
      runs.value = (runsRes.data.items || []).filter(r => r.plan_id === planId.value)
    } catch (e) {
      log.error('loadPlan failed', e)
    } finally {
      loader.value = false
    }
  }

  async function doLoadCases(page, search) {
    const res = await testCaseService.listBySpace(spaceId.value, {
      page,
      page_size: CASES_PAGE_SIZE,
      search: search || undefined,
    })
    return res.data.items || []
  }

  async function loadMoreCases() {
    if (loadingCases.value || !casesHasMore.value) return
    loadingCases.value = true
    try {
      const items = await doLoadCases(casesPage.value, caseSearch.value)
      availableCases.value.push(...items)
      casesPage.value += 1
      if (items.length < CASES_PAGE_SIZE) {
        casesHasMore.value = false
      }
    } catch (e) {
      log.error('loadMoreCases failed', e)
    } finally {
      loadingCases.value = false
    }
  }

  async function reloadCasesWithSearch() {
    clearTimeout(searchDebounce.value)
    searchDebounce.value = setTimeout(async () => {
      availableCases.value = []
      casesPage.value = 1
      casesHasMore.value = true
      loadingCases.value = true
      try {
        const items = await doLoadCases(1, caseSearch.value)
        availableCases.value = items
        casesPage.value = 2
        if (items.length < CASES_PAGE_SIZE) {
          casesHasMore.value = false
        }
      } catch (e) {
        log.error('reloadCasesWithSearch failed', e)
      } finally {
        loadingCases.value = false
      }
    }, 300)
  }

  watch(caseSearch, reloadCasesWithSearch)

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
    loadMoreCases()
  }

  return {
    spaceId,
    planId,
    plan,
    cases,
    runs,
    loader,
    availableCases,
    casesPage,
    casesHasMore,
    loadingCases,
    selectedCases,
    caseSearch,
    savingCases,
    filteredAvailableCases,
    caseMap,
    caseDialogOpen,
    selectedCase,
    loadPlan,
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
