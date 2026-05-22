<template>
  <div v-if="loader">
    <v-progress-linear
      color="primary"
      indeterminate
    ></v-progress-linear>
  </div>

  <div style="" :style="styleObject ?? {'max-width': '732px', 'margin': '0 auto'}" v-if="!loader">
    <case-list-left-component :case-id="caseId" read-only v-if="caseId"/>
  </div>
</template>

<script>
import CaseListLeftComponent from "@/components/cases/list/caseListLeftComponent.vue";
import axios from "axios";

export default {
  name: "casesDetailComponent",
  props: {
    shortName: String,
    styleObject: Object
  },
  components: {CaseListLeftComponent},
  data(){
    return{
      loader: true,
      caseId: undefined
    }
  },
  mounted() {
    this.getByShortName()
  },
  methods:{
    getByShortName(){
      if(!this.shortName) return;
      axios.get(`/api/v1/testcases/shortname/${this.shortName}`).then(res => {
        if(res.data){
          this.caseId = res.data.id
         this.loader = false
        }
      })
    }
  }
}
</script>

<style scoped>

</style>
