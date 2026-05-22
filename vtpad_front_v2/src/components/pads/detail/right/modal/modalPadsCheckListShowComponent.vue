<template>
  <v-dialog
    width="auto"
    :model-value="isActive"
    min-width="732"
    min-height="400"
    max-width="732"
    @update:modelValue="$emit('closeModalCheckListShowPadEmit')"
  >
    <v-card>
      <checklist-detail-component :short-name="item.short_name" :style-object="{'margin': 0}" />
    </v-card>
  </v-dialog>
</template>

<script>
import ChecklistDetailComponent from "@/components/checklist/detail/checklistDetailComponent.vue";

export default {
  name: "modalPadsCheckListShowComponent",
  components: {ChecklistDetailComponent},
  emits: ['closeModalCheckListShowPadEmit'],
  props: {
    isActive: Boolean,
    item: Object
  }
}
</script>

<style scoped>

</style>
