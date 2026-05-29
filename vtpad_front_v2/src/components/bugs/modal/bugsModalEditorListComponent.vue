<template>
  <editor-component
    ref="editorBugTextRef"
    class="bug-modal--text"
    :edit="true"
    placeHolderEditor="Text…"
    :text="bug.text"
    :show-menu-fixed="true"
    :show-menu-floating="false"
    :show-menu-bubble="false"
    menu-position="top"
    is-save
    max-height="340px"
    @editorSaveFromMenu="updateEditor('text')"
    @focusout="updateEditor('text')"
  />
</template>

<script setup>
import { ref } from 'vue'
import EditorComponent from '@/components/common/editor/editorComponent.vue'
import { bugService } from '@/services'

const props = defineProps({
  bug: Object
})

const emit = defineEmits(['updateBugTextEmit'])

const editorBugTextRef = ref(null)

function updateEditor(name) {
  let value = undefined
  switch (name) {
    case 'text':
      value = editorBugTextRef.value?.$data?.editor?.getHTML()
      break
    case 'steps':
      // value = editorBugTextSteps.value?.$data?.editor?.getHTML()
      break
    case 'additional_link':
      // value = editorBugTextLink.value?.$data?.editor?.getHTML()
      break
  }
  bugService.update(props.bug.id, {
    [name]: value
  }).then(() => {
    emit('updateBugTextEmit')
  })
}
</script>

<style scoped lang="scss">
.bug-modal--text {
  height: 370px;
  margin-bottom: 15px;
}
</style>
