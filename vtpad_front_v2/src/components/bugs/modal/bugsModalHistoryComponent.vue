<template>
  <v-container class="comments" style="min-height: 300px; max-height: 300px; overflow-y: auto">
    <v-checkbox v-model="showHistory" label="Show history" />

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
  </v-container>
</template>

<script setup>
import { ref, watch } from 'vue'
import BugsModalCommentHistoryElem from '@/components/bugs/modal/comment/bugsModalCommentHistoryElem.vue'
import BugsModalCommentCommentElem from '@/components/bugs/modal/comment/bugsModalCommentCommentElem.vue'

const props = defineProps({
  bug: Object,
  history: Object
})

const emit = defineEmits(['editComment'])

const events = ref([])
const showHistory = ref(false)

watch(showHistory, (newValue) => {
  if (!newValue) {
    events.value = events.value.filter(value => value.view === 'comment')
  } else {
    events.value = props.history
  }
}, { deep: true })

watch(() => props.history, (val) => {
  showHistory.value = false
  events.value = val.filter(value => value.view === 'comment')
}, { immediate: true, deep: true })

function editComment(comment) {
  emit('editComment', comment)
}

function getColor(eventView) {
  switch (eventView) {
    case 'history':
      return 'grey'
    default:
      return 'primary'
  }
}
</script>

<style lang="scss">
.comments {
  .v-checkbox .v-selection-control {
    min-height: unset !important;
  }
  padding-top: 0;
  padding-bottom: 0;
  button {
    background: unset !important;
  }
}
</style>
