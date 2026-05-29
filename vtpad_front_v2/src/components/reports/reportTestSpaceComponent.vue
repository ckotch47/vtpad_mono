<template>
  <aqa-report-select-component :test-list="testList" @select-test-lst-emit="selectTestByList" />

  <aqa-report-statistic-test-component
    v-if="testDetail?.statistic && testId"
    :status-list="testDetail.statistic"
  />

  <aqa-report-suite-main-component v-if="testId" :list-suite="suiteList" />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { reportService } from '@/services'
import AqaReportSelectComponent from '@/components/reports/aqa-report/aqaReportSelectComponent.vue'
import AqaReportStatisticTestComponent from '@/components/reports/aqa-report/aqaReportStatisticTestComponent.vue'
import AqaReportSuiteMainComponent from '@/components/reports/aqa-report/aqaReportSuite/aqaReportSuiteMainComponent.vue'

const route = useRoute()
const spaceId = computed(() => route.params.spaceId)

const testList = ref([])
const suiteList = ref([])
const testId = ref(undefined)
const testDetail = ref(undefined)

function getTestList() {
  reportService.listTests(spaceId.value).then(res => {
    testList.value = res.data
  })
}

function getTestDetail() {
  if (!testId.value) return
  reportService.getTestDetail(spaceId.value, testId.value).then(res => {
    testDetail.value = res.data
  })
}

function getSuiteList() {
  reportService.getTestSuites(spaceId.value, testId.value).then(res => {
    suiteList.value = res.data
  })
}

function selectTestByList(id) {
  testId.value = id
  getTestDetail()
  getSuiteList()
}

onMounted(() => getTestList())
</script>

<style lang="scss">
.aqa-color {
  &--PASSED { color: #41b883; }
  &--SKIPPED { color: #e6bb00; }
  &--FAILED { color: #e6003a; }
  &--UNKNOWN { color: #363636; }
}
</style>
