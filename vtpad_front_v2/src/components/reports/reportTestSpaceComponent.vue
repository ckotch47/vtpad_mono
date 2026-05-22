<template>
  <aqa-report-select-component :test-list="testList" @selectTestLstEmit="selectTestByList"/>

  <aqa-report-statistic-test-component
    v-if="testDetail?.statistic && testId"
    :status-list="testDetail.statistic"/>

  <aqa-report-suite-main-component v-if="testId" :list-suite="suiteList"/>
</template>

<script>
import AqaReportSelectComponent from "@/components/reports/aqa-report/aqaReportSelectComponent.vue";
import AqaReportStatisticTestComponent from "@/components/reports/aqa-report/aqaReportStatisticTestComponent.vue";
import AqaReportSuiteMainComponent
  from "@/components/reports/aqa-report/aqaReportSuite/aqaReportSuiteMainComponent.vue";
import axios from "axios";

export default {
  name: "reportAqaSpaceComponent",
  components: {AqaReportSuiteMainComponent, AqaReportStatisticTestComponent, AqaReportSelectComponent},
  data(){
    return{
      testList: [],
      suiteList: [],
      testId: undefined,
      spaceId: this.$route.params.spaceId,
      testDetail: undefined,
    }
  },
  mounted() {
    this.getTestList()
  },
  methods:{
    getTestList(){
      axios.get(`/api/v2/report/${this.spaceId}/test/list`).then(res => {
        this.testList = res.data
      })
    },
    getTestDetail(){
      if(!this.testId) return
      axios.get(`/api/v2/report/${this.spaceId}/test/${this.testId}/detail`).then(res => {
        this.testDetail = res.data
      })
    },
    getSuiteList(){
      axios.get(`/api/v2/report/${this.spaceId}/test/${this.testId}/suite/list`).then(res => {
        this.suiteList = res.data;
      })
    },
    selectTestByList(testId){
      this.testId = testId;
      this.getTestDetail();
      this.getSuiteList();
    },

  },

}
</script>

<style lang="scss">
.aqa-color{
  &--PASSED{
    color: #41b883;
  }
  &--SKIPPED{
    color: #e6bb00;
  }
  &--FAILED{
    color: #e6003a;
  }
  &--UNKNOWN{
    color: #363636;
  }
}
</style>
