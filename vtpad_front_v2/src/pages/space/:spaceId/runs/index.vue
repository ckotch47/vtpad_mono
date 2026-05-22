<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <runs-list-component />
  </v-container>
</template>

<script>
import RunsListComponent from "@/components/runs/list/runsListComponent.vue";

export default {
  name: "runsPage",
  components: {RunsListComponent}
}
</script>
<route lang="json">
{
"meta": {
"layout": "spaces",
"tabValue": "runs"
}
}
</route>
<style scoped>

</style>
