<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>

  <div v-else>
    <v-container fluid class="pb-0">
      <breadcrumbs-component :items="breadcrumbItems" />
      <v-row align="center">
        <v-col>
          <v-btn variant="text" prepend-icon="mdi-arrow-left" :to="`/space/${spaceId}/test-suites`" class="pl-0">
            Test Suites
          </v-btn>
          <h1 class="text-h4 font-weight-bold mt-1">{{ suite.name }}</h1>
          <p v-if="suite.description" class="text-body-1 text-medium-emphasis mt-1">{{ suite.description }}</p>
        </v-col>
        <v-col cols="auto">
          <v-btn color="primary" prepend-icon="mdi-play" @click="createRun">New Run</v-btn>
        </v-col>
      </v-row>
    </v-container>

    <!-- Stats -->
    <v-container fluid class="py-3">
      <v-row>
        <v-col v-for="stat in stats" :key="stat.label" cols="6" md="3">
          <v-card variant="outlined">
            <v-card-text class="d-flex align-center py-3">
              <v-icon size="32" :color="stat.color" class="mr-3">{{ stat.icon }}</v-icon>
              <div>
                <div class="text-h6 font-weight-bold">{{ stat.value }}</div>
                <div class="text-caption text-medium-emphasis">{{ stat.label }}</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Main Content -->
    <v-container fluid>
      <v-row>
        <v-col cols="12" md="3">
          <suite-sections-panel
            :flat-sections="flatSections"
            :selected-section="selectedSection"
            @select-section="onSectionSelect"
            @add-section="openSectionDialog()"
            @add-sub-section="openSectionDialog"
            @rename-section="openRenameDialog"
            @delete-section="deleteSection"
          />
        </v-col>
        <v-col cols="12" md="9">
          <suite-cases-panel
            :selected-section="selectedSection"
            :filtered-test-cases="filteredTestCases"
            :case-search="caseSearch"
            :open-add-case="openAddCase"
            :open-add-existing-case="openAddExistingCase"
            :existing-cases="existingCases"
            :selected-existing-cases="selectedExistingCases"
            :existing-case-search="existingCaseSearch"
            :new-case="newCase"
            :creating-case="creatingCase"
            :filtered-existing-cases="filteredExistingCases"
            @update:case-search="caseSearch = $event"
            @view-case="openCaseDialog"
            @remove-case="removeCaseFromSection"
            @update:open-add-case="openAddCase = $event"
            @open-add-new="openAddCase = true"
            @update:open-add-existing-case="openAddExistingCase = $event"
            @open-add-existing="openAddExistingCase = true; loadExistingCases()"
            @update:selected-existing-cases="selectedExistingCases = $event"
            @update:existing-case-search="existingCaseSearch = $event"
            @add-existing-cases="addExistingCases"
            @update:new-case="newCase = $event"
            @add-new-case="addTestCase"
          />
        </v-col>
      </v-row>
    </v-container>

    <section-dialog
      v-model="sectionDialog.open"
      :is-rename="sectionDialog.isRename"
      v-model:name="sectionDialog.name"
      v-model:description="sectionDialog.description"
      @save="saveSection"
    />

    <case-view-dialog v-model="caseDialogOpen" :test-case="selectedCase" @edit="caseDialogOpen = false" />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useTestSuiteDetail } from '@/composables/useTestSuiteDetail'
import BreadcrumbsComponent from '@/components/common/breadcrumbsComponent.vue'
import SuiteSectionsPanel from './SuiteSectionsPanel.vue'
import SuiteCasesPanel from './SuiteCasesPanel.vue'
import SectionDialog from './SectionDialog.vue'
import CaseViewDialog from '@/components/test-plans/detail/CaseViewDialog.vue'

const {
  spaceId,
  suite,
  flatSections,
  selectedSection,
  loader,
  caseSearch,
  openAddCase,
  openAddExistingCase,
  existingCases,
  selectedExistingCases,
  existingCaseSearch,
  newCase,
  creatingCase,
  sectionDialog,
  caseDialogOpen,
  selectedCase,
  breadcrumbItems,
  filteredTestCases,
  filteredExistingCases,
  allCases,
  onSectionSelect,
  openSectionDialog,
  openRenameDialog,
  saveSection,
  deleteSection,
  removeCaseFromSection,
  loadExistingCases,
  addExistingCases,
  addTestCase,
  openCaseDialog,
  createRun,
  caseCountByType,
  init,
} = useTestSuiteDetail()

const stats = computed(() => [
  { label: 'Total Cases', value: allCases.value.length, icon: 'mdi-test-tube', color: 'primary' },
  { label: 'Manual', value: caseCountByType('manual'), icon: 'mdi-hand-back-right-outline', color: 'info' },
  { label: 'Checklist', value: caseCountByType('checklist'), icon: 'mdi-check-box-outline', color: 'success' },
  { label: 'Automated', value: caseCountByType('automated'), icon: 'mdi-robot', color: 'warning' },
])

onMounted(() => init())
</script>

<style scoped>
.section-list-item {
  cursor: pointer;
}
.case-item {
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}
.case-item:last-child {
  border-bottom: none;
}
.tree-node-text {
  cursor: pointer;
  user-select: none;
}
.inline-rename-field {
  max-width: 180px;
  display: inline-block;
  vertical-align: middle;
}
</style>
