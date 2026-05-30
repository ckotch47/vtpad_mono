import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { testPlanService, testCaseService, testRunService } from '@/services'
import { useLogger } from './useLogger'

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

  const allCases = ref([])
  const selectedCases = ref([])
  const caseSearch = ref('')
  const savingCases = ref(false)

  const caseDialogOpen = ref(false)
  const selectedCase = ref(null)

  const filteredAvailableCases = computed(() => {
    const q = caseSearch.value.toLowerCase().trim()
    const plannedIds = new Set((plan.value.case_ids || []))
    let list = allCases.value.filter(tc => !plannedIds.has(tc.id))
    if (q) {
      list = list.filter(tc => tc.title?.toLowerCase().includes(q))
    }
    return list
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

  async function loadAllCases() {
    try {
      const res = await testCaseService.listBySpace(spaceId.value, { page: 1, page_size: 1000 })
      allCases.value = res.data.items || []
    } catch (e) {
      log.error('loadAllCases failed', e)
    }
  }

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
    loadAllCases()
  }

  return {
    spaceId,
    planId,
    plan,
    cases,
    runs,
    loader,
    allCases,
    selectedCases,
    caseSearch,
    savingCases,
    filteredAvailableCases,
    caseMap,
    caseDialogOpen,
    selectedCase,
    loadPlan,
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
