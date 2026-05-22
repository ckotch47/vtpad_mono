<template>
  <div class="d-flex flex-column" >
    <editor-component
      :edit="true"
      :placeHolderEditor="'Comment…'"
      :text="isEdit ? this.comment.text : ''"
      :show-menu-fixed="true"
      :show-menu-floating="false"
      :show-menu-bubble="false"
      :menu-position="'top'"
      max-height="200px"
      ref="newCommentRef"
      :is-save="true"
      :is-delete="this.isEdit"
      @editorSaveFromMenu="newComment"
      @editorDeleteFromMenu="deleteComment"
    />

<!--    <div class="d-flex justify-end send-comment&#45;&#45;btn ">-->
<!--      <v-btn v-if="!this.isEdit" color="primary" class="" variant="outlined" @click="newComment">Send</v-btn>-->
<!--      <div class="d-flex justify-space-between w-100" v-else>-->
<!--        <v-btn color="red" class="" variant="outlined" @click="deleteComment">Delete</v-btn>-->
<!--        <v-btn color="primary" class="" variant="outlined" @click="updateComment">Edit</v-btn>-->

<!--      </div>-->
<!--    </div>-->
  </div>
</template>

<script>
import EditorComponent from "@/components/common/editor/editorComponent.vue";
import axios from "axios";

export default {
  name: "bugsModalCommentComponent",
  components: {EditorComponent},
  emits: ['updateComment', 'newComment'],
  props:{
    bug: Object,
    edit: Boolean,
    comment: Object
  },
  data(){
    return{
      isEdit: false,
      editComment: undefined
    }
  },
  updated() {
    this.isEdit = this.edit
  },
  methods:{
    async updateComment(){
      await axios.put(`/api/v1/comment/${this.comment.id}`,{
        text: this.$refs.newCommentRef.$data.editor.getHTML()
      })
      this.isEdit = false
      this.$emit('newComment')
    },
    async deleteComment(){
      await axios.delete(`/api/v1/comment/${this.comment.id}`)
      this.isEdit = false
      this.$emit('newComment')
    },
    async newComment(){
      if(this.isEdit){
        await this.updateComment();
        return;
      }
      if(this.$refs.newCommentRef.$data.editor.getHTML() === '<p></p>')
        return
      await axios.post(`/api/v1/comment/${this.bug.id}`,{
        text: this.$refs.newCommentRef.$data.editor.getHTML()
      })
      this.$emit('newComment')
      this.$refs.newCommentRef.$data.editor.commands.setContent('<p></p>')
    }
  }
}
</script>

<style lang="scss">
.v-timeline-item__body{
  width: 660px;
}
.send-comment--btn{
  margin: 0 10px 20px 10px;

}
</style>
