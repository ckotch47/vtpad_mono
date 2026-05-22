<template>
  <div v-if="loader">
    <v-progress-linear
      color="primary"
      indeterminate
    ></v-progress-linear>
  </div>


    <v-card>
      <case-list-filter-component
        :show-create="true"
        :space-id="spaceId"
        @newTestCaseEmit="newCase"
        @searchCaseEmit="changeCaseQParam"
      />
    </v-card>
  <div v-if="!loader">
    <case-list-component
      @deleteTestCaseEmit="deleteTestCaseFromList"
      @updateTestCaseEmit="updateTestCase"
      @newTestCasesEmit="newCase"
      :item="items"
    />
  </div>
</template>

<script>
import CaseListFilterComponent from "@/components/cases/list/caseListFilterComponent.vue";
import CaseListComponent from "@/components/cases/list/caseListComponent.vue";
import axios from "axios";

export default {
  name: "casesComponent",
  components: {CaseListComponent, CaseListFilterComponent},
  data(){
    return{
      loader: true,
      items: [],
      spaceId: this.$route.params.spaceId,
      params: {
        q: '',
        sort: 'DESC',
        limit: undefined,
        offset: undefined
      }
    }
  },
  mounted() {
    this.getCaseList()
  },
  methods:{
    getCaseList(){
      axios.get(`/api/v1/testcases/${this.spaceId}`, {params: this.params}).then(res => {
        this.items = res.data
        this.loader = false
      })
    },
    changeCaseQParam(qParam){
      this.params.q = qParam ?? '';
      this.getCaseList()
    },
    newCase(cases){
      this.items.unshift(cases)
    },
    deleteTestCaseFromList(caseId){
      const tmp = this.items.findIndex(value => value.id === caseId)
      this.items.splice(tmp, 1)
    },
    updateTestCase(cases){
      this.items.find(value => value.id === cases.id).title = cases.title
    }
  }
}
</script>

<style scoped>

</style>
