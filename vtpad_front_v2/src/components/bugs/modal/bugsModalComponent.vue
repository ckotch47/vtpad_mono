<template>
  <v-dialog
    :model-value="isActive"
    fullscreen
    :class="!full ? 'bug-modal' : 'bug-modal--full'"
    @update:model-value="$emit('closeBugModal')"
    @close="$emit('closeBugModal')"
  >
    <v-card>
      <v-toolbar>
        <v-btn icon="mdi-close" @click="$emit('closeBugModal')" />
        <v-toolbar-title />
        <div class="d-flex custom-title">
          <div>
            <span>{{ openBugElem ? openBugElem.short_name : bugItem.short_name }}</span>
            <v-btn icon="mdi-link-variant" variant="plain" @click="copyIssueLink" />
          </div>
          <div v-if="bugItem?.title" class="title-text">
            {{ bugItem.title }}
          </div>
          <div>
            <v-avatar color="grey" size="24" :data-placeholder="bugItem.create_user.username[0].toLowerCase()">
              <v-img :src="bugItem.create_user.avatar.filepath" :alt="bugItem.create_user.username || 'User avatar'" />
            </v-avatar>
            {{ bugItem.create_user.username }}
          </div>
        </div>
        <v-spacer />
      </v-toolbar>

      <div v-if="loader">
        <v-progress-linear color="primary" indeterminate />
      </div>

      <v-text-field
        v-if="!loader"
        v-model="bugItem.title"
        class="custom-text--input"
        variant="outlined"
        placeholder="Title"
        @change="updateBugTitle"
      />

      <div v-if="!loader" class="bug-modal--content d-flex">
        <div class="bug-modal--content_left">
          <bugs-modal-editor-list-component
            :bug="openBugElem"
            @update-bug-text-emit="getHistory"
          />
          <bugs-modal-comment-component
            :bug="openBugElem"
            :edit="isEditComment"
            :comment="editComment"
            @new-comment="newComment"
          />
          <bugs-modal-history-component-v2
            :bug="openBugElem"
            :history="history"
            @edit-comment="editCommentEvent"
          />
          <attachment-list-component
            v-if="bugItem?.id"
            entity-type="bug"
            :entity-id="bugItem.id"
          />
        </div>
        <div class="bug-modal--content_right">
          <bugs-modal-setting-component
            :bug="openBugElem"
            :filter="filters"
            @update-bug="updateBug"
          />
        </div>
      </div>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { bugService, commentService } from '@/services'
import BugsModalEditorListComponent from '@/components/bugs/modal/bugsModalEditorListComponent.vue'
import BugsModalSettingComponent from '@/components/bugs/modal/bugsModalSettingComponent.vue'
import BugsModalCommentComponent from '@/components/bugs/modal/bugsModalCommentComponent.vue'
import BugsModalHistoryComponentV2 from '@/components/bugs/modal/bugsModalHistoryComponentV2.vue'
import AttachmentListComponent from '@/components/attachments/attachmentListComponent.vue'

const props = defineProps({
  isActive: Boolean,
  bugItem: Object,
  filters: Object,
  full: Boolean
})

const emit = defineEmits(['updateBug', 'closeBugModal'])

const loader = ref(true)
const openBugElem = ref(undefined)
const history = ref([])
const isEditComment = ref(false)
const editComment = ref(undefined)

function editCommentEvent(comment) {
  isEditComment.value = true
  editComment.value = comment
}

function newComment() {
  isEditComment.value = false
  editComment.value = undefined
  getHistory()
}

async function getHistory() {
  const bugId = openBugElem.value?.id || props.bugItem?.id
  if (!bugId) return
  history.value = (await commentService.list(bugId)).data.reverse()
}

function updateBug(bug) {
  emit('updateBug', bug)
  getHistory()
}

function updateBugTitle() {
  bugService.update(props.bugItem.id, {
    title: props.bugItem.title
  }).then(res => {
    openBugElem.value = res.data
    emit('updateBug', res.data)
    getHistory()
  })
}

function openBugItem() {
  if (props.full) {
    openBugElem.value = props.bugItem
    loader.value = false
    return
  }
  bugService.getById(props.bugItem.id).then(res => {
    openBugElem.value = res.data
    loader.value = false
  })
}

function copyIssueLink() {
  navigator.clipboard.writeText(`${location.origin}/issue/${openBugElem.value.short_name}`)
}

watch(() => props.bugItem, () => {
  if (props.bugItem) {
    openBugItem()
    getHistory()
  }
}, { immediate: true })
</script>

<style lang="scss">
.bug-modal {
  &--content {
    &_left {
      width: 100%;
      max-width: 732px;
    }
    &_right {
      margin: 20px 10px 20px 10px;
      width: 60%;
    }
  }
  .v-overlay__content {
    width: 75vw !important;
    max-width: 1400px !important;
    right: 0;
    margin: 0;
    left: unset !important;
  }
  .v-card {
    width: 75vw !important;
    max-width: 1400px;
  }
  .editor-custom {
    max-width: 732px;
    box-shadow: 0 0 4px #d6d6d6;
    margin: 20px 10px;
  }
  .custom-title {
    width: 90%;
    display: flex;
    flex-direction: row;
    flex-wrap: nowrap;
    justify-content: space-between;
    align-items: center;
  }
  .custom-text--input {
    margin: 20px 10px 0 10px;
    max-height: 56px;
    input {
      border: none;
    }
  }
  .title-text {
    width: 65%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 65%;
  }
}

@media (width <= 1500px) {
  .bug-modal {
    .v-overlay__content {
      width: 85vw !important;
      right: 0;
      margin: 0;
      left: unset !important;
    }
    .v-card {
      width: 85vw !important;
    }
  }
}

@media (width <= 1300px) {
  .bug-modal {
    .v-overlay__content {
      width: 100vw !important;
      right: 0;
      margin: 0;
      left: unset !important;
    }
    .v-card {
      width: 100vw !important;
    }
  }
}

@media (width <= 900px) {
  .custom-title {
    div:nth-child(1), div:nth-child(3) {
      display: none;
    }
  }
  .bug-modal {
    .bug-modal--content_right {
      width: 100%;
      padding-right: 18px;
    }
    .bug-modal--content_left {
      padding-right: 18px;
      margin: auto;
    }
    .editor-custom {
      max-width: unset;
      width: 100%;
    }
    .v-overlay__content {
      width: 100vw !important;
      right: 0;
      margin: 0;
      left: unset !important;
      min-width: unset !important;
    }
    .v-card {
      min-width: unset !important;
      width: 100vw !important;
    }
    .bug-modal--content {
      flex-direction: column-reverse;
    }
  }
}
</style>
