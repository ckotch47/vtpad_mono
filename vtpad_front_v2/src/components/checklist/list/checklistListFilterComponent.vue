<template>
  <div class="py-8 pa-8">
    <v-text-field
      label="Search" variant="outlined"
      v-model="searchChecklist"
      @update:modelValue="$emit('searchChecklistEmit', searchChecklist)"
      @keydown.enter="$emit('searchChecklistEmit', searchChecklist)"
      @focusout="$emit('searchChecklistEmit', searchChecklist)"
    />

    <v-text-field
      v-if="showCreate"
      label="Type text and press enter" variant="outlined"
      v-model="newChecklistName"
      @keydown.enter="newChecklist"
    />
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "checklistListFilterComponent",
  emits: ['newChecklistEmit', 'searchChecklistEmit'],
  props: {
    spaceId: String,
    showCreate: Boolean
  },
  data(){
    return{
      searchChecklist: undefined,
      newChecklistName: undefined
    }
  },
  methods:{
    newChecklist(){
      if(!this.newChecklistName) return;
      axios.post(`/api/v1/checklist/${this.spaceId}`, {
        title: this.newChecklistName
      }).then(res => {
        this.$emit('newChecklistEmit', res.data)
      })
    }
  }
}
</script>

<style scoped>

</style>
