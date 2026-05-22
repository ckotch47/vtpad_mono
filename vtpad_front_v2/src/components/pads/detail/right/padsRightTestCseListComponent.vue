<template>
  <v-expansion-panels v-model="openPanels">
    <v-expansion-panel >
      <v-expansion-panel-title>
        <div class="d-flex justify-space-between align-center w-100">
          <p>Test cases:</p>
          <!--          <v-btn :icon="'mdi-plus'" variant="text" ></v-btn>-->
        </div>
      </v-expansion-panel-title>
      <v-expansion-panel-text class="no-padding-important">
        <v-list>
          <v-list-item
            v-for="item in testCases"
            :key="item.id"
            :title="item.short_name"
            :value="item.id"
            @click="openTestCase(item)"
            />
<!--          <v-list-item :title="'VT-3T'" @click="showModalDetail = !showModalDetail"/>-->
<!--          <v-list-item :title="'VT-2T'" @click="showModalDetail = !showModalDetail"/>-->
<!--          <v-list-item :title="'VT-1T'" @click="showModalDetail = !showModalDetail"/>-->

          <v-list-item
            v-if="edit && itemId"
            :title="'Edit…'"
            class="text-primary"
            @click="showModal = !showModal"
          />
        </v-list>
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>

  <modal-pads-test-case-add
    :is-active="showModal"
    :edit="edit"
    @click-on-test-case-emit="addRemoveTestCase"
    @closeModalTestCaseAddPadEmit="showModal = !showModal"/>
  <modal-pads-test-case-show-component
    :item="openedTestCase"
    :is-active="showModalDetail"
    @closeModalTestCaseShowPadEmit="showModalDetail = !showModalDetail"/>
</template>

<script>
import ModalPadsTestCaseAdd from "@/components/pads/detail/right/modal/modalPadsTestCaseAdd.vue";
import ModalPadsTestCaseShowComponent from "@/components/pads/detail/right/modal/modalPadsTestCaseShowComponent.vue";
import axios from "axios";

export default {
  name: "padsRightTestCseListComponent",
  components: {ModalPadsTestCaseShowComponent, ModalPadsTestCaseAdd},
  emits: ['AddTestCaseFromPadEmit', 'OpenTestCaseFromPadEmit'],
  props: {
    edit: Boolean,
    itemId: String
  },
  watch: {
    itemId(){
      this.getTestCaseForItem()
    }
  },
  data: () => ({
    showModal: false,
    showModalDetail: false,
    testCases: [],
    openedTestCase: undefined,
    openPanels: [1]
  }),

  methods: {
    getTestCaseForItem(){
      if(!this.itemId) return
      axios.get(`/api/v2/items/testcase/${this.itemId}`).then(value => {
        this.testCases = value.data
        this.openPanels = [0]
      })
    },
    openTestCase(item){
      this.openedTestCase = item
      this.showModalDetail = !this.showModalDetail
    },
    addRemoveTestCase(testCaseId, testCase){
      if(this.testCases.find(value => value.id === testCaseId)){
        this.removeTestCase(testCaseId)
      }
      else {
        this.addTestCase(testCaseId, testCase)
      }
    },
    addTestCase(testCaseId, testCase){
      axios.post(`/api/v2/items/add/testcase/${this.itemId}?testcase_id=${testCaseId}`).then(value => {
        this.testCases.push(testCase)
      })
    },
    removeTestCase(testCaseId){
      axios.delete(`/api/b2/items/testcase/${this.itemId}?testcase_id=${testCaseId}`).then(value => {
        const index = this.testCases.findIndex(value1 => value1.id === testCaseId)
        this.testCases.splice(index, 1)
        console.log(value)
      })
    }
  }
}
</script>

<style scoped>

</style>
