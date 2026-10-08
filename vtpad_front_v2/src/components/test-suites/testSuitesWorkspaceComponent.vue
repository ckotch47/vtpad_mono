<template>
  <v-container fluid class="suite-workspace custom-container max-width-1500">
    <page-header-component title="Test Suites" />
    <v-row class="suite-workspace__row" no-gutters>
      <v-col
        cols="12"
        md="3"
        class="suite-workspace__list-column"
        :class="{ 'suite-workspace__mobile-hidden': selectedSuiteId }"
      >
        <v-card variant="outlined" class="suite-workspace__list-card">
          <div class="suite-workspace__panel-heading">
            <div>
              <div class="text-subtitle-1 font-weight-medium">Suites</div>
              <div class="text-caption text-medium-emphasis">Browse and organize test suites</div>
            </div>
            <v-icon color="primary">mdi-folder-multiple-outline</v-icon>
          </div>
          <test-suites-list-component @suite-changed="refreshDetail" />
        </v-card>
      </v-col>

      <v-col
        cols="12"
        md="9"
        class="suite-workspace__detail-column"
        :class="{ 'suite-workspace__mobile-hidden': !selectedSuiteId }"
      >
        <test-suite-detail-component
          v-if="selectedSuiteId"
          :key="`${selectedSuiteId}:${detailRevision}`"
        />
        <v-card v-else variant="outlined" class="suite-workspace__placeholder">
          <v-empty-state
            icon="mdi-folder-open-outline"
            title="Select a test suite"
            text="Choose a suite from the list to view its sections, cases, and runs."
          />
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import TestSuitesListComponent from './testSuitesListComponent.vue'
import TestSuiteDetailComponent from './detail/testSuiteDetailComponent.vue'

const route = useRoute()
const selectedSuiteId = computed(() => route.params.suiteId || '')
const detailRevision = ref(0)

function refreshDetail() {
  if (selectedSuiteId.value) detailRevision.value += 1
}
</script>

<style scoped>
.suite-workspace__row {
  gap: 16px;
  flex-wrap: nowrap;
  align-items: stretch;
}

.suite-workspace__list-column {
  flex: 0 0 320px;
  width: 320px;
  min-width: 0;
  max-width: 340px;
}

.suite-workspace__detail-column {
  flex: 1 1 0;
  width: auto;
  min-width: 0;
}

.suite-workspace__list-card {
  display: flex;
  flex-direction: column;
  height: min(78vh, 900px);
  min-height: 500px;
  overflow: hidden;
}

.suite-workspace__panel-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px 10px;
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.suite-workspace__placeholder {
  min-height: min(78vh, 900px);
  display: grid;
  place-items: center;
}

@media (max-width: 959.98px) {
  .suite-workspace__row {
    display: block;
  }

  .suite-workspace__list-column,
  .suite-workspace__detail-column {
    flex: initial;
    max-width: none;
    width: 100%;
  }

  .suite-workspace__list-card {
    height: calc(100dvh - 230px);
    min-height: 360px;
  }

  .suite-workspace__placeholder {
    min-height: 55vh;
  }

  .suite-workspace__mobile-hidden {
    display: none;
  }
}
</style>
