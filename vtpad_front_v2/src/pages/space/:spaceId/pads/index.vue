<template>
  <v-container class="mx-auto custom-container max-width-1500">
  <pads-list-component />
  </v-container>
</template>

<script>
import PadsListComponent from "@/components/pads/padsListComponent.vue";

export default {
  name: "padsPage",
  components: {PadsListComponent}
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
