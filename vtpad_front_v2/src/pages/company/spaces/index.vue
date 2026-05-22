<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <company-spaces-list />
  </v-container>
</template>
<route lang="json">
{
"meta": {
"layout": "company",
"tabValue": "spaces"
}
}
</route>
<script>
import CompanySpacesList from "@/components/company/spaces/companySpacesList.vue";

export default {
  name: "companySpacesPage",
  components: {CompanySpacesList}
}
</script>

<style scoped>

</style>
