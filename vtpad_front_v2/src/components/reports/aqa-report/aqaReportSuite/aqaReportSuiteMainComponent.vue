<template>
  <v-card class="suites-card my-8" v-for="item in listSuite" :key="item.id">
    <v-card-item>
      <aqa-report-suite-card-component @showModalMessageSuiteEmit="showAqaErrorMessageModal" :suite-item="item"/>
    </v-card-item>
  </v-card>

  <v-dialog max-width="1500px" v-model="isActiveAqaError" @close="isActiveAqaError = false">
    <v-card>
      <v-toolbar title="Error">
        <v-btn text="Close" @click="isActiveAqaError = false"/>
      </v-toolbar>

      <div class="pa-8">
        {{message}}
      </div>
    </v-card>
  </v-dialog>
</template>

<script>

import AqaReportSuiteCardComponent
  from "@/components/reports/aqa-report/aqaReportSuite/aqaReportSuiteCardComponent.vue";

export default {
  name: "aqaReportSuiteMainComponent",
  components: {AqaReportSuiteCardComponent},
  props:{
    listSuite: Array,
  },
  data(){
    return{
      isActiveAqaError: false,
      message: undefined
    }
  },
  mounted() {
  },
  methods:{
    showAqaErrorMessageModal(event){
      this.message = event
      this.isActiveAqaError = true
    }
  }
}
</script>

<style scoped lang="scss">
.suites-card{
  .v-card-item{
    padding: 0;
  }
}
</style>
