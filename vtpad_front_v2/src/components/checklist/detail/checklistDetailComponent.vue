<template>
  <div v-if="loader">
    <v-progress-linear
      color="primary"
      indeterminate
    ></v-progress-linear>
  </div>

  <div style="" :style="styleObject ?? {'max-width': '732px', 'margin': '0 auto'}" v-if="!loader">

    <checklist-list-right-component :checklist-id="checklistId" read-only  v-if="checklistId"/>
  </div>
</template>

<script>
import ChecklistListRightComponent from "@/components/checklist/list/checklistListRightComponent.vue";
import axios from "axios";

export default {
  name: "checklistDetailComponent",
  components: {ChecklistListRightComponent},
  props: {
    shortName: String,
    styleObject: Object
  },
  data(){
    return{
      loader: true,
      checklistId: undefined
    }
  },
  mounted() {
    this.getChecklistIdByShortName()
  },
  methods:{
    getChecklistIdByShortName(){
      if(!this.shortName) return
      axios.get(`/api/v1/checklist/by-short/${this.shortName}`).then(res => {
        if(res.data){
          this.checklistId = res.data.id;
          this.loader = false
        }
      })
    }
  }
}
</script>

<style scoped>

</style>
