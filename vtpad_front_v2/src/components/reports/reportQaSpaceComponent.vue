<template>
  <report-qa-filter-component :statistic="listItems.count" @selectFilterEmit="selectFilter" />
  <report-qa-list-component title="Created" :data-list="listItems.opened" />
  <report-qa-list-component title="Updated" :data-list="listItems.updated" />
</template>

<script setup>
import { ref } from 'vue'
import ReportQaFilterComponent from '@/components/reports/qa-report/reportQaFilterComponent.vue'
import ReportQaListComponent from '@/components/reports/qa-report/reportQaListComponent.vue'
import { qaReportService } from '@/services'

const listItems = ref({
  count: undefined,
  opened: [],
  updated: []
})

function selectFilter(data) {
  qaReportService.getBugList(data).then(res => {
    listItems.value = res.data
  })
}
</script>
