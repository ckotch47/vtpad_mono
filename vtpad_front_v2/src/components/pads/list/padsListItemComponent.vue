<template>
  <div class="d-flex list-item">
    <v-list-item
      class="w-97"
      :value="value"
      :to="`pads/${id}`"
      :title="name"
      prepend-icon="mdi-note"
    />

    <div class="list-item--icon d-flex flex-column justify-center">
      <v-icon icon="mdi-cog" @click="openModal()"></v-icon>
    </div>
  </div>
</template>

<script>
export default {
  name: "padsListItemComponent",
  props: {
    item: Object,
    id: String,
    name: String,
    value: String,
    folderId: String
  },
  methods:{
    openModal(){
      this.$emit('openItemModal', this.id)
    }
  }

}
</script>

<style scoped lang="scss">
.router--link{
  width: 100%;
  display: block;
}
</style>
