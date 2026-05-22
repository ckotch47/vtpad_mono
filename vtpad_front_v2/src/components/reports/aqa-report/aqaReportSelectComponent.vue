<template>
<v-card>
  <v-card-item>
    <v-autocomplete
      :items="testList"
      item-title="name"
      item-value="id"
      :label="'Report'"
      variant="underlined"
      @update:modelValue="$emit('selectTestLstEmit', $event)"
    />
  </v-card-item>
</v-card>
</template>

<script>
export default {
  name: "aqaReportSelectComponent",
  emits: ['selectTestLstEmit'],
  props: {
    testList: Array
  },
  data(){
    return{
      items: ['test 01-04-29', 'november 09-23']
    }
  }
}
</script>

<style scoped>

</style>
