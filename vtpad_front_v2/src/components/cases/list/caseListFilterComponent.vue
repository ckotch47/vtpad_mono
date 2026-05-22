<template>
<div class="py-8 pa-8">
  <v-text-field label="Search" variant="outlined" v-model="searchCaseModel" @update:modelValue="searchCaseEmitEvent" @keydown.enter="searchCaseEmitEvent" @focusout="searchCaseEmitEvent"/>

  <v-text-field
    v-if="showCreate"
    label="Type text and press enter"
    variant="outlined"
    @keydown.enter="newCase"
    v-model="newCaseName"
  />

</div>
</template>

<script>
import axios from "axios";

export default {
  name: "caseListFilterComponent",
  emits: ['newTestCaseEmit', 'searchCaseEmit'],
  props: {
    spaceId: String,
    showCreate: Boolean
  },
  data(){
    return{
      newCaseName: undefined,
      searchCaseModel: undefined
    }
  },
  methods:{
    searchCaseEmitEvent(){
      this.$emit('searchCaseEmit', this.searchCaseModel)
    },
    newCase(){
      if(!this.newCaseName) return
      axios.post(`/api/v1/testcases`,{
        title: this.newCaseName,
        space_id: this.spaceId
      }).then(res => {
        this.$emit('newTestCaseEmit', res.data)
      })
      this.newCaseName = undefined
    }
  }
}
</script>

<style scoped>

</style>
