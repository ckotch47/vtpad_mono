<template>
  <report-qa-filter-component @selectFilterEmit="selectFilter" :statistic="listItems.count"/>
  <report-qa-list-component :title="'Created'" :data-list="listItems.opened" />
  <report-qa-list-component :title="'Updated'" :data-list="listItems.updated"/>
</template>

<script>
import ReportQaFilterComponent from "@/components/reports/qa-report/reportQaFilterComponent.vue";
import ReportQaListComponent from "@/components/reports/qa-report/reportQaListComponent.vue";
import { qaReportService } from '@/services'

export default {
  name: "reportQaSpaceComponent",
  components: {ReportQaListComponent, ReportQaFilterComponent},
  data(){
    return{
      listItems: {
        count: undefined,
        opened: [],
        updated: []
      }
    }
  },
  methods:{
    selectFilter(data){
      qaReportService.getBugList(data).then(res => {
        this.listItems = res.data
      })
    }
  }
}
</script>

<style scoped>

</style>
