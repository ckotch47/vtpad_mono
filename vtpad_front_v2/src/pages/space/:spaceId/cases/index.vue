<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <cases-component />
  </v-container>
</template>

<script>
import CasesComponent from "@/components/cases/casesComponent.vue";

export default {
  name: "casesPage",
  components: {CasesComponent}
}
</script>
<route lang="json">
{
"meta": {
"layout": "spaces",
"tabValue": "cases"
}
}
</route>
<style scoped>

</style>
