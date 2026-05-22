<template>
  <v-dialog
    transition="dialog-top-transition"
    width="auto"
    :model-value="isActive"
    min-width="400"
    min-height="400"

    @update:modelValue="$emit('closeModal')"
  >
    <v-card>
      <v-toolbar title="Runs list">
        <v-btn :text="'Close'" @click="$emit('closeModal')"/>
      </v-toolbar>
      <v-list>
        <v-list-item
          v-for="elem in runsList"
          :key="elem.id"
          :title="elem.name"
          :to="`/space/${spaceId}/runs/${elem.id}`"
          />
      </v-list>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from "axios";

export default {
  name: "padsDetailRunsListModalComponent",
  emits: ['closeModal'],
  props: {
    isActive: Boolean,
    padId: String
  },
  data(){
    return {
      runsList: [],
      spaceId: this.$route.params.spaceId
    }
  },
  mounted() {
    this.getRuns()
  },
  methods:{
    getRuns(){
      axios.get(`/api/v1/runs/all/${this.padId}`).then(res => {
        this.runsList = res.data
      })
    }
  }
}
</script>

<style scoped>

</style>
