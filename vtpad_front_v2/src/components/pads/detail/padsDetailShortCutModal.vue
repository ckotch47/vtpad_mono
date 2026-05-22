<template>
  <v-dialog
    transition="dialog-top-transition"
    width="auto"
    :model-value="isActive"
    min-width="400"
    min-height="600"

    @update:modelValue="$emit('closeModal')"
  >
    <v-card>
      <v-toolbar title="Shortcut">
        <v-btn :text="'Close'" @click="$emit('closeModal')"/>
      </v-toolbar>
      <h4>Windows / Linux</h4>
      <v-list>
        <v-list-item title="ctrl+enter => new sub item"/>
        <v-list-item title="alt+enter => new item"/>
        <v-list-item title="ctrl+delete => delete item"/>
        <v-list-item title="ctrl+shift+left => up item"/>
        <v-list-item title="ctrl+shift+right => down item"/>
      </v-list>
      <h4>MacOs</h4>
      <v-list>
        <v-list-item title="ctrl+enter => new sub item"/>
        <v-list-item title="option+enter => new item"/>
        <v-list-item title="ctrl+delete => delete item"/>
        <v-list-item title="ctrl+shift+left => up item"/>
        <v-list-item title="ctrl+shift+right => down item"/>
      </v-list>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: "padsDetailShortCutModal",
  emits: ['closeModal'],
  props: {
    isActive: Boolean,
  },
}
</script>

<style scoped>

</style>
