<template>
  <v-card v-for="item in listSuite" :key="item.id" class="suites-card my-8">
    <v-card-item>
      <aqa-report-suite-card-component :suite-item="item" @showModalMessageSuiteEmit="showAqaErrorMessageModal" />
    </v-card-item>
  </v-card>

  <v-dialog v-model="isActiveAqaError" max-width="1500px" @close="isActiveAqaError = false">
    <v-card>
      <v-toolbar title="Error">
        <v-btn text="Close" @click="isActiveAqaError = false" />
      </v-toolbar>
      <div class="pa-8">
        {{ message }}
      </div>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref } from 'vue'
import AqaReportSuiteCardComponent from '@/components/reports/aqa-report/aqaReportSuite/aqaReportSuiteCardComponent.vue'

defineProps({
  listSuite: Array
})

const isActiveAqaError = ref(false)
const message = ref(undefined)

function showAqaErrorMessageModal(event) {
  message.value = event
  isActiveAqaError.value = true
}
</script>

<style scoped lang="scss">
.suites-card {
  .v-card-item {
    padding: 0;
  }
}
</style>
