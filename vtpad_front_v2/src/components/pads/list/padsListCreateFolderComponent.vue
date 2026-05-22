<template>
  <v-list-item >
    <template v-slot:prepend >
      <v-icon icon="mdi-folder"></v-icon>
    </template>
    <v-list-item-title
      contenteditable="true"
      class="no-white-space is-empty"
      @keydown.enter="createPadFolder($event)"
      data-placeholder="Create…"
      @focusin="createPadFolderFocusIn($event)"
      @focusout="createPadFolderFocusOut($event)"

    />
  </v-list-item>
</template>

<script>
import axios from "axios";

export default {
  name: "padsListCreateFolderComponent",
  emits: ['createFolderEmit'],
  props:{
    spaceId: String
  },
  methods:{

    pasteAsPlainText(event) {
      event.preventDefault();
      event.target.innerText = event.clipboardData.getData("text/plain");
    },
    createPadFolder(event){
      axios.post(`/api/v1/pad-folder/${this.spaceId}`,{
        name: event.target.innerText,
        main_id: null
      }).then(res => {
        this.$emit('createFolderEmit', res.data)
        event.target.innerText = ''
      })
    },
    createPadFolderFocusIn(event){
      event.target.classList.remove('is-empty')
    },
    createPadFolderFocusOut(event){
      if(!event.target.innerText)
        event.target.classList.add('is-empty')
      else
        event.target.classList.remove('is-empty')
    }
  }
}
</script>

<style lang="scss">

</style>
