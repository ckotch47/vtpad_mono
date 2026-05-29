<template>
    <v-dialog
      :model-value="isActive"
      @update:modelValue="$emit('closeBugModal')"

      fullscreen
      :class="!full ? 'bug-modal' : 'bug-modal--full' "
      @close="$emit('closeBugModal')"
    >

    <v-card >
      <v-toolbar>
        <v-btn
          icon="mdi-close"
          @click="$emit('closeBugModal')"
        ></v-btn>
        <v-toolbar-title />
        <div class="d-flex custom-title">
          <div>
            <span>{{openBugElem ? openBugElem.short_name : bugItem.short_name}}</span>
            <v-btn
              icon="mdi-link-variant"
              variant="plain"
              @click="copyIssueLink"
            />
          </div>
          <div class="title-text" v-if="bugItem?.title">
            {{bugItem.title}}
          </div>
          <div>
            <v-avatar
              color="grey"
              size="24"
              :data-placeholder="bugItem.create_user.username[0].toLowerCase()"
            >
              <v-img :src="bugItem.create_user.avatar.filepath" :alt="bugItem.create_user.username || 'User avatar'" />
            </v-avatar>
            {{bugItem.create_user.username}}
          </div>
        </div>

        <v-spacer></v-spacer>
      </v-toolbar>

      <div v-if="loader">
        <v-progress-linear
          color="primary"
          indeterminate
        ></v-progress-linear>
      </div>

      <v-text-field
        v-if="!loader"
        class="custom-text--input"
        :model-value="openBugElem.title"
        v-model="bugItem.title"
        @change="updateBugTitle($event)"
        variant="outlined"
        placeholder="Title"
      />

      <div v-if="!loader" class="bug-modal--content d-flex">
        <div class="bug-modal--content_left">
          <bugs-modal-editor-list-component
            :bug="openBugElem"
            @updateBugTextEmit="this.getHistory().then()"
          />
<!--          <bugs-modal-history-component-->
<!--            :bug="openBugElem"-->
<!--            :history="history"-->
<!--            @editComment="editCommentEvent"-->
<!--          />-->
          <bugs-modal-comment-component
            :bug="openBugElem"
            :edit="isEditComment"
            :comment="editComment"
            @new-comment="newComment"
          />
          <bugs-modal-history-component-v2
            :bug="openBugElem"
            :history="history"
            @editComment="editCommentEvent"
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

<script>

import BugsModalEditorListComponent from "@/components/bugs/modal/bugsModalEditorListComponent.vue";
import BugsModalSettingComponent from "@/components/bugs/modal/bugsModalSettingComponent.vue";
import { bugService, commentService } from '@/services'
import BugsModalCommentComponent from "@/components/bugs/modal/bugsModalCommentComponent.vue";
import BugsModalHistoryComponentV2 from "@/components/bugs/modal/bugsModalHistoryComponentV2.vue";
import AttachmentListComponent from "@/components/attachments/attachmentListComponent.vue";

export default {
  name: "bugsModalComponent",
  components: {
    BugsModalHistoryComponentV2,
    BugsModalCommentComponent,
    BugsModalSettingComponent, BugsModalEditorListComponent, AttachmentListComponent},
  emits: ['updateBug', 'closeBugModal'],
  props: {
    isActive: Boolean,
    bugItem: Object,
    filters: Object,
    full: Boolean
  },
  data(){
    return{
      title: 'Очень длинное название ну прям немного',
      loader: true,
      openBugElem: undefined,
      history: [],
      isEditComment: false,
      editComment: undefined
    }
  },
  mounted() {
    if(this.bugItem)
      this.openBugItem()
      this.getHistory().then()
  },
  updated() {
  },
  methods:{
    editCommentEvent(comment){
      this.isEditComment = true
      this.editComment = comment
    },
    newComment(){
      this.isEditComment = false
      this.editComment = undefined
      this.getHistory().then();
    },
    async getHistory(){
      this.history = (await commentService.list(this.bugItem.id)).data.reverse()
    },
    updateBug(bug){
      this.$emit('updateBug', bug);
      this.getHistory().then()
    },
    updateBugTitle(event){
      bugService.update(this.bugItem.id,{
        title: event.target.value
      }).then(res => {
        this.openBugElem = res.data
        this.$emit('updateBug', res.data)
        this.getHistory().then()
      })
    },
    updateComment(){

    },
    openBugItem(){
      if(this.full) {
        this.openBugElem = this.bugItem
        this.loader = false
        return
      }
      const bugId = this.bugItem.id;
      bugService.getById(bugId).then(res => {
        this.openBugElem = res.data
        this.loader = false
      })
    },
    copyIssueLink(){
      navigator.clipboard.writeText(`${location.origin}/issue/${this.openBugElem.short_name}`);
    }
  }


}
</script>

<style lang="scss">

.bug-modal {
  //.v-avatar::before{
  //  color: white;
  //  content: attr(data-placeholder);
  //  margin-left: 24px;
  //}
  &--content{
    &_left{
      width: 100%;
      max-width: 732px;
    }
    &_right{
      margin: 20px 10px 20px 10px;
      width: 60%;
    }
  }
  .v-overlay__content{
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
  .editor-custom{
    max-width: 732px;
    box-shadow: 0 0 4px #d6d6d6;
    //max-height: 372px;
    //overflow-y: auto;
    margin: 20px 10px;
  }
  .custom-title{
    width: 90%;
    display: flex;
    flex-direction: row;
    flex-wrap: nowrap;
    justify-content: space-between;
    align-items: center;
  }
  .custom-text--input{
    margin: 20px 10px 0 10px;
    max-height: 56px;
    input{
      border: none
    }

  }
  .title-text{
    width: 65%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 65%;
  }

}



@media (width <= 1500px) {
  .bug-modal, {
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
  .custom-title{
    div:nth-child(1), div:nth-child(3){
      display: none;
    }
  }
  .bug-modal,  {
    .bug-modal--content_right{
      width: 100%;

      padding-right: 18px;
    }
    .bug-modal--content_left{
      padding-right: 18px;
      margin: auto;
    }
    .editor-custom{
      max-width: unset;
      width: 100%;
    }
    //.send-comment--btn{
    //  width: 100%;
    //}
    .v-overlay__content {
      width: 100vw !important;
      right: 0;
      margin: 0;
      left: unset !important;
      min-width: unset!important;
    }
    .v-card {
      min-width: unset!important;
      width: 100vw !important;
    }
    .bug-modal--content{

      flex-direction: column-reverse;
    }
  }
}

</style>

