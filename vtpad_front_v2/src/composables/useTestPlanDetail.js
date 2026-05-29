import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { testPlanService, testCaseService, testSuiteService, testRunService, sectionService } from '@/services'
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

  const allSuites = ref([])
  const allSections = ref([])

  const editSuiteIds = ref([])
  const savingSuites = ref(false)

  const sectionSourceSuite = ref(null)
  const sourceSections = ref([])
  const editSectionIds = ref([])
  const savingSections = ref(false)

  const caseSourceSuites = ref([])
  const caseSourceSections = ref([])
  const caseSourceSectionsList = ref([])
  const availableCases = ref([])
  const selectedCases = ref([])
  const caseSearch = ref('')
  const savingCases = ref(false)

  const caseDialogOpen = ref(false)
  const selectedCase = ref(null)

  const suiteIdsChanged = computed(() => {
    const current = plan.value.suite_ids || []
    if (editSuiteIds.value.length !== current.length) return true
    return editSuiteIds.value.some(id => !current.includes(id)) || current.some(id => !editSuiteIds.value.includes(id))
  })

  const filteredAvailableCases = computed(() => {
    const q = caseSearch.value.toLowerCase().trim()
    if (!q) return availableCases.value
    return availableCases.value.filter(tc => tc.title?.toLowerCase().includes(q))
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
      log.error('loadPlan failed', e)
    }
  }

  async function loadAllSections() {
    if (!allSuites.value.length) return
    const promises = allSuites.value.map(suite =>
      sectionService.listBySuite(suite.id).catch(() => ({ data: [] }))
    )
    const responses = await Promise.all(promises)
    const all = []
    const seen = new Set()
    for (const res of responses) {
      for (const section of (res.data || [])) {
        if (!seen.has(section.id)) {
          seen.add(section.id)
          all.push(section)
        }
      }
    }
    allSections.value = all
  }

  async function saveSuites() {
    savingSuites.value = true
    try {
      await testPlanService.update(planId.value, { suite_ids: editSuiteIds.value })
      await loadPlan()
    } catch (e) {
      log.error('loadPlan failed', e)
    } finally {
      savingSuites.value = false
    }
  }

  function resetSuiteIds() {
    editSuiteIds.value = [...(plan.value.suite_ids || [])]
  }

  async function onSectionSourceSuiteChange() {
    editSectionIds.value = []
    if (!sectionSourceSuite.value) {
      sourceSections.value = []
      return
    }
    try {
      const res = await sectionService.listBySuite(sectionSourceSuite.value)
      sourceSections.value = res.data || []
    } catch (e) {
      log.error('loadPlan failed', e)
      sourceSections.value = []
    }
  }

  async function saveSections() {
    savingSections.value = true
    try {
      const current = plan.value.section_ids || []
      const merged = [...new Set([...current, ...editSectionIds.value])]
      await testPlanService.update(planId.value, { section_ids: merged })
      editSectionIds.value = []
      sectionSourceSuite.value = null
      sourceSections.value = []
      await loadPlan()
    } catch (e) {
      log.error('loadPlan failed', e)
    } finally {
      savingSections.value = false
    }
  }

  async function removeSection(sectionId) {
    const current = (plan.value.section_ids || []).filter(id => id !== sectionId)
    try {
      await testPlanService.update(planId.value, { section_ids: current })
      await loadPlan()
    } catch (e) {
      log.error('loadPlan failed', e)
    }
  }

  async function removeCase(caseId) {
    const current = (plan.value.case_ids || []).filter(id => id !== caseId)
    try {
      await testPlanService.update(planId.value, { case_ids: current })
      await loadPlan()
    } catch (e) {
      log.error('loadPlan failed', e)
    }
  }

  async function onCaseSourceSuitesChange() {
    caseSourceSections.value = []
    caseSourceSectionsList.value = []
    availableCases.value = []
    selectedCases.value = []
    if (!caseSourceSuites.value.length) return
    try {
      const promises = caseSourceSuites.value.map(suiteId =>
        sectionService.listBySuite(suiteId)
      )
      const responses = await Promise.all(promises)
      const all = []
      const seen = new Set()
      for (const res of responses) {
        for (const section of (res.data || [])) {
          if (!seen.has(section.id)) {
            seen.add(section.id)
            all.push(section)
          }
        }
      }
      caseSourceSectionsList.value = all
    } catch (e) {
      log.error('loadPlan failed', e)
      caseSourceSectionsList.value = []
    }
  }

  async function onCaseSourceSectionsChange() {
    availableCases.value = []
    selectedCases.value = []
    if (!caseSourceSections.value.length && !caseSourceSuites.value.length) return
    try {
      let allCases = []
      const validSections = (caseSourceSections.value || []).filter(Boolean)
      if (validSections.length) {
        const promises = validSections.map(sectionId =>
          testCaseService.listBySection(sectionId)
        )
        const responses = await Promise.all(promises)
        allCases = responses.flatMap(r => r.data)
      } else {
        const promises = caseSourceSuites.value.map(suiteId =>
          testCaseService.listBySuite(suiteId)
        )
        const responses = await Promise.all(promises)
        allCases = responses.flatMap(r => r.data)
      }
      const seen = new Set()
      availableCases.value = allCases.filter(tc => {
        if (seen.has(tc.id)) return false
        seen.add(tc.id)
        return true
      })
    } catch (e) {
      log.error('loadPlan failed', e)
      availableCases.value = []
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
      log.error('loadPlan failed', e)
    } finally {
      savingCases.value = false
    }
  }

  function selectAllAvailable() {
    const availableIds = filteredAvailableCases.value
      .filter(tc => !isCaseInPlan(tc.id))
      .map(tc => tc.id)
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
      log.error('loadPlan failed', e)
    }
  }

  function openCaseDialog(id) {
    testCaseService.getById(id).then(res => {
      selectedCase.value = res.data
      caseDialogOpen.value = true
    })
  }

  function sectionName(sectionId) {
    const found = allSections.value.find(s => s.id === sectionId)
    return found?.name || sectionId
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

  watch(sectionSourceSuite, () => onSectionSourceSuiteChange())
  watch(caseSourceSuites, () => onCaseSourceSuitesChange())
  watch(caseSourceSections, () => onCaseSourceSectionsChange())

  function init() {
    loadPlan()
    loadSuites().then(() => loadAllSections())
  }

  return {
    spaceId,
    planId,
    plan,
    cases,
    runs,
    loader,
    allSuites,
    allSections,
    editSuiteIds,
    savingSuites,
    suiteIdsChanged,
    sectionSourceSuite,
    sourceSections,
    editSectionIds,
    savingSections,
    caseSourceSuites,
    caseSourceSections,
    caseSourceSectionsList,
    availableCases,
    selectedCases,
    caseSearch,
    savingCases,
    filteredAvailableCases,
    caseMap,
    caseDialogOpen,
    selectedCase,
    loadPlan,
    saveSuites,
    resetSuiteIds,
    onSectionSourceSuiteChange,
    saveSections,
    removeSection,
    removeCase,
    onCaseSourceSuitesChange,
    onCaseSourceSectionsChange,
    isCaseInPlan,
    addIndividualCases,
    selectAllAvailable,
    deselectAll,
    createRun,
    openCaseDialog,
    sectionName,
    typeIcon,
    typeColor,
    statusColor,
    runStatusColor,
    init,
  }
}
