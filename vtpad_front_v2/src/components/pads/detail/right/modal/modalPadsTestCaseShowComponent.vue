<template>
  <v-dialog
    width="auto"
    :model-value="isActive"
    min-width="732"
    min-height="400"
    max-width="732"
    @update:modelValue="$emit('closeModalTestCaseShowPadEmit')"
  >
    <v-card>
      <cases-detail-component :short-name="item.short_name" :style-object="{'margin': 0}"/>
    </v-card>
  </v-dialog>
</template>

<script>
import CasesDetailComponent from "@/components/cases/detail/casesDetailComponent.vue";

export default {
  name: "modalPadsTestCaseShowComponent",
  components: {CasesDetailComponent},
  props: {
    isActive: Boolean,
    item: Object
  },
  emits: ['closeModalTestCaseShowPadEmit']
}
</script>

<style scoped>

</style>
