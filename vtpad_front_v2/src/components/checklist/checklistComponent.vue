<template>
  <div v-if="loader">
    <v-progress-linear
      color="primary"
      indeterminate
    ></v-progress-linear>
  </div>

  <v-card>
    <checklist-list-filter-component
      :space-id="spaceId"
      @newChecklistEmit="newChecklist"
      @searchChecklistEmit="changeQParam"
      :show-create="true"
    />

  </v-card>

    <div v-if="!loader">
      <checklist-list-component
        :item="items"
        @deleteChecklistEmit="deleteChecklist"
        @updateChecklistEmit="updateChecklist"
        @newChecklistEmits="newChecklist"
      />
    </div>

</template>

<script>
import ChecklistListFilterComponent from "@/components/checklist/list/checklistListFilterComponent.vue";
import ChecklistListComponent from "@/components/checklist/list/checklistListComponent.vue";
import axios from "axios";

export default {
  name: "checklistComponent",
  components: {ChecklistListComponent, ChecklistListFilterComponent},
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
    this.getChecklist();
  },
  methods:{
    getChecklist(){
      axios.get(`/api/v1/checklist/list/${this.spaceId}`, {params: this.params}).then(res => {
        this.items = res.data;
        this.loader = false;
      })
    },
    changeQParam(qParam){
      this.params.q = qParam ?? '';
      this.getChecklist();
    },
    newChecklist(checklist){
      this.items.unshift(checklist)
    },
    deleteChecklist(checklistId){
      const tmp = this.items.findIndex(value => value.id === checklistId)
      this.items.splice(tmp, 1)
    },
    updateChecklist(checklist){
      this.items.find(value => value.id === checklist.id).title = checklist.title
    }
  }
}
</script>

<style scoped>

</style>
