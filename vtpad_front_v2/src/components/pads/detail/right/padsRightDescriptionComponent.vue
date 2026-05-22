<template>
  <v-expansion-panels >
    <v-expansion-panel >
      <v-expansion-panel-title>
        <div class="d-flex justify-space-between align-center w-100">
          <p>Description:</p>

        </div>
      </v-expansion-panel-title>
      <v-expansion-panel-text class="no-padding-important">
        <editor-component

          :edit="edit"
          :placeHolderEditor="'Text…'"
          :text="text ?? ''"
          :show-menu-fixed="edit"
          :show-menu-floating="false"
          :show-menu-bubble="false"
          :menu-position="'top'"
          is-save
          min-height="340px"
          max-height="340px"
        />

      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script>
import EditorComponent from "@/components/common/editor/editorComponent.vue";

export default {
  name: "padsRightDescriptionComponent",
  components: {EditorComponent},
  props: {
    edit: Boolean,
    text: String
  },
  emits: ['SaveDescriptionPadEmit']
}
</script>

<style scoped>

</style>
