<template>
  <div class="d-flex py-8">
    <checklist-list-left-component :items="item" @openChecklistEmit="openChecklist"/>
    <checklist-list-right-component
      :checklist-id="openChecklistId"
      @deleteChecklistEmit="deleteChecklist"
      @updateChecklistEmits="updateChecklist"
      @newChecklistEmits="newChecklist"
      @closeChecklistEmits="closeChecklist"
    />
  </div>
</template>

<script>
import ChecklistListLeftComponent from "@/components/checklist/list/checklistListLeftComponent.vue";
import ChecklistListRightComponent from "@/components/checklist/list/checklistListRightComponent.vue";

export default {
  name: "checklistListComponent",
  components: {ChecklistListRightComponent, ChecklistListLeftComponent},
  emits: ['deleteChecklistEmit', 'updateChecklistEmit', 'newChecklistEmits'],
  props:{
    item: Array
  },
  data(){
    return{
      openChecklistId: undefined
    }
  },
  methods:{
    closeChecklist(){
      this.openChecklistId = undefined
    },
    openChecklist(checklistId){
      this.openChecklistId = checklistId;
    },
    deleteChecklist(checklistId){
      this.$emit('deleteChecklistEmit', checklistId)
    },
    updateChecklist(checklist){
      this.$emit('updateChecklistEmit', checklist)
    },
    newChecklist(checklist){
      this.$emit('newChecklistEmits', checklist)
    }
  }
}
</script>

<style scoped>

</style>
