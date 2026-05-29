<template>
  <div class="d-flex justify-space-between my-8">
    <v-card min-width="300px">
      <v-card-item>
        <p
          v-for="(item, i) in statusListItems"
          :key="i"
          class="my-4"
        >
          {{ item.title.toUpperCase() }}: <span :class="`aqa-color--${item.title.toUpperCase()}`">{{ item.value }}</span>
        </p>
      </v-card-item>
    </v-card>
    <v-card min-width="300px">
      <v-card-item>
        <reports-pie-chart-component v-if="dataChart" :data-chart="dataChart" />
      </v-card-item>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import ReportsPieChartComponent from '@/components/reports/reportsPieChartComponent.vue'
import { color } from '@/components/common/collorList'

const props = defineProps({
  statusList: Object
})

const statusListItems = ref([])
const dataChart = ref(undefined)

function draw() {
  dataChart.value = {
    labelList: [],
    colorList: [],
    dataList: []
  }
  statusListItems.value = []
  for (const elem of Object.keys(props.statusList)) {
    statusListItems.value.push({ title: elem, value: props.statusList[elem] })
    dataChart.value.labelList.push(elem)
    dataChart.value.colorList.push(color[elem ? elem.toLowerCase() : 'null'])
    dataChart.value.dataList.push(props.statusList[elem])
  }
}

onMounted(draw)
watch(() => props.statusList, draw, { deep: true })
</script>

<style scoped>
</style>
