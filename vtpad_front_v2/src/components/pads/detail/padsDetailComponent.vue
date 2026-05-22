<template>
  <div v-if="loader">
    <v-progress-linear
      color="primary"
      indeterminate
    ></v-progress-linear>
  </div>

  <v-text-field
    label="Pad name"
    v-model="pad.name"
    :append-inner-icon="'mdi-content-save'"
    @click:append-inner="savePadName"
    class="pad-name--field"
  />

  <div v-if="!loader ">


    <div class="d-flex">
      <v-list class="w-66">

        <pads-detail-list-item-component v-if="items.length !== 0 && !loader" :items="items" :pad-id="padId"/>
  <!--      <pads-detail-half-component v-if="items.length !== 0 && !loader" :items="items" :pad-id="padId" />-->
        <pads-detail-list-item-new-component v-if="items.length === 0 && !loader" :pad-id="padId" @newItemEmit="newItem"/>
      </v-list>

    <div class="w-33 pl-2" style="padding-left: 16px">
      <div class="position-sticky overflow-y-scroll" style="top: 15px; max-height: 80vh" >
        <pads-detail-half-right-component :is-show-bugs="false" :can-edit="true"/>
      </div>
    </div>
    </div>
  </div>



    <div class="run--btn">
      <pads-detail-runs-list-modal-component
        v-if="isShowRunsListModal"
        @closeModal="isShowRunsListModal = false"
        :is-active="isShowRunsListModal"
        :pad-id="pad.id"
      />
      <pads-detail-short-cut-modal
        v-if="isShowShortcutMpdal"
        @closeModal="isShowShortcutMpdal = false"
        :is-active="isShowShortcutMpdal"
      />

      <v-fab
        color="warning"
        icon="mdi-help"
        class="select-run--btn"
        @click="isShowShortcutMpdal = true"
      />
      <v-fab
        color="primary"
        icon="mdi-menu"
        class="select-run--btn"
        @click="isShowRunsListModal = true"
      />
      <v-fab
        color="info"
        icon="mdi-plus"
        class="new-run--btn"
        @click="newRun"
      />
    </div>

</template>

<script>
import axios from "axios";
import PadsDetailListItemNewComponent from "@/components/pads/detail/padsDetailListItemNewComponent.vue";
import PadsDetailRunsListModalComponent from "@/components/pads/detail/padsDetailRunsListModalComponent.vue";
import PadsDetailShortCutModal from "@/components/pads/detail/padsDetailShortCutModal.vue";
import PadsDetailHalfRightComponent from "@/components/pads/detail/v2/padsDetailHalfRightComponent.vue";
import PadsDetailListItemComponent from "@/components/pads/detail/padsDetailListItemComponent.vue";
import {useAppStore} from "@/stores/app";
export default {

  name: "padsDetailComponent",
  components: {
    PadsDetailListItemComponent,
    PadsDetailHalfRightComponent,
    PadsDetailShortCutModal,
    PadsDetailRunsListModalComponent, PadsDetailListItemNewComponent},
  data(){
    return{
      store: useAppStore(),
      openItem: undefined,
      padId: this.$route.params.padid,
      spaceId: this.$route.params.spaceId,
      isShowRunsListModal: false,
      isShowShortcutMpdal: false,
      items: [],
      pad: {
        "id": "",
        "name": "",
        "spaces_id": "",
        "sort": 0,
        "folder_id": null
      },
      loader: true
    }
  },
  mounted() {
    this.openItem = this.store.openItem
    this.loader = true
    this.getItems()
    this.getPadDetail()
  },
  beforeUnmount() {
    this.store.openItem = undefined
  },
  methods:{
    savePadName(){
      axios.patch(`/api/v1/pad/${this.pad.id}`, {
        name: this.pad.name
      })
    },
    getPadDetail(){
      axios.get(`/api/v1/pad/detail/${this.padId}`).then(res =>{
        this.pad = res.data;

        this.loader = false
      })
    },
    getItems(){
      this.loader = true;
      axios.get(`/api/v2/items/${this.padId}`).then(res => {
        this.items = res.data
        this.loader = false;
      })
    },
    newItem(){
      this.getItems()
    },
    newRun(){
      const date = new Date();
      const name = `${date.getMonth()+1}.${date.getDate()} ${date.getHours()}:${date.getMinutes()}`
      axios.post(`/api/v1/runs/${this.padId}`,{
        name: 'Run - ' + name
      }).then(res => {
        if(res.status === 200){
          location.href = `${location.origin}/space/${this.spaceId}/runs/${res.data.id}`
        }
      })
    }
  }
}
</script>

<style scoped>
.run--btn{
  display: flex;
  flex-direction: column;
  flex-wrap: nowrap;
  position: fixed;
  bottom: 5px;
  right: 60px;
  height: 180px;
  z-index: 9;
}
.pad-name--field{
  padding: 0 0px;
}
</style>
