<template>
  <div class="editor-custom_main">
    <div ref="editorCustomRef" class="editor-custom">
      <div v-if="editor && showMenuFixed" class="editor-custom_menu--fixed_top">
        <editor-menu-component
          :editor="editor"
          :is-save="isSave"
          :is-delete="isDelete"
          @editor-save-from-menu="$emit('editorSaveFromMenu')"
          @editor-delete-from-menu="$emit('editorDeleteFromMenu')"
          @editor-update-emit="editorUpdate"
        />
      </div>
      <div
        ref="editorCustomTextRef"
        class="editor-custom_text"
        :style="{ 'max-height': maxHeight ?? '340px', 'min-height': minHeight ?? '100px' }"
      >
        <bubble-menu
          v-if="editor && showMenuBubble"
          :editor="editor"
          :tippy-options="{ duration: 100 }"
        >
          <editor-menu-component :editor="editor" />
        </bubble-menu>

        <floating-menu
          v-if="editor && showMenuFloating"
          :editor="editor"
          :tippy-options="{ duration: 100 }"
          max-with="732px"
        >
          <editor-menu-component :editor="editor" />
        </floating-menu>

        <editor-content :editor="editor" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { Editor, EditorContent, BubbleMenu, FloatingMenu } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import Typography from '@tiptap/extension-typography'
import Image from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import TaskItem from '@tiptap/extension-task-item'
import TaskList from '@tiptap/extension-task-list'
import EditorMenuComponent from '@/components/common/editor/editorMenuComponent.vue'

const props = defineProps({
  text: String,
  edit: Boolean,
  postId: { type: undefined, default: undefined },
  showMenuFixed: Boolean,
  showMenuBubble: Boolean,
  showMenuFloating: Boolean,
  placeHolderEditor: String,
  menuPosition: { type: String, default: 'top' },
  isSave: Boolean,
  maxHeight: String,
  minHeight: String,
  isDelete: Boolean
})

const emit = defineEmits(['editorSaveFromMenu', 'editorDeleteFromMenu', 'editor-update'])

const editor = ref(null)
const editorCustomRef = ref(null)
const editorCustomTextRef = ref(null)

watch(() => props.text, (newVal) => {
  if (editor.value && newVal !== editor.value.getHTML()) {
    editor.value.commands.setContent(newVal)
  }
})

onMounted(() => {
  window.addEventListener('scroll', handleScroll)

  editor.value = new Editor({
    content: props.text,
    editable: props.edit,
    onUpdate: ({ editor: ed }) => {
      emit('editor-update', ed.getHTML())
    },
    extensions: [
      Image.configure({ allowBase64: false, inline: true }),
      Link.configure({ target: null, linkOnPaste: true, openOnClick: true }),
      Placeholder.configure({
        placeholder: props.placeHolderEditor ?? 'Write something …'
      }),
      StarterKit,
      Typography,
      TaskList,
      TaskItem.configure({
        nested: true,
        HTMLAttributes: { class: 'custom-checklist--items' }
      })
    ]
  })
})

onBeforeUnmount(() => {
  editor.value?.destroy()
  window.removeEventListener('scroll', handleScroll)
})

function editorUpdate(event) {
  // placeholder for compatibility
}

function handleScroll() {
  return false
}
</script>

<style lang="scss">
.tiptap p.is-editor-empty:first-child::before {
  content: attr(data-placeholder);
  float: left;
  color: #adb5bd;
  pointer-events: none;
  height: 0;
}

.tiptap {
  > * + * { margin-top: 0.75em; }
  ul, ol { padding: 0 1rem; }
  h1, h2, h3, h4, h5, h6 { line-height: 1.1; }
  code { font-family: MyFancyCustomFont, monospace; font-size: inherit; }
  pre {
    background: rgb(var(--v-theme-surface-light));
    border: 0px solid #ddd;
    border-left: 3px solid #f36d33;
    page-break-inside: avoid;
    font-family: monospace;
    line-height: 1.6;
    margin-bottom: 1.6em;
    max-width: 100%;
    overflow: auto;
    padding: 1em 1.5em;
    display: block;
    word-wrap: break-word;
  }
  img { max-width: 100%; height: auto; }
  blockquote { padding-left: 1rem; border-left: 2px solid rgba(#0D0D0D, 0.1); }
  hr { border: none; border-top: 2px solid rgba(#0D0D0D, 0.1); margin: 2rem 0; }

  ul[data-type="taskList"] {
    list-style: none;
    padding: 0;
    margin: 0;

    li {
      align-items: flex-start;
      display: flex;

      > label { flex: 0 0 auto; margin-right: 0.5rem; user-select: none; }
      > div { flex: 1 1 auto; }

      input[type="checkbox"] {
        width: 20px;
        height: 20px;
        background-color: rgb(var(--v-theme-on-surface-variant)) !important;
        border-radius: 50%;
        vertical-align: middle;
        appearance: none;
        -webkit-appearance: none;
        outline: none;
        cursor: pointer;
        transition: all 0.2s;

        &:checked {
          accent-color: rgb(var(--v-theme-primary)) !important;
          background-color: rgb(var(--v-theme-primary)) !important;
          color: #ffffff !important;
          &:before { transform: rotate(45deg); }
        }
      }
    }
  }
}

.editor-custom_main {
  button, input, select {
    font-size: inherit;
    font-family: inherit;
    color: rgb(0, 0, 0);
    accent-color: black;
    border-width: 0px;
    border-style: solid;
    border-color: black;
    border-image: initial;
    padding: 0.1rem 0.4rem;
    background: rgb(var(--v-theme-surface));
    color: rgba(var(--v-theme-on-surface), var(--v-high-emphasis-opacity));
  }
  .editor-custom {
    max-width: unset;
    box-shadow: 0 0 4px #d6d6d6;
    min-height: 100%;
    margin: 20px auto;
  }
}

.editor-control_buttons {
  position: fixed;
  top: 0;
  max-height: 32px;
  background-color: white;
  z-index: 1;
  width: 100%;
  max-width: 1440px;
}

.ProseMirror {
  padding: 12px;
  min-height: 100px;
}
.tiptap > * + * { margin-top: 5px; }
.ProseMirror:focus { outline: none; }
.tippy-box { max-width: 732px !important; }

.tiptap div.is-empty:first-child::before {
  color: #adb5bd;
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}
p.is-empty:first-child::before {
  color: #adb5bd;
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}
.editor-custom.__fixed {
  .editor-custom_menu { top: 0; position: fixed; }
  .editor-custom_text { padding-top: 40px; }
}
.editor-custom_menu--fixed_top {
  overflow-x: auto;
  z-index: 9;
  .editor--menu {
    display: flex;
    flex-wrap: nowrap;
    justify-content: space-between;
    max-width: calc(100vw - 15px);
    overflow-x: auto;
  }
}
.editor-custom_text { overflow-y: auto; }
.editor-custom_menu {
  z-index: 2;
  background-color: #f4f4f4;
  padding: 2px;
  button {
    border: none;
    border-radius: 0;
    padding: 3px;
    margin: 0.2rem;
  }
}
</style>
