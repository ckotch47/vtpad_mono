<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>

  <div v-else>
    <v-container fluid class="pb-0">
      <v-row align="center">
        <v-col>
          <v-btn
            variant="text"
            prepend-icon="mdi-arrow-left"
            :to="`/space/${spaceId}/test-plans`"
            class="pl-0"
          >
            Test Plans
          </v-btn>
          <h1 class="text-h4 font-weight-bold mt-1">{{ plan.name }}</h1>
          <p v-if="plan.description" class="text-body-1 text-medium-emphasis mt-1">
            {{ plan.description }}
          </p>
        </v-col>
        <v-col cols="auto">
          <v-btn color="primary" prepend-icon="mdi-play" :disabled="cases.length === 0" @click="createRun">
            New Run
          </v-btn>
        </v-col>
      </v-row>
    </v-container>

    <v-container fluid>
      <v-row>
        <v-col cols="12" md="8">
          <plan-cases-list
            :cases="cases"
            :removable-ids="plan.case_ids || []"
            @view-case="openCaseDialog"
            @remove-case="removeCase"
          />
        </v-col>
        <v-col cols="12" md="4">
          <plan-sources-panel
            :plan="plan"
            :all-suites="allSuites"
            v-model:edit-suite-ids="editSuiteIds"
            :saving-suites="savingSuites"
            :suite-ids-changed="suiteIdsChanged"
            :loading-cases="loadingCases"
            :cases-has-more="casesHasMore"
            v-model:selected-cases="selectedCases"
            v-model:case-search="caseSearch"
            :saving-cases="savingCases"
            :filtered-available-cases="filteredAvailableCases"
            :runs="runs"
            :is-case-in-plan="isCaseInPlan"
            @save-suites="saveSuites"
            @reset-suites="resetSuiteIds"
            @add-cases="addIndividualCases"
            @select-all-available="selectAllAvailable"
            @deselect-all="deselectAll"
            @load-more-cases="loadMoreCases"
          />
        </v-col>
      </v-row>
    </v-container>

    <case-view-dialog v-model="caseDialogOpen" :test-case="selectedCase" @edit="caseDialogOpen = false" />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useTestPlanDetail } from '@/composables/useTestPlanDetail'
import PlanCasesList from './PlanCasesList.vue'
import PlanSourcesPanel from './PlanSourcesPanel.vue'
import CaseViewDialog from './CaseViewDialog.vue'

const {
  spaceId,
  plan,
  cases,
  runs,
  loader,
  allSuites,
  editSuiteIds,
  savingSuites,
  suiteIdsChanged,
  loadingCases,
  casesHasMore,
  selectedCases,
  caseSearch,
  savingCases,
  filteredAvailableCases,
  caseMap,
  caseDialogOpen,
  selectedCase,
  saveSuites,
  resetSuiteIds,
  loadMoreCases,
  removeCase,
  isCaseInPlan,
  addIndividualCases,
  selectAllAvailable,
  deselectAll,
  createRun,
  openCaseDialog,
  init,
} = useTestPlanDetail()

onMounted(init)
</script>
