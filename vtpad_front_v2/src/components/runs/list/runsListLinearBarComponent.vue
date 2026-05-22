<template>
  <div class="d-flex align-center mx-auto">
    <v-progress-linear
      style="max-width: 93%"
      buffer-color="red"
      buffer-opacity="1"
      :buffer-value="fail+pass"
      color="green"
      height="6"
      :max=all
      min="0"
      :model-value="pass"
      rounded
    ></v-progress-linear>
    <div class="ms-4 ">{{pass}}/{{all}}</div>
  </div>
</template>

<script>
export default {
  name: "runsListLinearBarComponent",
  props:{
    pass: Number,
    fail: Number,
    all: Number
  }
}
</script>

<style scoped>

</style>
