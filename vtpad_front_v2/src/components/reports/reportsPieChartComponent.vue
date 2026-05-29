<template>
  <Doughnut v-if="loaded" :data="data" :options="options" :style="myStyles" />
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { Doughnut } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  dataChart: Object
})

const loaded = ref(false)
const data = ref(undefined)
const options = ref({
  responsive: false,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'left'
    }
  }
})

const myStyles = computed(() => ({
  height: '150px',
  position: 'relative'
}))

function updateChart() {
  const temp = props.dataChart
  data.value = {
    labels: temp.labelList,
    datasets: [
      {
        backgroundColor: temp.colorList,
        data: temp.dataList
      }
    ]
  }
}

watch(() => props.dataChart, updateChart, { deep: true })

onMounted(() => {
  updateChart()
  loaded.value = true
})
</script>

<style scoped>
</style>
