<template>
  <v-timeline density="compact" side="end">

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
</template>

<script>
import BugsModalCommentHistoryElem from "@/components/bugs/modal/comment/bugsModalCommentHistoryElem.vue";
import BugsModalCommentCommentElem from "@/components/bugs/modal/comment/bugsModalCommentCommentElem.vue";

export default {
  name: "bugsModalHistoryListComponent",
  components: {BugsModalCommentCommentElem, BugsModalCommentHistoryElem},
  emits: ['editComment'],
  props:{
    events: Array
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

<style scoped>

</style>
