<template>
<v-card style="width: 100%" class="pa-4">
  <div class="d-flex justify-space-between mb-4 w-100 align-center"  >
    <div class="d-flex align-center" >
      <div class="text-primary">{{checklist.short_name ?? ''}}</div>
      <v-btn
        v-if="checklist.short_name"
        icon="mdi-link-variant"
        variant="plain"
        @click="copyIssueLink"
      />
    </div>
    <v-btn variant="text" icon="mdi-close" @click="setDefaultChecklist" v-if="!readOnly"/>
  </div>
  <v-text-field label="Title" variant="outlined" :model-value="checklist.title" v-model="checklist.title"/>
<!--  <span class="checklist-editor">Scenario </span>-->

  <editor-component
    :text="checklist.text"
    :edit="true"
    :placeHolderEditor="'Scenario…'"
    :show-menu-fixed="!readOnly"
    :show-menu-bubble="false"
    class="first"
    max-height="450px"
    min-height="450px"
    ref="checklistTextRef"
  />

  <div class="d-flex justify-space-between mt-2" style="width: 100%" v-if="!readOnly">
    <v-btn :color="'red'" variant="outlined" :text="'Delete'" :append-icon="'mdi-delete-forever'" @click="deleteChecklist"/>
    <v-btn :color="'primary'" variant="outlined" :text="'Save'" :append-icon="'mdi-content-save'" @click="saveChecklist"/>
  </div>
</v-card>
</template>

<script>
import EditorComponent from "@/components/common/editor/editorComponent.vue";
import axios from "axios";

export default {
  name: "checklistListRightComponent",
  components: {EditorComponent},
  emits: ['deleteChecklistEmit', 'updateChecklistEmits', 'closeChecklistEmits', 'newChecklistEmits'],
  props: {
    checklistId: String,
    readOnly: Boolean,
    edit: Boolean
  },
  data(){
    return{
      checklist: {
        "id": undefined,
        "create_date": undefined,
        "update_date": undefined,
        "title": undefined,
        "text": undefined,
        "state": undefined,
        "sort": 0,
        "short_name": undefined,
        "space_id": undefined,
      },
      checklistBase: {
        "id": undefined,
        "create_date": undefined,
        "update_date": undefined,
        "title": undefined,
        "text": undefined,
        "state": undefined,
        "sort": 0,
        "short_name": undefined,
        "space_id": undefined,
      },
      spaceId: this.$route.params.spaceId,
    }
  },
  mounted() {
    if(this.checklistId){
      axios.get(`/api/v1/checklist/${this.checklistId}`).then(res => {
        this.checklist = res.data
      })
    }else{
      this.checklist = this.checklistBase;
    }
  },

  updated() {
    if(this.checklistId){
      axios.get(`/api/v1/checklist/${this.checklistId}`).then(res => {
        this.checklist = res.data
      })
    }else{
      this.checklist = this.checklistBase;
    }
  },
  methods:{
    setDefaultChecklistBase(){
      return {
        "id": undefined,
        "create_date": undefined,
        "update_date": undefined,
        "title": undefined,
        "text": undefined,
        "state": undefined,
        "sort": 0,
        "short_name": undefined,
        "space_id": undefined,
      }
    },
    copyIssueLink(){
      if(!this.checklist.short_name) return;
      navigator.clipboard.writeText(`${location.origin}/list/${this.checklist.short_name}`);
    },
    setDefaultChecklist(){
      this.$emit('closeChecklistEmits')
      this.checklist = this.setDefaultChecklistBase();
    },
    saveChecklist(){
      this.checklist.text = this.$refs.checklistTextRef.$data.editor.getHTML();
      if(!this.checklist.id) {
        this.createChecklist();
        return
      }

      axios.patch(`/api/v1/checklist/${this.checklist.id}`, this.checklist).then(()=>{
        this.$emit('updateChecklistEmits', this.checklist)
      })
    },
    createChecklist(){
      axios.post(`/api/v1/checklist/${this.spaceId}`, this.checklist).then((res) => {
        this.checklist = res.data;
        this.$emit('newChecklistEmits', this.checklist);

      })

    },
    deleteChecklist(){
      axios.delete(`/api/v1/checklist/${this.checklist.id}`).then(()=>{
        this.$emit('deleteChecklistEmit', this.checklist.id);
        this.checklist = this.checklistBase;
      })
    }
  }
}
</script>

<style scoped lang="scss">
.editor-custom{
  max-width: 732px;
  box-shadow: 0 0 4px #d6d6d6;
  max-height: 280px;
//max-height: 732px;
  overflow-y: auto;
//margin: 20px 0;
&.first{
   margin-top: 0;
 }
}

.checklist-editor {
  font-size: 11px;
  color: #8d8d8d;
}
</style>
