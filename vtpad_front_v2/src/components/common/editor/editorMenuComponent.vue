<template>
  <div class="editor--menu">
    <!-- Text formatting -->
    <div class="editor-menu-group">
      <v-tooltip text="Bold (Ctrl+B)" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().toggleBold().run()"
            :disabled="!editor.can().chain().focus().toggleBold().run()"
            :class="{ 'is-active': editor.isActive('bold') }"
          >
            <v-icon icon="mdi-format-bold" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Italic (Ctrl+I)" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().toggleItalic().run()"
            :disabled="!editor.can().chain().focus().toggleItalic().run()"
            :class="{ 'is-active': editor.isActive('italic') }"
          >
            <v-icon icon="mdi-format-italic" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Underline (Ctrl+U)" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().toggleUnderline().run()"
            :disabled="!editor.can().chain().focus().toggleUnderline().run()"
            :class="{ 'is-active': editor.isActive('underline') }"
          >
            <v-icon icon="mdi-format-underline" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Strikethrough" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().toggleStrike().run()"
            :disabled="!editor.can().chain().focus().toggleStrike().run()"
            :class="{ 'is-active': editor.isActive('strike') }"
          >
            <v-icon icon="mdi-format-strikethrough-variant" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Clear formatting" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().unsetAllMarks().run()"
          >
            <v-icon icon="mdi-format-color-marker-cancel" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
    </div>

    <v-divider vertical class="mx-1" />

    <!-- Alignment -->
    <div class="editor-menu-group">
      <v-tooltip text="Align left" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().setTextAlign('left').run()"
            :class="{ 'is-active': editor.isActive({ textAlign: 'left' }) }"
          >
            <v-icon icon="mdi-format-align-left" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Align center" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().setTextAlign('center').run()"
            :class="{ 'is-active': editor.isActive({ textAlign: 'center' }) }"
          >
            <v-icon icon="mdi-format-align-center" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Align right" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().setTextAlign('right').run()"
            :class="{ 'is-active': editor.isActive({ textAlign: 'right' }) }"
          >
            <v-icon icon="mdi-format-align-right" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
    </div>

    <v-divider vertical class="mx-1" />

    <!-- Structure -->
    <div class="editor-menu-group">
      <v-tooltip text="Heading 2" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
            :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }"
          >
            <v-icon icon="mdi-format-header-2" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Heading 3" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().toggleHeading({ level: 3 }).run()"
            :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }"
          >
            <v-icon icon="mdi-format-header-3" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Bullet list" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().toggleBulletList().run()"
            :class="{ 'is-active': editor.isActive('bulletList') }"
          >
            <v-icon icon="mdi-format-list-bulleted" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Task list" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().toggleTaskList().run()"
            :class="{ 'is-active': editor.isActive('taskList') }"
          >
            <v-icon icon="mdi-format-list-checkbox" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Reset checklist" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="refreshCheckList"
          >
            <v-icon icon="mdi-refresh" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Ordered list" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().toggleOrderedList().run()"
            :class="{ 'is-active': editor.isActive('orderedList') }"
          >
            <v-icon icon="mdi-order-numeric-ascending" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Code block" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().toggleCodeBlock().run()"
            :class="{ 'is-active': editor.isActive('codeBlock') }"
          >
            <v-icon icon="mdi-code-braces" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Quote" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().toggleBlockquote().run()"
            :class="{ 'is-active': editor.isActive('blockquote') }"
          >
            <v-icon icon="mdi-format-quote-close" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Horizontal rule" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().setHorizontalRule().run()"
          >
            <v-icon icon="mdi-minus" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
    </div>

    <v-divider vertical class="mx-1" />

    <!-- Insert -->
    <div class="editor-menu-group">
      <v-tooltip text="Link" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="openLinkDialog"
            :class="{ 'is-active': editor.isActive('link') }"
          >
            <v-icon icon="mdi-link" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Image" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="openFileUpload"
          >
            <v-icon icon="mdi-image" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Insert table" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="insertTable"
          >
            <v-icon icon="mdi-table" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Add column after" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().addColumnAfter().run()"
            :disabled="!editor.can().addColumnAfter()"
          >
            <v-icon icon="mdi-table-column-plus-after" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Add row after" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().addRowAfter().run()"
            :disabled="!editor.can().addRowAfter()"
          >
            <v-icon icon="mdi-table-row-plus-after" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Delete table" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().deleteTable().run()"
            :disabled="!editor.can().deleteTable()"
          >
            <v-icon icon="mdi-table-remove" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
    </div>

    <v-divider vertical class="mx-1" />

    <!-- History -->
    <div class="editor-menu-group">
      <v-tooltip text="Undo" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().undo().run()"
            :disabled="!editor.can().chain().focus().undo().run()"
          >
            <v-icon icon="mdi-undo" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Redo" location="top">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            @click="editor.chain().focus().redo().run()"
            :disabled="!editor.can().chain().focus().redo().run()"
          >
            <v-icon icon="mdi-redo" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
    </div>

    <v-divider v-if="isSave || isDelete" vertical class="mx-1" />

    <!-- Actions -->
    <div v-if="isSave || isDelete" class="editor-menu-group">
      <v-tooltip text="Save" location="top" v-if="isSave">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            color="primary"
            @click="$emit('editorSaveFromMenu')"
          >
            <v-icon icon="mdi-content-save" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Delete" location="top" v-if="isDelete">
        <template #activator="{ props: tp }">
          <v-btn
            v-bind="tp"
            icon
            size="small"
            variant="text"
            density="compact"
            color="error"
            @click="$emit('editorDeleteFromMenu')"
          >
            <v-icon icon="mdi-delete" size="small" />
          </v-btn>
        </template>
      </v-tooltip>
    </div>

    <input
      type="file"
      ref="fileInput"
      style="display: none"
      multiple
      accept="image/jpeg, image/png, image/gif, image/webp"
      @change="uploadFile"
    />

    <!-- Link Dialog -->
    <v-dialog v-model="linkDialog" max-width="420">
      <v-card>
        <v-card-title class="text-subtitle-1">Add Link</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="linkUrl"
            label="URL"
            placeholder="https://..."
            density="compact"
            variant="outlined"
            hide-details="auto"
            class="mb-2"
            @keyup.enter="applyLink"
          />
          <v-text-field
            v-model="linkText"
            label="Text (optional)"
            placeholder="Leave empty to keep selected text"
            density="compact"
            variant="outlined"
            hide-details="auto"
            @keyup.enter="applyLink"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" size="small" @click="linkDialog = false">Cancel</v-btn>
          <v-btn v-if="editor.isActive('link')" color="error" variant="text" size="small" @click="removeLink">Remove</v-btn>
          <v-btn color="primary" variant="flat" size="small" @click="applyLink">Apply</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const props = defineProps({
  editor: { type: Object, default: null },
  isSave: Boolean,
  isDelete: Boolean,
  bubble: Boolean
})

const emit = defineEmits(['editorSaveFromMenu', 'editorDeleteFromMenu'])

const fileInput = ref(null)
const linkDialog = ref(false)
const linkUrl = ref('')
const linkText = ref('')

function openFileUpload() {
  fileInput.value?.click()
}

async function uploadFile(event) {
  const files = event.target.files
  if (!files || !files.length) return
  for (const file of files) {
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await axios.post('/v1/file/image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      const url = res.data?.filepath || res.data?.url || ''
      const fullUrl = url.startsWith('http') ? url : `${import.meta.env.VITE_API_BASE_URL}${url}`
      props.editor.chain().focus().setImage({ src: fullUrl }).run()
    } catch (e) {
      console.error('Image upload failed', e)
    }
  }
  event.target.value = ''
}

function openLinkDialog() {
  const previousUrl = props.editor.getAttributes('link').href
  linkUrl.value = previousUrl || ''
  linkText.value = ''
  linkDialog.value = true
}

function applyLink() {
  if (!linkUrl.value) {
    removeLink()
    return
  }
  if (linkText.value) {
    props.editor.chain().focus().insertContent(`<a href="${linkUrl.value}">${linkText.value}</a>`).run()
  } else {
    props.editor.chain().focus().extendMarkRange('link').setLink({ href: linkUrl.value }).run()
  }
  linkDialog.value = false
}

function removeLink() {
  props.editor.chain().focus().extendMarkRange('link').unsetLink().run()
  linkDialog.value = false
}

function insertTable() {
  props.editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
}

function refreshCheckList() {
  const html = props.editor.getHTML()
    .replaceAll('data-checked="true"', 'data-checked="false"')
    .replaceAll('checked="checked"', '')
  props.editor.commands.setContent(html)
}
</script>

<style lang="scss">
.editor--menu {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 2px;
  padding: 4px;

  .editor-menu-group {
    display: flex;
    align-items: center;
    gap: 2px;
  }

  .v-btn {
    margin: 0;
    border-radius: 4px;
    min-width: 28px;
    width: 28px;
    height: 28px;

    &.is-active {
      background-color: rgb(var(--v-theme-on-surface-variant));
      color: rgb(var(--v-theme-surface));
    }
  }
}
</style>
