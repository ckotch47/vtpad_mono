<template>
  <div class="d-flex py-8">
    <case-list-right-component :items="item" @openCaseEmit="openCase"/>
    <case-list-left-component
      @deleteTestCaseEmit="deleteTestCase"
      @updateTestCaseEmits="updateTestCases"
      @newTestCaseEmits="newTestCases"
      :case-id="openCaseId"/>
  </div>
</template>

<script>
import CaseListRightComponent from "@/components/cases/list/caseListRightComponent.vue";
import CaseListLeftComponent from "@/components/cases/list/caseListLeftComponent.vue";

export default {
  name: "caseListComponent",
  components: {CaseListLeftComponent, CaseListRightComponent},
  emits: ['deleteTestCaseEmit', 'updateTestCaseEmit', 'newTestCasesEmit'],
  props:{
    item: Array
  },
  data(){
    return{
      openCaseId: undefined
    }
  },
  methods:{
    openCase(caseId){
      this.openCaseId = caseId;
    },
    deleteTestCase(caseId){
      this.$emit('deleteTestCaseEmit', caseId)
    },
    updateTestCases(cases){
      this.$emit('updateTestCaseEmit', cases)
    },
    newTestCases(cases){
      this.$emit('newTestCasesEmit', cases)
    }
  }
}
</script>

<style scoped>

</style>
