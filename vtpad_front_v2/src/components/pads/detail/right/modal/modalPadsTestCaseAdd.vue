<template>
  <v-dialog
    width="auto"
    :model-value="isActive"
    min-width="800"
    min-height="400"
    max-width="900"
    @update:modelValue="$emit('closeModalTestCaseAddPadEmit')"
  >
    <v-card>
      <case-list-filter-component
        :space-id="spaceId"
        @searchCaseEmit="changeCaseQParam"
      />
      <div class="pa-4">
        <case-list-right-component :items="items" @open-case-emit="clickOnTestCase"/>
      </div>
    </v-card>
  </v-dialog>
</template>

<script>

import CaseListFilterComponent from "@/components/cases/list/caseListFilterComponent.vue";
import axios from "axios";
import CaseListRightComponent from "@/components/cases/list/caseListRightComponent.vue";

export default {
  name: "modalPadsTestCaseAdd",
  components: {CaseListRightComponent, CaseListFilterComponent},
  emits: ['closeModalTestCaseAddPadEmit', 'clickOnTestCaseEmit'],
  props: {
    isActive: Boolean,
    edit: Boolean
  },
  data(){
    return{
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
    if(this.edit)
    this.getCaseList();
  },
  methods:{
    getCaseList(){
      axios.get(`/api/v1/testcases/${this.spaceId}`, {params: this.params}).then(res => {
        this.items = res.data
      })
    },
    changeCaseQParam(qParam){
      this.params.q = qParam ?? '';
      this.getCaseList()
    },
    clickOnTestCase(testCaseId, testCase){
      this.$emit('clickOnTestCaseEmit', testCaseId, testCase)
    },
  }
}
</script>

<style scoped>

</style>
