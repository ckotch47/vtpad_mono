<template>
  <report-qa-filter-component :statistic="listItems.count" @selectFilterEmit="selectFilter" />
  <v-card v-if="currentFilter && listItems.count" class="my-4 pa-4 d-flex justify-end">
    <qa-report-email-dialog :filter="currentFilter" />
  </v-card>
  <report-qa-list-component title="Created" :data-list="listItems.opened" />
  <report-qa-list-component title="Updated" :data-list="listItems.updated" />
</template>

<script setup>
import { ref } from 'vue'
import ReportQaFilterComponent from '@/components/reports/qa-report/reportQaFilterComponent.vue'
import ReportQaListComponent from '@/components/reports/qa-report/reportQaListComponent.vue'
import QaReportEmailDialog from '@/components/reports/qa-report/qaReportEmailDialog.vue'
import { qaReportService } from '@/services'

const listItems = ref({
  count: undefined,
  opened: [],
  updated: []
})
const currentFilter = ref(null)

function selectFilter(data) {
  currentFilter.value = data
  listItems.value = { count: undefined, opened: [], updated: [] }
  qaReportService.getBugList(data).then(res => {
    listItems.value = res.data
  })
}
</script>
