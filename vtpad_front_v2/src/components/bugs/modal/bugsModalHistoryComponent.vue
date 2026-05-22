<template>
  <v-container class="comments" style="min-height: 300px; max-height: 300px; overflow-y: auto">
    <v-checkbox label="Show history" v-model="showHistory"> </v-checkbox>

    <v-timeline
      density="compact"
      side="end"
    >

      <v-timeline-item
        v-for="event in events"
        :key="event.id"
        :dot-color="getColor(event.view)"
        size="small"
      >
        <bugs-modal-comment-history-elem
          v-if="event.view === 'history'"
          :comment="event"
        />
        <bugs-modal-comment-comment-elem
          v-else-if="event.view === 'comment'"
          :comment="event"
          @editComment="editComment"
        />
      </v-timeline-item>

    </v-timeline>
  </v-container>
</template>

<script>
import BugsModalCommentHistoryElem from "@/components/bugs/modal/comment/bugsModalCommentHistoryElem.vue";
import BugsModalCommentCommentElem from "@/components/bugs/modal/comment/bugsModalCommentCommentElem.vue";

export default {
  name: "bugsModalHistoryComponent",
  components: {BugsModalCommentCommentElem, BugsModalCommentHistoryElem},
  emits: ['editComment'],
  props:{
    bug: Object,
    history: Object
  },
  data: () => ({
    events: [],
    input: null,
    nonce: 0,
    showHistory: false
  }),
  mounted() {
    this.showHistory = false
    this.events = this.history.filter(value => value.view === 'comment')
  },
  updated() {
    this.showHistory = false
    this.events = this.history.filter(value => value.view === 'comment')
  },
  watch:{
    showHistory:{
      handler(newValue) {
        if(!newValue){
          this.events = this.events.filter(value => value.view === 'comment')
        }else{
          this.events = this.history
        }
      },
      deep: true
    }
  },
  methods: {
    comment () {


    },
    editComment(comment){
      this.$emit('editComment', comment)
    },
    getColor(eventView){
      switch (eventView){
        case 'history':
          return 'grey'
        default:
          return 'primary'
      }
    }
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
