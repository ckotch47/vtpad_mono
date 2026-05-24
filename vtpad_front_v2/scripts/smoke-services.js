import * as services from '@/services/index.js'

const EXPECTED = {
  authService: ['login', 'refresh'],
  userService: ['getCurrent', 'updateCurrent', 'searchByMail'],
  spaceService: ['list', 'create', 'getById', 'getByShort', 'update', 'delete', 'getUsers', 'addUser', 'removeUser', 'updateUser', 'makeOwner', 'getStatistic', 'getAllRuns'],
  companyUserService: ['list', 'create', 'update', 'resetPassword', 'delete'],
  tagService: ['list', 'create', 'update', 'delete'],
  bugService: ['list', 'getById', 'getByShort', 'getFilters', 'create', 'update'],
  commentService: ['list', 'create', 'update', 'delete'],
  notificationService: ['list', 'unreadCount', 'markRead', 'markAllRead'],
  fileService: ['upload'],
  sectionService: ['getTree', 'create', 'update', 'delete', 'sort'],
  testCaseService: ['listBySpace', 'listBySuite', 'listBySection', 'getById', 'create', 'update', 'delete', 'sort', 'getRuns', 'duplicate'],
  testSuiteService: ['listBySpace', 'getById', 'create', 'update', 'delete', 'sort'],
  testPlanService: ['listBySpace', 'getById', 'getCases', 'create', 'update', 'delete'],
  testRunService: ['listBySpace', 'getById', 'getDetail', 'create', 'update', 'start', 'complete', 'delete', 'updateResult', 'bulkUpdateResults', 'getStepResults', 'updateStepResults'],
  techDocService: ['getTree', 'listBySpace', 'getById', 'create', 'update', 'delete'],
  reportService: ['listTests', 'getTestDetail', 'getTestSuites', 'getSuiteDetail'],
  analyticsService: ['getSpaceStats', 'getTrend', 'getTopFailed', 'getCoverage'],
  qaReportService: ['getUsers', 'getBugList'],
  uploadService: ['upload'],
}

let passed = 0
let failed = 0

for (const [name, methods] of Object.entries(EXPECTED)) {
  const svc = services[name]
  if (!svc) {
    console.error(`❌ Missing service: ${name}`)
    failed++
    continue
  }

  let ok = true
  for (const m of methods) {
    if (typeof svc[m] !== 'function') {
      console.error(`❌ ${name}.${m} is not a function`)
      ok = false
      failed++
    }
  }

  if (ok) {
    passed++
  }
}

// Smoke: calling a method should return a thenable (axios promise)
try {
  const result = services.testCaseService.getById('00000000-0000-0000-0000-000000000000')
  if (result && typeof result.then === 'function') {
    console.log('✅ Method returns a Promise-like object')
  } else {
    console.error('❌ Method does not return a thenable')
    failed++
  }
} catch (e) {
  console.error('❌ Smoke call failed:', e.message)
  failed++
}

console.log(`\n${passed}/${Object.keys(EXPECTED).length} services OK, ${failed} issues`)
if (failed > 0) process.exit(1)
