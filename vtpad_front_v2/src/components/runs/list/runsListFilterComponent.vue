<template>
  <v-card class="d-flex pa-8">
    <v-select
      class=""
      label="Pad"
      :items="selectItem"
      item-value="id"
      item-title="name"
      variant="outlined"
      v-model="itemPad"
      @update:modelValue="$emit('changeFilterEmit', itemPad, itemCount)"
      style="margin-right: 16px"
    ></v-select>

    <v-select
      class=""
      label=""
      :items="['5', '10', '25', '50', '100']"
      v-model="itemCount"
      variant="outlined"
      max-width="200px"
      @update:modelValue="$emit('changeFilterEmit', itemPad, itemCount)"
    ></v-select>

  </v-card>
</template>

<script>
export default {
  name: "runsListFilterComponent",
  emits: ['changeFilterEmit'],
  props: {
    selectItem: undefined
  },
  data(){
    return{
      itemCount: 5,
      itemPad: undefined
    }
  }
}
</script>

<style scoped lang="scss">

</style>
