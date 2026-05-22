<template>
  <div>
    <p>Created pads: {{padsStatistic.count}}</p>
    <p>Items into pads: {{padsStatistic.items_count}}</p>
  </div>
</template>

<script>
export default {
  name: "statisticPagePadComponent",
  props:{
    padsStatistic:{
      count: Number,
      items_count: Number
    }
  }
}
</script>

<style scoped>

</style>
