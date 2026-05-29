<template>
  <aqa-report-suite-card-title-component :suite-item="suiteItem" />

  <v-expansion-panels>
    <v-expansion-panel title="Detail" @click="showSuiteTable">
      <v-expansion-panel-text>
        <aqa-report-suite-table-component
          v-if="itemsDetail"
          :suite-items="itemsDetail"
          @showModalMessageSuiteEmit="$emit('showModalMessageSuiteEmit', $event)"
        />
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import AqaReportSuiteCardTitleComponent from '@/components/reports/aqa-report/aqaReportSuite/aqaReportSuiteCardTitleComponent.vue'
import AqaReportSuiteTableComponent from '@/components/reports/aqa-report/aqaReportSuite/aqaReportSuiteTableComponent.vue'
import { reportService } from '@/services'

const route = useRoute()
const spaceId = route.params?.id

const props = defineProps({
  suiteItem: Object
})

defineEmits(['showModalMessageSuiteEmit'])

const itemsDetail = ref(undefined)

function showSuiteTable() {
  if (!itemsDetail.value) {
    reportService.getSuiteDetail(spaceId, props.suiteItem.id).then(res => {
      itemsDetail.value = res.data
    })
  }
}
</script>

<style scoped>
</style>
