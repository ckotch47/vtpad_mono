<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <pads-detail-component />
  </v-container>
</template>

<script>
import PadsDetailComponent from "@/components/pads/detail/padsDetailComponent.vue";

export default {
  name: "padsDetailPage",
  components: {PadsDetailComponent}
}
</script>
<route lang="json">
{
"meta": {
"layout": "spaces",
"tabValue": "pads"
}
}
</route>
<style scoped>

</style>
