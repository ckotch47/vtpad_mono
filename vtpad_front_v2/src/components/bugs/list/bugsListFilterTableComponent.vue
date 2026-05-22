<template>
  <div :class="!display ? 'bugs-filter--d_none' : 'bugs-filter--d'">
    <v-select
      class="bugs-filter--d_select"
      :label="title"
      :items="item"
      item-value="id"
      item-title="title"
      variant="underlined"
      :multiple="multi"
      style=""
      v-model="select"
      @update:modelValue="someChange"
    ></v-select>
    <span v-if="!display"  class="text-primary">{{title}}</span>

  </div>
</template>

<script>
export default {
  name: "bugsListFilterTableComponent",
  props:{
    title: String,
    item: Object,
    multi: Boolean,
    link: Boolean,
    selectArray: Array,
    display: Boolean
  },
  // watch:{
  //   selectArray: {
  //     handler() {
  //       console.log(this.selectArray)
  //       this.select = this.selectArray;
  //     },
  //     deep: true
  //   },
  // },
  updated() {
    this.select = this.selectArray;
  },
  data(){
    return{
      select: undefined
    }
  },
  methods:{
    someChange(){
      this.$emit('changeFilter', this.select);
    }
  }
}
</script>

<style lang="scss" >
.text-primary{
  color: rgb(var(--v-theme-primary));
}
.bugs-filter {
  &--d_none {
    position: relative;
    display: inline-block;
    cursor: pointer
  }
  &--d_select{

  }
}
.bugs-filter--d_none{
  .bugs-filter--d_select{
    opacity:0;
    position:absolute;
    left:0;top:0;width:100%
  }
}
</style>
