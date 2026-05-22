<template>
  <div v-if="loader">
    <v-progress-linear
      color="primary"
      indeterminate
    ></v-progress-linear>
  </div>

  <runs-list-filter-component :select-item="filters" @changeFilterEmit="changeFilter"/>

  <v-card
    v-for="(pad, i) in runs.pad"
    :key="i"
    :class="pad.run.length > 0 ? 'my-8' : ''"
    :style="pad.run.length === 0 ? 'display: none' : ''"
  >
    <runs-list-item-pad-component v-if="pad.run.length > 0" :pad="pad"/>
  </v-card>
</template>

<script>

import RunsListItemPadComponent from "@/components/runs/list/runsListItemPadComponent.vue";
import RunsListFilterComponent from "@/components/runs/list/runsListFilterComponent.vue";
import axios from "axios";

export default {
  name: "runsListComponent",
  components: {RunsListFilterComponent, RunsListItemPadComponent},
  data(){
    return{
      loader: true,
      spaceId: this.$route.params.spaceId,
      runs: {},
      filters: undefined,
      filterParam:{
        pad_id: undefined,
        skip: 0,
        limit:5
      }
    }
  },
  mounted() {
    this.getFilters();
    this.getRuns();
  },
  methods:{
    getRuns(){
      this.loader = true
      axios.get(`/api/v2/runs/last/${this.spaceId}`).then(res => {
        this.runs = res.data
        this.loader = false
      })
    },
    getFilters(){
      axios.get(`/api/v1/runs/filter/${this.spaceId}`).then(res => {
        this.filters = res.data
      })
    },
    changeFilter(padId, count){
      this.loader = true
      if(!padId) return;
      if(padId === this.filterParam.pad_id) return;
      this.filterParam.pad_id = padId;
      console.log(padId, this.filterParam.pad_id)
      this.filterParam.limit = count;
      axios.get(`/api/v1/runs/by-filter/${this.spaceId}`, {params: this.filterParam}).then(res => {
        this.runs = {
          pad: [{
            "pad_name": "",
            "run": res.data
          },]
        }

        this.loader = false
      })
    }
  }
}
</script>

<style scoped>

</style>
