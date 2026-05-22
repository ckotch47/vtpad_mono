<template>
  <v-list class="checklist-list">
    <v-list-item
      v-for="item in items"
      :key="item.id"
      :title="item.title"
      :value="item.id"
      @click="$emit('openChecklistEmit', item.id, item)"
    >
      <template v-slot:prepend >

        <div class="checklist-list--short_name">{{item.short_name}}</div>
      </template>

    </v-list-item>
  </v-list>
</template>

<script>
export default {
  name: "checklistListLeftComponent",
  emits: ['openChecklistEmit'],
  props:{
    items: Array
  },
  data(){
    return{

    }
  }
}
</script>

<style lang="scss">
.checklist-list{
  width: 100%;
  margin-right: 16px;
  overflow-y: scroll;
  max-height: 732px;
&--short_name{
   margin-right: 8px;
   color: rgb(var(--v-theme-primary));
 }
}
</style>
