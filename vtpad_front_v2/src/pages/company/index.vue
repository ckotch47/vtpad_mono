<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <company-main-component />
  </v-container>
</template>
<route lang="json">
{
"meta": {
"layout": "company",
"tabValue": "info"
}
}
</route>
<script>

import CompanyMainComponent from "@/components/company/companyMainComponent.vue";

export default {
  name: "indexCompanyPage",
  components: {CompanyMainComponent},
}
</script>

<style scoped>

</style>
