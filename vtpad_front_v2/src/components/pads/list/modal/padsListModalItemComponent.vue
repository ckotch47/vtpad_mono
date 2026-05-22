<template>
  <v-dialog
    transition="dialog-top-transition"
    width="auto"
    :model-value="isActive"
    min-width="600"
    min-height="400"
    @close="$emit('closeItemModal')"
  >

    <v-card >
      <v-toolbar :title="pad.name"><v-btn
        text="Close"
        @click="$emit('closeItemModal')"
      />
      </v-toolbar>

      <div class="pa-8">
        <v-text-field
          class="custom-text--input"
          label="Name"
          variant="outlined"
          placeholder="Name"
          :model-value="pad.name"
          v-model="padName"
        />
        <v-select
          class=""
          label="Folder"
          :items="foldersList"
          item-title="name"
          item-value="id"
          :model-value="folderPad"
          variant="underlined"
          v-model="folderPad"
          style="width:100%"
        ></v-select>

        <div class="d-flex justify-space-between">
          <v-btn
            text="Delete"
            color="red"
            @click="deletePad"
          />
          <div>

            <v-btn
              text="Save"
              color="primary"
              @click="savePad"
            />
          </div>
        </div>
      </div>
    </v-card>
  </v-dialog>
</template>

<script>


import axios from "axios";

export default {
  name: "padsListModalItemComponent",
  emits:  ['saveItemModalEmit',  'deleteItemModalEmit'],
  props:{
    isActive: Boolean,
    name: String,
    folder: Array,
    pad: Object
  },
  data(){
    return{
      folderPad: this.pad.folder_id,
      padName: this.pad.name,
      foldersList: [...[{
        "id": 'none',
        "name": "Root",
      }], ...this.folder]
    }
  },
  mounted() {
  },
  methods:{
    savePad(){
      axios.patch(`/api/v1/pad/${this.pad.id}`, {
        name: this.padName,
        folder_id: this.folderPad
      }).then(res => {
        this.$emit('saveItemModalEmit', this.pad.folder_id, this.folderPad)
      })
    },
    deletePad(){
      axios.delete(`/api/v1/pad/${this.pad.id}`)
        .then(this.$emit('deleteItemModalEmit', this.pad.id, this.pad.folder_id))
    }
  }
}
</script>

<style scoped>

</style>
