<template>
  <div class="d-flex justify-space-between my-8">
    <v-card min-width="300px">
      <v-card-item>
        <p
          class="my-4"
          v-for="(item, i) in statusListItems"
          :key="i"

        >
          {{item.title.toUpperCase()}}: <span :class="`aqa-color--${item.title.toUpperCase()}`">{{item.value}}</span>
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

<script>
import ReportsPieChartComponent from "@/components/reports/reportsPieChartComponent.vue";
import {color} from "@/components/common/collorList";

export default {
  name: "aqaReportStatisticTestComponent",
  components: {ReportsPieChartComponent},
  props:{
    statusList: Object
  },
  data(){
    return{
      statusListItems: [],
      dataChart: undefined
    }
  },
  updated() {
    this.draw()
  },
  mounted() {
    this.draw()

  },
  methods:{
    draw(){
      this.dataChart = {
        labelList: [],
        colorList: [],
        dataList: []
      }
      this.statusListItems = [];
      for(const elem of Object.keys(this.statusList)){
        this.statusListItems.push({title: elem, value:this.statusList[elem]})
        this.dataChart.labelList.push(elem)
        this.dataChart.colorList.push(color[elem ? elem.toLowerCase() : 'null'])
        this.dataChart.dataList.push(this.statusList[elem])
      }
    }
  }
}
</script>

<style scoped>

</style>
