<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <checklist-detail-component :short-name="shortName" />
  </v-container>
</template>

<script>
import ChecklistDetailComponent from "@/components/checklist/detail/checklistDetailComponent.vue";

export default {
  name: "CheckListDetail",
  components: {ChecklistDetailComponent},
  data(){
    return {
      isActive: true,
      shortName: this.$route.params.listId ?? undefined,
    }
  },
  mounted() {
    console.log()
  }
}
</script>

<style scoped>

</style>
