<template>
  <div>
    <p>Created bugs: {{bugStatistic.count}}</p>
    <p v-for="(item, i) in bugStatistic.state" :key="i">{{item.state}}: {{item.item_count}}</p>
  </div>
</template>

<script>
export default {
  name: "statisticPageBugsComponent",
  props:{
    bugStatistic:{
      "count": Number,
      state: Array
    }
  }
}
</script>

<style scoped>

</style>
