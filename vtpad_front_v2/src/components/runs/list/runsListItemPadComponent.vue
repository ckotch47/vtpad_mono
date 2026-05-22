<template>
  <h3>{{pad.pad_name}}</h3>
  <v-card-item
    v-for="item in pad.run"
    :key="item.id"
  >
    <router-link :to="`runs/${item.id}`" class="router--link">{{item.name}}</router-link>
    <runs-list-linear-bar-component
      v-if="item.items_count.pass > -1"
      :pass="item.items_count.pass"
      :fail="item.items_count.fail"
      :all="item.items_count.all"
    />

    <runs-list-linear-bar-component
      v-if="item.items_count.passed > -1"
      :pass="item.items_count.passed"
      :fail="item.items_count.failed"
      :all="item.items_count.all"
    />
  </v-card-item>
</template>

<script>
import RunsListLinearBarComponent from "@/components/runs/list/runsListLinearBarComponent.vue";

export default {
  name: "runsListItemPadComponent",
  components: {RunsListLinearBarComponent},
  props:{
    pad: Object
  }
}
</script>

<style scoped>

</style>
