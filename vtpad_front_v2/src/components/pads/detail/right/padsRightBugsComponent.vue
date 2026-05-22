<template>
  <v-expansion-panels>
    <v-expansion-panel >
      <v-expansion-panel-title>
        <div class="d-flex justify-space-between align-center w-100">
          <p>Bugs:</p>
          <!--          <v-btn :icon="'mdi-plus'" variant="text" ></v-btn>-->
        </div>
      </v-expansion-panel-title>
      <v-expansion-panel-text class="no-padding-important">
        <v-list>
          <v-list-item :title="'VT-404'" @click="$emit('clickShowBugsFromPadEmit')"/>
          <v-list-item
            v-if="edit"
            :title="'Add…'"
            class="text-primary"
            @click="createBug"

          />
        </v-list>
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>

  <bugs-modal-component
    v-if="dialog"
    :is-active="dialog"
    :bug-item="openBugItem"
    :filters="filter"
    @close-bug-modal="closeBugModal()"
  />

</template>

<script>
import axios from "axios";
import BugsModalComponent from "@/components/bugs/modal/bugsModalComponent.vue";

export default {
  name: "padsRightBugsComponent",
  components: {BugsModalComponent},
  emits: ['addBugsFroPadEmit', 'clickShowBugsFromPadEmit'],
  props: {
    edit: Boolean
  },
  data: () => ({
    spaceId: undefined,
    dialog: false,
    openBugItem: undefined,
    filter: undefined
  }),
  mounted() {
    this.spaceId = this.$route.params.spaceId
    this.getFilter().then()
  },
  methods: {
    async getFilter(){
      axios.get('/api/v1/bugs/filters?space_id='+this.spaceId).then(res => {
        this.filter = res.data;
        for(const item of this.filter.user){
          item.title = item.username
        }
      })
    },
    createBug(){
      axios.post(`/api/v1/bugs`, {
        space_id: this.spaceId,
        state: 'OPEN',
        title: ''
      }).then(res => {

        this.openBug(res.data)
      })
    },
    openBug(bugItem){
      this.dialog = !this.dialog;
      this.openBugItem = bugItem;
      this.store.openBug = bugItem;
    },
    closeBugModal(){

      this.dialog = false;
      this.openBugItem = undefined
      this.store.openBug = undefined;
    },
  }
}
</script>

<style scoped>

</style>
