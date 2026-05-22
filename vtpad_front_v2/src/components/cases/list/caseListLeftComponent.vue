<template>
  <v-card style="width: 100%" class="pa-4">

    <div class="d-flex justify-space-between mb-4 w-100 align-center"  >
      <div class="d-flex align-center" >
        <div class="text-primary">{{testCase.short_name ?? ''}}</div>
        <v-btn
          v-if="testCase.short_name"
          icon="mdi-link-variant"
          variant="plain"
          @click="copyIssueLink"
        />
      </div>
      <v-btn variant="text" icon="mdi-close" @click="setDefaultTestCase" v-if="!readOnly"/>
    </div>
    <v-text-field
      label="Link"
      variant="outlined"
      :model-value="testCase.link ?? '' "
      v-model="testCase.link"
    >
      <template v-slot:append>
        <a :href="testCase.link ?? '#'" target="_blank" >
          <v-icon :icon="'mdi-vector-link'" color="primary"></v-icon>
        </a>
      </template>
    </v-text-field>

    <v-text-field
      label="Title"
      variant="outlined"
      :model-value="testCase.title"
      v-model="testCase.title"
    />

    <span class="title_case-editor">Description </span>
    <editor-component
      :text="testCase.text"
      :edit="true"
      :placeHolderEditor="'Description…'"
      :show-menu-fixed="!readOnly"
      :show-menu-bubble="false"
      class="first"
      max-height="200px"
      ref="testCaseTextRef"
    />

    <span class="title_case-editor">Steps </span>
    <editor-component
      :text="testCase.steps"
      :edit="true"
      :placeHolderEditor="'Steps…'"
      :show-menu-fixed="!readOnly"
      :show-menu-bubble="false"
      max-height="200px"
      ref="testCaseStepsRef"
    />

    <span class="title_case-editor">Expected results </span>
    <editor-component
      :text="testCase.expected_results"
      :edit="true"
      :placeHolderEditor="'Expected results…'"
      :show-menu-fixed="!readOnly"
      max-height="200px"
      ref="testCaseExpectedRef"
    />

    <div
      class="d-flex justify-space-between mt-2"
      style="width: 100%"
      v-if="!readOnly"
    >
      <v-btn :color="'red'" variant="outlined" :text="'Delete'" :append-icon="'mdi-delete-forever'" @click="deleteTestCase"/>
      <v-btn :color="'primary'" variant="outlined" :text="'Save'" :append-icon="'mdi-content-save'" @click="saveTestCase"/>
    </div>
  </v-card>
</template>

<script>
import EditorComponent from "@/components/common/editor/editorComponent.vue";
import axios from "axios";
import {useAppStore} from "@/stores/app";

export default {
  name: "caseListLeftComponent",
  components: {EditorComponent},
  props:{
    caseId: String,
    readOnly: Boolean
  },
  emits: ['deleteTestCaseEmit', 'updateTestCaseEmits', 'newTestCaseEmits'],
  data(){
    return{
      loader: true,
      testCase: {
        "id": undefined,
        "create_date": undefined,
        "update_date": undefined,
        "title": undefined,
        "text": undefined,
        "steps": undefined,
        "expected_results": undefined,
        "sort": 0,
        "short_name": undefined,
        "link": undefined,
        "space_id": undefined,
      },
      testCaseBase: {
        "id": undefined,
        "create_date": undefined,
        "update_date": undefined,
        "title": undefined,
        "text": undefined,
        "steps": undefined,
        "expected_results": undefined,
        "sort": 0,
        "short_name": undefined,
        "link": undefined,
        "space_id": undefined,
      },
      spaceId: this.$route.params.spaceId,
    }
  },
  mounted() {
    if(this.caseId){
      axios.get(`/api/v1/testcases/detail/${this.caseId}`).then(res => {
        this.testCase = res.data
      })
    }
  },
  updated() {
    if(this.caseId){
      axios.get(`/api/v1/testcases/detail/${this.caseId}`).then(res => {
        this.testCase = res.data
      })
    }
  },
  methods:{
    copyIssueLink(){
      if(!this.testCase.short_name) return;
      navigator.clipboard.writeText(`${location.origin}/cases/${this.testCase.short_name}`);
    },
    setDefaultTestCase(){
      this.testCase = {
        "id": undefined,
        "create_date": undefined,
        "update_date": undefined,
        "title": undefined,
        "text": undefined,
        "steps": undefined,
        "expected_results": undefined,
        "sort": 0,
        "short_name": undefined,
        "link": undefined,
        "space_id": undefined,
      }
    },
    saveTestCase(){
      this.testCase.text = this.$refs.testCaseTextRef.$data.editor.getHTML();
      this.testCase.steps = this.$refs.testCaseStepsRef.$data.editor.getHTML();
      this.testCase.expected_results = this.$refs.testCaseExpectedRef.$data.editor.getHTML();
      this.testCase.sort = this.testCase.sort?.toString() ?? 0;
      if(!this.testCase.id) {
        this.createTestCase();
        return;
      }
      axios.patch(`/api/v1/testcases/${this.testCase.id}`, this.testCase).then(()=>{
        this.$emit('updateTestCaseEmits', this.testCase)
      });
    },
    createTestCase(){
      axios.post(`/api/v1/testcases`, {
        ...this.testCase,
        space_id: this.spaceId
      }).then(res => {
        this.testCase = res.data;
        this.$emit('newTestCaseEmits', this.testCase)
      })
    },
    deleteTestCase(){
      axios.delete(`/api/v1/testcases/${this.testCase.id}`).then(()=>{
        this.$emit('deleteTestCaseEmit', this.testCase.id)
        this.setDefaultTestCase();
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
.title_case-editor {
  font-size: 11px;
  color: #8d8d8d;
}
</style>
