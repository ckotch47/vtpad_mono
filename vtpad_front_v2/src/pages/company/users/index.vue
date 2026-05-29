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
<script setup>
import CompanyUserListComponent from '@/components/company/list/companyUserListComponent.vue'
</script>
