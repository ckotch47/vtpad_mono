<template>

  <v-list class="cases-list">
    <v-list-item
    v-for="item in items"
    :key="item.id"
    :title="item.title"
    :value="item.id"
    @click="$emit('openCaseEmit', item.id, item)"
    >
      <template v-slot:prepend >
        <div class="cases-list--short_name">{{item.short_name}}</div>
      </template>

    </v-list-item>
  </v-list>
</template>

<script>
export default {
  name: "caseListRightComponent",
  props:{
    items: Array
  },
  emits: ['openCaseEmit'],
  data(){
    return{
    }
  }
}
</script>

<style lang="scss">
.cases-list{
  width: 100%;
  margin-right: 16px;
  overflow-y: scroll;
  max-height: 866px;
  &--short_name{
    margin-right: 8px;
    color: rgb(var(--v-theme-primary));
  }
}
</style>
