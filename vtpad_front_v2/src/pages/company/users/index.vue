<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <company-user-list-component />
  </v-container>
</template>

<route lang="json">
{
"meta": {
"layout": "company",
"tabValue": "users"
}
}
</route>
<script>
import CompanyUserListComponent from "@/components/company/list/companyUserListComponent.vue";

export default {
  name: "companyUsersPage",
  components: {CompanyUserListComponent}
}
</script>

<style scoped>

</style>
