<template>
  <v-dialog
    transition="dialog-top-transition"
    width="auto"
    :model-value="isActive"
    min-width="600"
    min-height="400"
    @close="$emit('closeFolderModal')"
  >

    <v-card >
      <v-toolbar :title="folder.name">
        <v-btn
          text="Close"
          @click="$emit('closeFolderModal')"
        ></v-btn>
      </v-toolbar>

      <div class="pa-8">
        <v-text-field
          class="custom-text--input"
          label="Name"
          variant="outlined"
          placeholder="Name"
          :model-value="folderName"
          v-model="folderName"
        ></v-text-field>

        <div class="d-flex justify-space-between">
          <v-btn
            text="Delete"
            color="red"
            @click="deleteFolder"
          ></v-btn>
          <div >

          <v-btn
            text="Save"
            color="primary"
            @click="saveFolder"
          ></v-btn>
          </div>
        </div>
      </div>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from "axios";

export default {
  name: "padsListModalFolderComponent",
  props:{
    isActive: Boolean,
    folder: Object,
  },
  emits: ['updateFolderEmit', 'deleteFolderEmit'],
  data(){
    return{
      folderName: undefined,
      folderItem: undefined
    }
  },
  mounted() {
    this.folderName = this.folder.name
    this.folderItem = this.folder
  },
  methods:{
    saveFolder(){
      axios.patch(`/api/v1/pad-folder/${this.folder.id}`,{
        name: this.folderName
      }).then(res => {
        this.folderItem = res.data
        this.$emit('updateFolderEmit', res.data)
      })
    },
    deleteFolder(){
      axios.delete(`/api/v1/pad-folder/${this.folder.id}`).then(this.$emit('deleteFolderEmit', this.folder))
    }
  }
}
</script>

<style scoped>

</style>
