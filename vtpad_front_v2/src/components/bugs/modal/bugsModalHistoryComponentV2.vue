<template>
  <v-container class="comments" style=" max-height: 600px; overflow-y: auto">
    <v-tabs

      color="primary"
      v-model="historyTabValue"
      class="rounded-0_custom"
    >
      <v-tab text="comment" :value="0" />
      <v-tab text="history" :value="1" />
    </v-tabs>



    <v-tabs-window v-model="historyTabValue">
      <v-tabs-window-item value="0">
        <bugs-modal-history-list-component
          :events="history.filter(value => value.view === 'comment')"
          @editComment="editComment"
        />
      </v-tabs-window-item>


    <v-tabs-window-item value="1">
      <bugs-modal-history-list-component
        :events="history"
        @editComment="editComment"
      />
    </v-tabs-window-item>


    </v-tabs-window>
  </v-container>
</template>

<script>

import BugsModalHistoryListComponent from "@/components/bugs/modal/history/bugsModalHistoryListComponent.vue";

export default {
  name: "bugsModalHistoryComponentV2",
  components: {BugsModalHistoryListComponent},
  emits: ['editComment'],
  props:{
    bug: Object,
    history: Array
  },
  data: () => ({
    historyTabValue: null,
    events: [],
    input: null,
    nonce: 0,
    showHistory: false
  }),
  mounted() {
    // this.events = this.history.filter(value => value.view === 'comment')
  },
  updated() {
    // this.showHistory = false
    // this.events = this.history.filter(value => value.view === 'comment')
  },

  methods: {
    editComment(comment){
      this.$emit('editComment', comment)
    },
  },
}
</script>

<style  lang="scss">
.comments {
  .v-checkbox .v-selection-control {
    min-height: unset !important;
  }
  padding-top: 0;
  padding-bottom: 0;
  button{
    background: unset !important;
  }
}
</style>
