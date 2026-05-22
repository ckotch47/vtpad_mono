<template>
  <v-dialog
    width="auto"
    :model-value="isActive"
    min-width="800"
    min-height="400"
    max-width="900"
    @update:modelValue="$emit('closeModalCheckListAddPadEmit')"
  >
    <v-card>
      <checklist-list-filter-component
        :show-create="false"
        :space-id="spaceId"
        @searchChecklistEmit="changeQParam"
      />

      <div class="pa-4">
        <checklist-list-left-component :items="items" @open-checklist-emit="clickOnCheckList"/>
      </div>
    </v-card>
  </v-dialog>
</template>

<script>
import ChecklistListFilterComponent from "@/components/checklist/list/checklistListFilterComponent.vue";
import ChecklistListLeftComponent from "@/components/checklist/list/checklistListLeftComponent.vue";
import axios from "axios";

export default {
  name: "modalPadsCheckListAddComponent",
  components: {ChecklistListLeftComponent, ChecklistListFilterComponent},
  emits: ['closeModalCheckListAddPadEmit', 'clickOnChecklistEmit'],
  props: {
    isActive: Boolean,
    edit: Boolean
  },
  data(){
    return{
      spaceId: this.$route.params.spaceId,
      items: [],
      params: {
        q: null
      }
    }
  },
  mounted() {
    if(this.edit)
    this.getChecklist()
  },
  methods:{
    changeQParam(qParam){
      this.params.q = qParam ?? '';
      this.getChecklist();
    },
    getChecklist(){
      axios.get(`/api/v1/checklist/list/${this.spaceId}`, {params: this.params}).then(res => {
        this.items = res.data;
      })
    },
    clickOnCheckList(itemId, item){
      this.$emit('clickOnChecklistEmit', itemId, item)
    }
  }
}
</script>

<style scoped>

</style>
