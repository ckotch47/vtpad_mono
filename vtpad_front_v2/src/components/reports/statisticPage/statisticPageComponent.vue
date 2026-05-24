<template>
  <div v-if="loader">
    <v-progress-linear
      color="primary"
      indeterminate
    ></v-progress-linear>
  </div>
  <v-card min-height="400" v-if="!loader">
    <v-card-item>
      <div class="d-flex">
        <statistic-page-pad-component :pads-statistic="statisticItem.pads" v-if="statisticItem?.pads"/>
      </div>
    </v-card-item>

    <v-card-item v-if="statisticItem?.runs?.state.length > 0">
      <div class="d-flex justify-space-between">
        <statistic-page-run-component :run-statistic="statisticItem.runs" />
        <reports-pie-chart-component v-if="dataChartRuns" :data-chart="dataChartRuns" />
      </div>
    </v-card-item>

    <v-card-item v-if="statisticItem?.bugs?.state.length > 0">
      <div class="d-flex justify-space-between" >
        <statistic-page-bugs-component :bug-statistic="statisticItem.bugs" />
        <reports-pie-chart-component v-if="dataChartBugs" :data-chart="dataChartBugs" />
      </div>
    </v-card-item>
  </v-card>
</template>

<script>
import StatisticPagePadComponent from "@/components/reports/statisticPage/statisticPagePadComponent.vue";
import StatisticPageRunComponent from "@/components/reports/statisticPage/statisticPageRunComponent.vue";
import StatisticPageBugsComponent from "@/components/reports/statisticPage/statisticPageBugsComponent.vue";
import ReportsPieChartComponent from "@/components/reports/reportsPieChartComponent.vue";
import { spaceService } from '@/services'
import {color} from "@/components/common/collorList";

export default {
  name: "statisticPageComponent",
  components: {
    ReportsPieChartComponent,
    StatisticPageBugsComponent, StatisticPageRunComponent, StatisticPagePadComponent},
  watch:{
    $route: {
      handler() {
        this.loader = true;
        this.spaceId = this.$route.params.spaceId;
        this.statisticItem = undefined;
        this.dataChartRuns = undefined;
        this.dataChartBugs = undefined;
        this.getStatistics()
      },
      deep: false
    },
  },
  data(){
    return{
      loader: true,
      statisticItem: {},
      dataChartRuns: undefined,
      dataChartBugs: undefined,
      spaceId: this.$route.params.spaceId,

    }
  },
  mounted() {
    this.getStatistics();
  },
  methods:{
    getStatistics(){
      spaceService.getStatistic(this.spaceId).then(res => {
        this.statisticItem = res.data;
        this.updateChartsRuns();
        this.updateChartsBugs();
        this.loader = false
      })
    },
    updateChartsRuns(){
      this.dataChartRuns = {
        labelList: [],
        colorList: [],
        dataList: []
      };
      let data = this.statisticItem;
      for(const elem of data.runs.state){
        this.dataChartRuns.labelList.push(elem.state ?? 'null')
        this.dataChartRuns.colorList.push(color[elem.state ? elem.state.toLowerCase() : 'null'])
        this.dataChartRuns.dataList.push(elem.item_count)
      }
    },
    updateChartsBugs(){
      this.dataChartBugs = {
        labelList: [],
        colorList: [],
        dataList: []
      };
      let data = this.statisticItem;
      for(const elem of data.bugs.state){
        this.dataChartBugs.labelList.push(elem.state ?? 'null')
        this.dataChartBugs.colorList.push(color[elem.state ? elem.state.toLowerCase() : 'null'])
        this.dataChartBugs.dataList.push(elem.item_count)
      }
    }
  }
}
</script>

<style scoped>

</style>
