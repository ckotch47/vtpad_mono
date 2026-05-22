<template>
  <v-alert>
    <div class="d-flex justify-space-between flex-grow-1">
      <div>
        {{comment.create_user.username}}<br>
        <div v-html="sanitizedText" v-if="comment.view === 'comment'"></div>
      </div>
      <div class="flex-shrink-0">
          <v-icon icon="mdi-pencil" size="14" @click="editComment"/>
          {{comment.create_date ? comment.create_date.split('T')[0] : ''}}
      </div>
    </div>
  </v-alert>
</template>

<script>
import { sanitizeHtml } from '@/utils/sanitize';

export default {
  name: "bugsModalCommentCommentElem",
  props:{
    username: String,
    text: String,
    date: String,
    comment: Object
  },
  emits: ['editComment'],
  data(){
    return{
      textJson: {
        name: undefined,
        from: undefined,
        to: undefined
      }
    }
  },
  mounted() {
  },
  computed: {
    sanitizedText() {
      return sanitizeHtml(this.comment?.text);
    }
  },
  methods:{
    editComment(){
      this.$emit('editComment',  this.comment)
    }
  }
}
</script>

<style scoped>

</style>
