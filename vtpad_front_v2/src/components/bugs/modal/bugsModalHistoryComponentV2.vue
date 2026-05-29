<template>
  <v-container class="comments" style="max-height: 600px; overflow-y: auto">
    <v-tabs
      v-model="historyTabValue"
      color="primary"
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

<script setup>
import { ref } from 'vue'
import BugsModalHistoryListComponent from '@/components/bugs/modal/history/bugsModalHistoryListComponent.vue'

defineProps({
  bug: Object,
  history: Array
})

const emit = defineEmits(['editComment'])

const historyTabValue = ref(null)

function editComment(comment) {
  emit('editComment', comment)
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
