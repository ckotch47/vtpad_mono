<template>
  <v-alert>
    <div class="d-flex justify-space-between flex-grow-1">
      <div>
        {{ comment.create_user.username }}<br>
        <div v-if="comment.view === 'comment'" v-html="sanitizedText" />
      </div>
      <div class="flex-shrink-0">
        <v-icon icon="mdi-pencil" size="14" @click="editComment" />
        {{ comment.create_date ? comment.create_date.split('T')[0] : '' }}
      </div>
    </div>
  </v-alert>
</template>

<script setup>
import { computed } from 'vue'
import { sanitizeHtml } from '@/utils/sanitize'

const props = defineProps({
  username: String,
  text: String,
  date: String,
  comment: Object
})

const emit = defineEmits(['editComment'])

const sanitizedText = computed(() => sanitizeHtml(props.comment?.text))

function editComment() {
  emit('editComment', props.comment)
}
</script>
