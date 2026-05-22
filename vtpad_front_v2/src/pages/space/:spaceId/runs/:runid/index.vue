<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <runs-detail-component />
  </v-container>
</template>

<script>
import RunsDetailComponent from "@/components/runs/detail/runsDetailComponent.vue";

export default {
  name: "runsDetailPage",
  components: {RunsDetailComponent}
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
