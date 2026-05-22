<template>
<v-container class="max-width-1500  ">
  <v-empty-state
    headline="Whoops, 404"
    title="Page not found"
  >
    <div class="text-center">
    <p>The page you were looking for does not exist</p>
    <p><a href="/space">Click…</a> return Home</p>
    </div>
  </v-empty-state>
</v-container>
</template>

<script>
export default {
  name: "404Page"
}
</script>

<style scoped>

</style>
