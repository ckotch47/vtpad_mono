<template>
  <aqa-report-suite-card-title-component :suite-item="suiteItem"/>

  <v-expansion-panels class="">
    <v-expansion-panel :title="'Detail'" @click="showSuiteTable">
      <v-expansion-panel-text>
        <aqa-report-suite-table-component @showModalMessageSuiteEmit="$emit('showModalMessageSuiteEmit', $event)" :suite-items="itemsDetail" v-if="itemsDetail"/>
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script>

import AqaReportSuiteCardTitleComponent
  from "@/components/reports/aqa-report/aqaReportSuite/aqaReportSuiteCardTitleComponent.vue";
import AqaReportSuiteTableComponent
  from "@/components/reports/aqa-report/aqaReportSuite/aqaReportSuiteTableComponent.vue";
import { reportService } from '@/services'

export default {
  name: "aqaReportSuiteCardComponent",
  components: {AqaReportSuiteTableComponent, AqaReportSuiteCardTitleComponent},
  emits: ['showModalMessageSuiteEmit'],
  props:{
    suiteItem: Object
  },
  data(){
    return{
      itemsDetail: undefined,
      spaceId: this.$route?.params.id
    }
  },
  methods:{
    showSuiteTable(){
      if(!this.itemsDetail)
      reportService.getSuiteDetail(this.spaceId, this.suiteItem.id).then(res => {
        this.itemsDetail = res.data
      })

    }
  }
}
</script>

<style scoped>

</style>
