<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>
  <v-card v-if="!loader" min-height="400">
    <v-card-item>
      <div class="d-flex">
        <statistic-page-pad-component v-if="statisticItem?.pads" :pads-statistic="statisticItem.pads" />
      </div>
    </v-card-item>

    <v-card-item v-if="statisticItem?.runs?.state.length > 0">
      <div class="d-flex justify-space-between">
        <statistic-page-run-component :run-statistic="statisticItem.runs" />
        <reports-pie-chart-component v-if="dataChartRuns" :data-chart="dataChartRuns" />
      </div>
    </v-card-item>

    <v-card-item v-if="statisticItem?.bugs?.state.length > 0">
      <div class="d-flex justify-space-between">
        <statistic-page-bugs-component :bug-statistic="statisticItem.bugs" />
        <reports-pie-chart-component v-if="dataChartBugs" :data-chart="dataChartBugs" />
      </div>
    </v-card-item>
  </v-card>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import StatisticPagePadComponent from '@/components/reports/statisticPage/statisticPagePadComponent.vue'
import StatisticPageRunComponent from '@/components/reports/statisticPage/statisticPageRunComponent.vue'
import StatisticPageBugsComponent from '@/components/reports/statisticPage/statisticPageBugsComponent.vue'
import ReportsPieChartComponent from '@/components/reports/reportsPieChartComponent.vue'
import { spaceService } from '@/services'
import { color } from '@/components/common/collorList'

const route = useRoute()
const spaceId = ref(route.params.spaceId)

const loader = ref(true)
const statisticItem = ref({})
const dataChartRuns = ref(undefined)
const dataChartBugs = ref(undefined)

function getStatistics() {
  spaceService.getStatistic(spaceId.value).then(res => {
    statisticItem.value = res.data
    updateChartsRuns()
    updateChartsBugs()
    loader.value = false
  })
}

function updateChartsRuns() {
  dataChartRuns.value = {
    labelList: [],
    colorList: [],
    dataList: []
  }
  for (const elem of statisticItem.value.runs.state) {
    dataChartRuns.value.labelList.push(elem.state ?? 'null')
    dataChartRuns.value.colorList.push(color[elem.state ? elem.state.toLowerCase() : 'null'])
    dataChartRuns.value.dataList.push(elem.item_count)
  }
}

function updateChartsBugs() {
  dataChartBugs.value = {
    labelList: [],
    colorList: [],
    dataList: []
  }
  for (const elem of statisticItem.value.bugs.state) {
    dataChartBugs.value.labelList.push(elem.state ?? 'null')
    dataChartBugs.value.colorList.push(color[elem.state ? elem.state.toLowerCase() : 'null'])
    dataChartBugs.value.dataList.push(elem.item_count)
  }
}

watch(() => route.params.spaceId, (val) => {
  loader.value = true
  spaceId.value = val
  statisticItem.value = undefined
  dataChartRuns.value = undefined
  dataChartBugs.value = undefined
  getStatistics()
}, { deep: false })

onMounted(getStatistics)
</script>

<style scoped>
</style>
