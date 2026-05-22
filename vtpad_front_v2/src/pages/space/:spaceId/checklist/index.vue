<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <checklist-component />
  </v-container>
</template>

<script>
import ChecklistComponent from "@/components/checklist/checklistComponent.vue";

export default {
  name: "CheckListPage",
  components: {ChecklistComponent}
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
