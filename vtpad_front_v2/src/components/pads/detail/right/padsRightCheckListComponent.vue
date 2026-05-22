<template>
  <v-expansion-panels v-model="openPanels">
    <v-expansion-panel >
      <v-expansion-panel-title>
        <div class="d-flex justify-space-between align-center w-100">
          <p>Check list:</p>
        </div>
      </v-expansion-panel-title>
      <v-expansion-panel-text class="no-padding-important">
        <v-list>
          <v-list-item
            v-for="item in checklists"
            :key="item.id"
            :title="item.short_name"
            :value="item.id"
            @click="openChecklist(item)"
            />
<!--          <v-list-item :title="'VT-32C'" value="1c" @click="showModalDetail = !showModalDetail"/>-->
<!--          <v-list-item :title="'VT-26C'" value="2c" @click="showModalDetail = !showModalDetail"/>-->
<!--          <v-list-item :title="'VT-1123C'" value="3c" @click="showModalDetail = !showModalDetail"/>-->
          <v-list-item

            v-if="edit && itemId"
            :title="'Edit…'"
            class="text-primary"
            @click="showModal = !showModal"/>
        </v-list>
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>

  <modal-pads-check-list-add-component
    :is-active="showModal"
    :edit="edit"
    @click-on-checklist-emit="addRemoveChecklist"
    @closeModalCheckListAddPadEmit="showModal = !showModal"
  />

  <modal-pads-check-list-show-component :item="openedChecklist" :is-active="showModalDetail" @closeModalCheckListShowPadEmit="showModalDetail = !showModalDetail" />
</template>

<script>
import ModalPadsCheckListAddComponent from "@/components/pads/detail/right/modal/modalPadsCheckListAddComponent.vue";
import ModalPadsCheckListShowComponent from "@/components/pads/detail/right/modal/modalPadsCheckListShowComponent.vue";
import axios from "axios";

export default {
  name: "padsRightCheckListComponent",
  components: {ModalPadsCheckListShowComponent, ModalPadsCheckListAddComponent},
  emits: ['AddChecklistFromPadEmit', 'OpenChecklistFromPadEmit'],
  props: {
    edit: Boolean,
    itemId: String
  },
  watch: {
    itemId(){
      this.getCheckListForItem()
    }
  },
  data: ()=> ({
    showModal: false,
    showModalDetail: false,
    checklists: [],
    openedChecklist: undefined,
    openPanels: [1]
  }),
  mounted() {

  },
  methods: {
    getCheckListForItem(){
      if(!this.itemId) return
      axios.get(`/api/v2/items/checklist/${this.itemId}`).then(value => {
        this.checklists = value.data

        this.openPanels = [0]
      })
    },
    openChecklist(item){
      this.openedChecklist = item;
      this.showModalDetail = !this.showModalDetail
    },
    addRemoveChecklist(checkListId, item){
      if(this.checklists.find(value => value.id === checkListId)) {
        this.removeChecklist(checkListId)
      }
      else{
        this.addChecklist(checkListId, item)
      }
    },
    addChecklist(checkListId, item){
      axios.post(`/api/v2/items/add/checklist/${this.itemId}?checklist_id=${checkListId}`).then(value => {
        this.checklists.push(item)
      })
    },
    removeChecklist(checkListId){
      axios.delete(`/api/v2/items/remove/checklist/${this.itemId}?checklist_id=${checkListId}`).then(value => {
        const index = this.checklists.findIndex(value1 => value1.id === checkListId)
        this.checklists.splice(index, 1);
        console.log(value)
      })
    },
  },
}
</script>

<style scoped>

</style>
