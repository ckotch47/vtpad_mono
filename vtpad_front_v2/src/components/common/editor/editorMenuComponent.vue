<template>
  <div class="editor--menu">
    <button
      @click="editor.chain().focus().toggleBold().run()"
      :disabled="!editor.can().chain().focus().toggleBold().run()"
      :class="{ 'is-active': editor.isActive('bold') }"
    >
      <v-icon icon="mdi-format-bold" />
    </button>
    <button
      @click="editor.chain().focus().toggleItalic().run()"
      :disabled="!editor.can().chain().focus().toggleItalic().run()"
      :class="{ 'is-active': editor.isActive('italic') }"
    >
      <v-icon icon="mdi-format-italic" />
    </button>
    <button
      @click="editor.chain().focus().toggleStrike().run()"
      :disabled="!editor.can().chain().focus().toggleStrike().run()"
      :class="{ 'is-active': editor.isActive('strike') }"
    >
      <v-icon icon="mdi-format-strikethrough-variant" />
    </button>
    <button @click="editor.chain().focus().unsetAllMarks().run()">
      <v-icon icon="mdi-format-color-marker-cancel" />
    </button>
    <button @click="editor.chain().focus().clearNodes().run()">
      <v-icon icon="mdi-format-clear" />
    </button>

    <button
      @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
      :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }"
    >
      <v-icon icon="mdi-format-header-2" />
    </button>
    <button
      @click="editor.chain().focus().toggleHeading({ level: 3 }).run()"
      :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }"
    >
      <v-icon icon="mdi-format-header-3" />
    </button>

    <button
      @click="editor.chain().focus().toggleBulletList().run()"
      :class="{ 'is-active': editor.isActive('bulletList') }"
    >
      <v-icon icon="mdi-format-list-bulleted" />
    </button>
    <button
      @click="editor.chain().focus().toggleTaskList().run()"
      :class="{ 'is-active': editor.isActive('taskList') }"
    >
      <v-icon icon="mdi-format-list-checkbox" />
    </button>
    <button @click="refreshCheckList" :class="{ 'is-active': false }">
      <v-icon icon="mdi-refresh" />
    </button>
    <button
      @click="editor.chain().focus().toggleOrderedList().run()"
      :class="{ 'is-active': editor.isActive('orderedList') }"
    >
      <v-icon icon="mdi-order-numeric-ascending" />
    </button>
    <button
      @click="editor.chain().focus().toggleCodeBlock().run()"
      :class="{ 'is-active': editor.isActive('codeBlock') }"
    >
      <v-icon icon="mdi-code-braces" />
    </button>
    <button
      @click="editor.chain().focus().toggleBlockquote().run()"
      :class="{ 'is-active': editor.isActive('blockquote') }"
    >
      <v-icon icon="mdi-format-quote-close" />
    </button>
    <button @click="editor.chain().focus().setHorizontalRule().run()">
      <v-icon icon="mdi-minus" />
    </button>

    <button
      @click="editor.chain().focus().undo().run()"
      :disabled="!editor.can().chain().focus().undo().run()"
    >
      <v-icon icon="mdi-undo" />
    </button>
    <button
      @click="editor.chain().focus().redo().run()"
      :disabled="!editor.can().chain().focus().redo().run()"
    >
      <v-icon icon="mdi-redo" />
    </button>

    <button @click="$emit('editorSaveFromMenu')" v-if="isSave">
      <v-icon icon="mdi-content-save" />
    </button>

    <button @click="$emit('editorDeleteFromMenu')" v-if="isDelete">
      <v-icon icon="mdi-delete" />
    </button>

    <input
      type="file"
      ref="fileInput"
      style="display: none"
      multiple
      accept="image/jpeg, image/png"
      @change="uploadFile"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  editor: { type: Object, default: null },
  isSave: Boolean,
  isDelete: Boolean
})

const emit = defineEmits(['editorSaveFromMenu', 'editorDeleteFromMenu', 'editorUpdateEmit'])

const fileInput = ref(null)

async function openFileUpload() {
  fileInput.value?.click()
}

async function uploadFile() {
  return false
}

function refreshCheckList() {
  const checkboxes = document.querySelectorAll('input[type=checkbox]')
  checkboxes.forEach((elem) => {
    elem.checked = false
  })
  let tmp = props.editor.getHTML()
  tmp = tmp.replaceAll('data-checked="true"', 'data-checked="false"')
  tmp = tmp.replaceAll('checked="checked"', '')
  props.editor.commands.setContent(tmp)
}
</script>

<style lang="scss">
.editor--menu {
  button {
    margin: 0;
    border-width: 0.5px;
    border-radius: 0;
    &.is-active {
      background-color: rgb(var(--v-theme-on-surface-variant));
    }
  }
}
</style>
