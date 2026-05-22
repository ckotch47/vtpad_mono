<template>
  <Doughnut v-if="loaded" :data="data"  :options="options" :style="myStyles" />
</template>

<script>
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { Doughnut } from 'vue-chartjs'
ChartJS.register(ArcElement, Tooltip, Legend)
export default {
  name: "reportsPieChartComponent",
  components: { Doughnut },
  props:{
    dataChart: {
      type: Object
    }
  },
  watch:{
    dataChart:{
      handler() {
        const temp = this.dataChart;
        this.data = {
          labels: temp.labelList,
          datasets: [
            {
              backgroundColor: temp.colorList, //['#41b883', '#e4c451', '#ff0026', '#4244c4'],
              data: temp.dataList,
            }
          ]
        };
      }
    }
  },
  computed: {
    myStyles () {
      return {
        height: `150px`,
        position: 'relative'
      }
    }
  },
  data() {
    return {
      loaded: false,
      dataChart1: {
        PASSED: 0,
        SKIPPED: 0,
        FAILED: 0,
        UNKNOWN: 0
      },
      data: undefined,
      options: {
        responsive: false,
        maintainAspectRatio: false,
        plugins:{
          legend:{
            position: 'left'
          }
        }
      }
    }
  },
  mounted() {
    const temp = this.dataChart;
    this.data = {
      labels: temp.labelList,
      datasets: [
        {
          backgroundColor: temp.colorList, //['#41b883', '#e4c451', '#ff0026', '#4244c4'],
          data: temp.dataList,
        }
      ]
    };
    this.loaded = true;
  }
}
</script>

<style scoped>

</style>
