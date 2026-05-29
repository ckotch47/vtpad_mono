<template>
  <div class="d-flex flex-column">
    <editor-component
      ref="newCommentRef"
      :edit="true"
      placeHolderEditor="Comment…"
      :text="isEdit ? comment.text : ''"
      :show-menu-fixed="true"
      :show-menu-floating="false"
      :show-menu-bubble="false"
      menu-position="top"
      max-height="200px"
      :is-save="true"
      :is-delete="isEdit"
      @editorSaveFromMenu="newComment"
      @editorDeleteFromMenu="deleteComment"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import EditorComponent from '@/components/common/editor/editorComponent.vue'
import { commentService } from '@/services'

const props = defineProps({
  bug: Object,
  edit: Boolean,
  comment: Object
})

const emit = defineEmits(['updateComment', 'newComment'])

const isEdit = ref(false)
const newCommentRef = ref(null)

watch(() => props.edit, (val) => {
  isEdit.value = val
}, { immediate: true })

async function updateComment() {
  await commentService.update(props.comment.id, {
    text: newCommentRef.value?.$data?.editor?.getHTML()
  })
  isEdit.value = false
  emit('newComment')
}

async function deleteComment() {
  await commentService.delete(props.comment.id)
  isEdit.value = false
  emit('newComment')
}

async function newComment() {
  if (isEdit.value) {
    await updateComment()
    return
  }
  if (newCommentRef.value?.$data?.editor?.getHTML() === '<p></p>') return
  await commentService.create(props.bug.id, {
    text: newCommentRef.value?.$data?.editor?.getHTML()
  })
  emit('newComment')
  newCommentRef.value?.$data?.editor?.commands.setContent('<p></p>')
}
</script>

<style lang="scss">
.v-timeline-item__body {
  width: 660px;
}
.send-comment--btn {
  margin: 0 10px 20px 10px;
}
</style>
