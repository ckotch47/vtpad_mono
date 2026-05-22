<template>
  <editor-component
    class="ma-2"
    :edit="true"
    :placeHolderEditor="'Text…'"

    :show-menu-fixed="true"
    :show-menu-floating="false"
    :show-menu-bubble="false"
    :menu-position="'top'"
    is-save
    max-height="300px"
  />

  <v-timeline density="compact" side="end">

    <v-timeline-item


      dot-color="primary"
      size="small"
    >
      <v-alert>
        <div class="d-flex justify-space-between flex-grow-1">
          <div>
            @blant<br>
            <div > some text comment</div>
          </div>
          <div class="flex-shrink-0">
            <v-icon icon="mdi-pencil" size="14" />
            2024-10-10 21:03
          </div>
        </div>
      </v-alert>
    </v-timeline-item>

  </v-timeline>
</template>

<script>
import EditorComponent from "@/components/common/editor/editorComponent.vue";

export default {
  name: "padsRightCommentComponent",
  components: {EditorComponent}
}
</script>

<style scoped>

</style>
