<template>
  <v-list-item>
    <template v-slot:prepend >
      <v-icon icon="mdi-note"></v-icon>
    </template>
    <v-list-item-title
      contenteditable="true"
      class="no-white-space is-empty"
      @keydown.enter="createPad($event)"
      data-placeholder="Create…"
      @focusin="createPadFocusIn($event)"
      @focusout="createPadFocusOut($event)"
    />
  </v-list-item>
</template>

<script>
import axios from "axios";

export default {
  name: "padsListCreateItemComponent",
  emits: ['createPadEmit'],
  props: {
    folderId: String,
    spaceId: String
  },
  methods:{
    createPad(event){
      axios.post(`/api/v1/pad/${this.spaceId}`,{
        name: event.target.innerText,
        folder_id: this.folderId
      }).then(res => {
        this.$emit('createPadEmit', res.data)
        event.target.innerText = ''
      })
    },
    createPadFocusIn(event){
      event.target.classList.remove('is-empty')
    },
    createPadFocusOut(event){
      if(!event.target.innerText) {
        event.target.classList.add('is-empty')
      }else{
        event.target.classList.remove('is-empty')
      }
    }
  }
}
</script>

<style scoped>

</style>
