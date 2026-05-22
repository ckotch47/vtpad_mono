<template>
  <div class="d-flex list-item">
    <v-list-item
      class="w-97"
      v-bind="props"
      @click="$emit('openFolderEmit', id)"
      prepend-icon="mdi-folder"
      append-icon=""
      :title="title"
    >
    </v-list-item>

    <div class="list-item--icon d-flex flex-column justify-center">
      <v-icon icon="mdi-cog" @click="$emit('openFolderModal')"></v-icon>
    </div>
  </div>
</template>

<script>


export default {
  name: "padsListFolderComponent",
  emits: [
    'openFolderEmit',
    'openFolderModal',
    'openFolder'
  ],
  props:{
    props: undefined,
    title: String,
    id: String,
    spaceId: String
  },
  methods:{

  }
}
</script>

<style scoped lang="scss">

</style>
