<template>
  <div>
    <p>Created runs: {{runStatistic.count}}</p>
    <p v-for="(item, i) in runStatistic.state" :key="i">{{item.state ?? 'not status'}}: {{item.item_count}}</p>
  </div>
</template>

<script>
export default {
  name: "statisticPageRunComponent",
  props:{
    runStatistic:{
      count: Number,
      state: Array
    }
  }
}
</script>

<style scoped>

</style>
