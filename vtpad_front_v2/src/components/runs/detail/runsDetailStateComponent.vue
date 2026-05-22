<template>
  <span v-if="state === 'pass'">🟢</span>
  <span v-else-if="state === 'fail'">🔴</span>
  <span v-else-if="state === 'skip'">🟠</span>
  <span v-else></span>
</template>

<script>
export default {
  name: "runsDetailStateComponent",
  props:{
    state: String
  }
}
</script>

<style scoped>

</style>
