<template>
  <h2  contenteditable="true">test pasd</h2>
  <v-card class="run-statistic--fixed">
    <v-card-item>
      <runs-list-linear-bar-component :pass="statistic.passed" :fail="statistic.failed" :all="statistic.allCount"/>
    </v-card-item>
  </v-card>
  <v-divider :thickness="2"></v-divider>

<!--  <div >-->
<!--    <v-list>-->
<!--      <runs-detail-list-item-component :items="items" @changeStateEmit="updateState" :show-state="true"/>-->
<!--    </v-list>-->
<!--  </div>-->

  <div class="d-flex py-4">
    <div class="w-66">
      <v-list>
        <runs-detail-list-item-component :items="items" @changeStateEmit="updateState" />
      </v-list>
    </div>

    <div class="w-33">
      <div class="position-sticky overflow-y-scroll" style="top: 15px; max-height: 80vh" >
        <right-run-detail-state-component @update-state-run-item-emit="updateStateRunItem"/>
        <pads-detail-half-right-component :is-show-bugs="false" :can-edit="false" />
      </div>
    </div>

  </div>
  <div class="re-run--btn">
    <v-fab

      color="primary"
      icon="mdi-autorenew"
      class="new-run--btn"
      @click="rerunRun"
    />
  </div>
</template>

<script>
import axios from "axios";
import RunsDetailListItemComponent from "@/components/runs/detail/runsDetailListItemComponent.vue";
import RunsListLinearBarComponent from "@/components/runs/list/runsListLinearBarComponent.vue";
import PadsDetailHalfRightComponent from "@/components/pads/detail/v2/padsDetailHalfRightComponent.vue";
import RightRunDetailStateComponent from "@/components/runs/detail/right/rightRunDetailStateComponent.vue";
import {useAppStore} from "@/stores/app";
export default {
  name: "runsDetailComponent",
  components: {
    RightRunDetailStateComponent,
    PadsDetailHalfRightComponent, RunsListLinearBarComponent, RunsDetailListItemComponent},
  data(){
    return{
      store: useAppStore(),
      fichaFlagDetailPadItem: false,
      items: [],
      runId: this.$route.params.runid,
      statistic: {
        allCount: 0,
        failed: 0,
        passed: 0
      },
      stateArr: {
        null: 'pass',
        'pass': 'fail',
        'fail': 'skip',
        'skip': 'pass'
      }
    }
  },
  beforeUnmount() {
    this.store.openRunItem = undefined
    this.store.openItem = undefined
  },
  mounted() {
    this.getRun();
  },
  methods:{
    getRun(){
      axios.get(`/api/v1/runs/items/${this.runId}`).then(res => {
        this.items = res.data.items;
        this.statistic = {
          allCount: res.data.allCount,
          failed: res.data.failed,
          passed: res.data.passed
        }
      })
    },
    updateState(value){

      if(value.from === 'fail'){
        this.statistic.failed --;
      }
      if(value.from === 'pass') {
        this.statistic.passed--;
      }

      if(value.to === 'fail') {
        this.statistic.failed++;
      }
      if(value.to === 'pass') {
        this.statistic.passed++;
      }
    },
    updateStateRunItem(newState, oldState, runItemId){
      axios.patch(`/api/v1/runitems/${runItemId}?state=${newState}`).then(res => {
        if(res.status === 200) {
          const tmp = {
            from: oldState,
            to: newState
          }
          this.updateState(tmp)

        }
      });
    },
    rerunRun(){
      axios.post(`/api/v2/runs/${this.runId}/rerun`).then(res => {
        this.getRun()
      })
    }
  }
}
</script>

<style lang="scss">
.run-statistic--fixed{
  /* position: absolute; */
  top: 0;
   z-index: 1000;
  position: sticky;
  margin-bottom: 24px;

}
.re-run--btn{
  display: flex;
  flex-direction: column;
  flex-wrap: nowrap;
  position: fixed;
  bottom: 5px;
  right: 60px;
  height: 120px;
  .v-fab__container{
    bottom: 0;
  }
}
</style>
