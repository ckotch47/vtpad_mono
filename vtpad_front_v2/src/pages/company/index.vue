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
<script setup>
import CompanyMainComponent from '@/components/company/companyMainComponent.vue'
</script>
