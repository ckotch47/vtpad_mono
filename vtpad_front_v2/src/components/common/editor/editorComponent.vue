
<template>
  <div class="editor-custom_main">

    <div class="editor-custom" ref="editorCustomRef">

      <div class="editor-custom_menu--fixed_top"  v-if="editor  && showMenuFixed">
        <editor-menu-component
          :editor="editor"
          @editorSaveFromMenu="$emit('editorSaveFromMenu')"
          @editorDeleteFromMenu="$emit('editorDeleteFromMenu')"
          @editorUpdateEmit="editorUpdate"
          :is-save="isSave"
          :is-delete="isDelete"
        />
      </div>
      <div class="editor-custom_text" :style="{'max-height': maxHeight ?? '340px', 'min-height': minHeight ?? '100px'}" ref="editorCustomTextRef">
        <bubble-menu
          :editor="editor"
          :tippy-options="{ duration: 100 }"
          v-if="editor && showMenuBubble"
        >
          <editor-menu-component :editor="editor" />
        </bubble-menu>

        <floating-menu
          :editor="editor"
          :tippy-options="{ duration: 100 }"
          max-with="732px"
          v-if="editor && showMenuFloating"
        >
          <editor-menu-component :editor="editor" />
        </floating-menu>


        <editor-content :editor="editor" />


      </div>

    </div>


  </div>
</template>

<script setup>

</script>

<script>

import { Editor, EditorContent, BubbleMenu, FloatingMenu } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import Typography from '@tiptap/extension-typography'
import Image from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import TaskItem from '@tiptap/extension-task-item'
import TaskList from '@tiptap/extension-task-list'
import EditorMenuComponent from "@/components/common/editor/editorMenuComponent.vue";

export default {
  props: {
    text: String,
    edit: Boolean,
    postId: undefined,
    showMenuFixed: Boolean,
    showMenuBubble: Boolean,
    showMenuFloating: Boolean,
    placeHolderEditor: String,
    menuPosition: 'top' || 'bottom',
    isSave: Boolean,
    maxHeight: String,
    minHeight: String,
    isDelete: Boolean,
  },
  emits: ["editorSaveFromMenu", 'editorDeleteFromMenu', 'editor-update'],
  name: "editorComponent",
  components: {
    EditorContent,
    FloatingMenu,
    BubbleMenu,
    EditorMenuComponent
  },
  data() {
    return {
      editor: null,
    }
  },
  created () {
    window.addEventListener('scroll', this.handleScroll);
  },
  watch: {
    text(newVal) {
      if (this.editor && newVal !== this.editor.getHTML()) {
        this.editor.commands.setContent(newVal)
      }
    }
  },
  mounted() {

    this.editor = new Editor({
      content: this.text,
      editable: this.edit,
      selectShow: this.edit,
      onUpdate: ({ editor }) => {
        this.$emit('editor-update', editor.getHTML());
      },
      extensions: [
        Image.configure({
          allowBase64: false,
          inline: true
        }),
        Link.configure({
          target: null,
          linkOnPaste: true,
          openOnClick: true,
        }),
        Placeholder.configure({
          placeholder: this.placeHolderEditor ?? 'Write something …',
        }),
        StarterKit,
        Typography,

        TaskList,
        TaskItem.configure({
          nested: true,
          HTMLAttributes: {
            class: 'custom-checklist--items',
          },
        }),
      ],
    })

  },

  beforeUnmount() {
    this.editor.destroy();
    window.removeEventListener('scroll', this.handleScroll);
  },
  methods:{
    editorUpdate(event){
      // console.log(event);
      // this.editor.commands.setContent(event)
    },
    handleScroll () {
      return false
      // if(window.scrollY > 198 && (window.innerHeight - this.$refs.edutirCustomTextRef.clientHeight) < 0){
      //
      //   this.$refs.editorCustomRef.classList.add('__fixed')
      //   // this.$refs.editorCustomMenuRef.classList.add('__fixed')
      // }else{
      //   this.$refs.editorCustomRef.classList.remove('__fixed')
      //   // this.$refs.editorCustomMenuRef.classList.remove('__fixed')
      // }

    }
  }
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
/* Basic editor styles */
.tiptap {
  > * + * {
    margin-top: 0.75em;
  }

  ul,
  ol {
    padding: 0 1rem;
  }

  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    line-height: 1.1;
  }

  code {
    font-family: MyFancyCustomFont, monospace;
    font-size: inherit;
  }
  pre {
    background: rgb(var(--v-theme-surface-light));
    border: 0px solid #ddd;
    border-left: 3px solid #f36d33;
    page-break-inside: avoid;
    font-family: monospace;
    //font-size: 15px;
    line-height: 1.6;
    margin-bottom: 1.6em;
    max-width: 100%;
    overflow: auto;
    padding: 1em 1.5em;
    display: block;
    word-wrap: break-word;
  }

  img {
    max-width: 100%;
    height: auto;
  }

  blockquote {
    padding-left: 1rem;
    border-left: 2px solid rgba(#0D0D0D, 0.1);
  }

  hr {
    border: none;
    border-top: 2px solid rgba(#0D0D0D, 0.1);
    margin: 2rem 0;
  }

  ul[data-type="taskList"] {
    list-style: none;
    //margin-left: 0;
    padding: 0;
    margin: 0;

    li {
      align-items: flex-start;
      display: flex;

      > label {
        flex: 0 0 auto;
        margin-right: 0.5rem;
        //margin-top: 2px;
        user-select: none;
      }

      > div {
        flex: 1 1 auto;
      }

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

        &:checked{
          accent-color: rgb(var(--v-theme-primary)) !important;
          background-color: rgb(var(--v-theme-primary)) !important;
          color: #ffffff !important;
          &:before{
            transform: rotate(45deg);
          }
        }
      }
    }







  }
}

.editor-custom_main{
  //margin: 20px 0;
  button, input, select {
    font-size: inherit;
    font-family: inherit;
    color: rgb(0, 0, 0);
    accent-color: black;
    /* margin: 0.1rem; */
    border-width: 0px;
    border-style: solid;
    border-color: black;
    border-image: initial;
    /* border-radius: 0.3rem; */
    padding: 0.1rem 0.4rem;
    background: rgb(var(--v-theme-surface));
    color: rgba(var(--v-theme-on-surface), var(--v-high-emphasis-opacity));
  }
  .editor-custom{
      max-width: unset;
      box-shadow: 0 0 4px #d6d6d6;
      min-height: 100%;
      margin: 20px auto;
      //max-height: 372px;
      //overflow-y: auto;
  }
}

.editor-control_buttons{
  position: fixed;
  top: 0;
  max-height: 32px;
  background-color: white;
  z-index: 1;
  width: 100%;
  max-width: 1440px;
}
.ProseMirror{
  // margin-top: 32px;
  padding: 12px;
  min-height: 100px;
  //font-size: 18px;
}
.tiptap > * + * {
  margin-top: 5px;
}

.ProseMirror:focus {
  outline: none;
}
.tippy-box{
  max-width: 732px!important;
  //background: whitesmoke;
}
.tiptap div.is-empty:first-child::before{
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
.editor-custom.__fixed{
  .editor-custom{
    &_menu{
      top: 0;
      position: fixed;
    }
    &_text{
      padding-top: 40px;

    }
  }
}
.editor-custom_menu--fixed{
  &_top{
    //position: absolute;
    //width: 100%;
    //max-width: calc(732px - 45px);
    //background: rgb(var(--v-theme-background));
    overflow-x: auto;
    z-index: 9;
    //margin: 0 10px;
    .editor--menu{
      display: flex;
      flex-wrap: nowrap;
      justify-content: space-between;
      max-width: calc(100vw - 15px);
      overflow-x: auto;
    }
  }
}
.editor-custom{
  &_text{
    //margin-top: 32px;
    //max-height: 340px;
    overflow-y: auto;
  }
  &_menu{

    z-index: 2;
    background-color: #f4f4f4;
    padding: 2px;


    button{
      border: none;
      border-radius: 0;
      padding: 3px;
      margin: 0.2rem;
    }
  }


}
</style>
