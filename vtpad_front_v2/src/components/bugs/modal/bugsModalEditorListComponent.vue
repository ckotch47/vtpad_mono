<template>
  <editor-component
    class="bug-modal--text"
    :edit="true"
    :placeHolderEditor="'Text…'"
    :text="bug.text"
    :show-menu-fixed="true"
    :show-menu-floating="false"
    :show-menu-bubble="false"
    :menu-position="'top'"
    is-save

    max-height="340px"
    @editorSaveFromMenu="updateEditor('text')"
    @focusout="updateEditor('text')"
    ref="editorBugTextRef"
  />
<!--  <div class="d-flex justify-end" style="margin-right: 10px">-->
<!--    <v-btn color="primary" class="" variant="outlined" @click="updateEditor('text')">Save</v-btn>-->
<!--  </div>-->
<!--  <editor-component-->
<!--    :edit="true"-->
<!--    :placeHolderEditor="'Steps…'"-->
<!--    :text="bug.steps"-->
<!--    @focusout="updateEditor('steps')"-->
<!--    ref="editorBugTextSteps"-->
<!--  />-->

<!--  <editor-component-->
<!--    :edit="true"-->
<!--    :placeHolderEditor="'Link…'"-->
<!--    :text="bug.additional_link"-->
<!--    @focusout="updateEditor('additional_link')"-->
<!--    ref="editorBugTextLink"-->
<!--  />-->
<!--  <v-divider :thickness="1" ></v-divider>-->

</template>

<script>
import EditorComponent from "@/components/common/editor/editorComponent.vue";
import axios from "axios";


export default {
  name: "bugsModalEditorListComponent",
  components: {EditorComponent},
  emits: ['updateBugTextEmit'],
  props:{
    bug: Object
  },
  data(){
    return{
      history: undefined
    }
  },
  async mounted() {
  },
  methods:{
    updateEditor(name){
      let value = undefined
      switch (name) {
        case 'text':
          value = this.$refs.editorBugTextRef.$data.editor.getHTML()
          break;
        case 'steps':
          value = this.$refs.editorBugTextSteps.$data.editor.getHTML()
          break;
        case 'additional_link':
          value = this.$refs.editorBugTextLink.$data.editor.getHTML()
          break;
      }
      axios.patch(`/api/v2/bugs/${this.bug.id}`,{
        [name]: value
      }).then( () => {
        this.$emit('updateBugTextEmit')
      })
    }
  }
}
</script>

<style scoped lang="scss">
.bug-modal--text{
  height: 370px;
  margin-bottom: 15px;
}
</style>
