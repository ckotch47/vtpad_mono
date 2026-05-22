<template>
  <v-select
    label="State"
    :items="['pass', 'fail', 'skip']"

    v-model="stateItem"
    @update:modelValue="updateState"
  ></v-select>

</template>

<script>
import {useAppStore} from "@/stores/app";
export default {
  props: {
    state: String
  },
  emits: ['updateStateRunItemEmit'],
  name: "rightRunDetailStateComponent",
  data: () => ({
    store: useAppStore(),
    stateItem: undefined,
    item: undefined
  }),
  mounted() {
    this.stateItem = this.state
  },
  watch: {
    'store.getOpenRunItem'(newValue){
      this.stateItem = newValue.state
      this.item = newValue
    }
  },
  methods:{
    updateState(event){
      if(this.item){
        this.$emit('updateStateRunItemEmit', event, this.item.state, this.item.id);
        this.store.openRunItem.state = event
      }
      // console.log(event, this.item.id)
    }
  }
}
</script>

<style scoped>

</style>
