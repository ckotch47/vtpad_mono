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
          <v-btn color="primary" prepend-icon="mdi-play" @click="createRun" :disabled="cases.length === 0">
            New Run
          </v-btn>
        </v-col>
      </v-row>
    </v-container>

    <v-container fluid>
      <v-row>
        <!-- Selected Cases -->
        <v-col cols="12" md="8">
          <v-card>
            <v-card-title class="d-flex align-center">
              <span>Cases in Plan</span>
              <v-spacer />
              <v-chip size="small" color="primary">{{ cases.length }}</v-chip>
            </v-card-title>
            <v-divider />
            <v-card-text class="pa-0">
              <v-list density="compact">
                <v-list-item
                  v-for="tc in cases"
                  :key="tc.id"
                  class="case-item"
                  @click="openCaseDialog(tc.id)"
                >
                  <template v-slot:prepend>
                    <v-icon :color="typeColor(tc.type)">{{ typeIcon(tc.type) }}</v-icon>
                  </template>
                  <v-list-item-title>
                    {{ tc.title }}
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip size="x-small" :color="statusColor(tc.status)">{{ tc.status }}</v-chip>
                    <span v-if="tc.suite" class="text-caption text-medium-emphasis ml-2">
                      {{ tc.suite.name }}
                    </span>
                  </v-list-item-subtitle>
                  <template v-slot:append>
                    <v-btn icon size="x-small" variant="text" color="error" @click.stop="removeCase(tc.id)">
                      <v-icon>mdi-close</v-icon>
                    </v-btn>
                  </template>
                </v-list-item>
              </v-list>
              <v-empty-state
                v-if="cases.length === 0"
                icon="mdi-test-tube-off"
                text="No cases in this plan yet. Select suites and add cases below."
              />
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Add Cases -->
        <v-col cols="12" md="4">
          <v-card>
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2">mdi-plus</v-icon>
              Add Cases
            </v-card-title>
            <v-divider />
            <v-card-text>
              <v-select
                v-model="selectedSuites"
                :items="suites"
                item-title="name"
                item-value="id"
                label="Select Suites"
                multiple
                chips
                clearable
                class="mb-3"
                @update:model-value="loadAvailableCases"
              />

              <v-text-field
                v-model="caseSearch"
                label="Search cases"
                prepend-inner-icon="mdi-magnify"
                density="compact"
                hide-details
                variant="outlined"
                class="mb-2"
                clearable
              />

              <div class="d-flex align-center mb-2">
                <v-btn
                  size="small"
                  variant="text"
                  prepend-icon="mdi-checkbox-multiple-marked"
                  @click="selectAllAvailable"
                  :disabled="filteredAvailableCases.length === 0"
                >
                  Select All
                </v-btn>
                <v-btn
                  size="small"
                  variant="text"
                  prepend-icon="mdi-checkbox-multiple-blank-outline"
                  @click="deselectAll"
                  :disabled="selectedCases.length === 0"
                >
                  Deselect All
                </v-btn>
                <v-spacer />
                <span class="text-caption text-medium-emphasis">
                  {{ selectedCases.length }} selected
                </span>
              </div>

              <v-list density="compact" style="max-height: 350px; overflow-y: auto;">
                <v-list-item
                  v-for="tc in filteredAvailableCases"
                  :key="tc.id"
                  :disabled="isCaseInPlan(tc.id)"
                >
                  <template v-slot:prepend>
                    <v-checkbox-btn
                      v-model="selectedCases"
                      :value="tc.id"
                      :disabled="isCaseInPlan(tc.id)"
                    />
                  </template>
                  <v-list-item-title>{{ tc.title }}</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip size="x-small" :color="typeColor(tc.type)">{{ tc.type }}</v-chip>
                    <span class="text-caption text-medium-emphasis ml-1">{{ tc.suite?.name }}</span>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn
                color="primary"
                :disabled="selectedCases.length === 0"
                @click="addCasesToPlan"
              >
                Add {{ selectedCases.length ? `(${selectedCases.length})` : '' }}
              </v-btn>
            </v-card-actions>
          </v-card>

          <v-card class="mt-4">
            <v-card-title>Runs from this Plan</v-card-title>
            <v-card-text>
              <v-list density="compact" v-if="runs.length">
                <v-list-item
                  v-for="run in runs"
                  :key="run.id"
                  :to="`/space/${spaceId}/test-runs/${run.id}`"
                >
                  <v-list-item-title>{{ run.name }}</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip size="x-small" :color="runStatusColor(run.status)">{{ run.status }}</v-chip>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
              <v-empty-state
                v-else
                icon="mdi-play-circle-outline"
                text="No runs yet"
              />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    <!-- View Test Case Dialog -->
    <v-dialog v-model="caseDialogOpen" max-width="900" scrollable>
      <v-card v-if="selectedCase">
        <v-card-title class="d-flex align-center py-3">
          <span class="text-truncate" style="max-width: 500px">{{ selectedCase.title }}</span>
          <v-spacer />
          <v-chip size="small" :color="typeColor(selectedCase.type)" class="mr-1">{{ selectedCase.type }}</v-chip>
          <v-chip size="small" :color="statusColor(selectedCase.status)">{{ selectedCase.status }}</v-chip>
          <v-btn
            icon="mdi-pencil"
            size="small"
            variant="text"
            class="ml-2"
            :to="`/space/${spaceId}/test-cases/${selectedCase.id}/edit`"
            @click="caseDialogOpen = false"
          />
          <v-btn icon="mdi-close" size="small" variant="text" @click="caseDialogOpen = false" />
        </v-card-title>
        <v-divider />
        <v-card-text class="py-4">
          <div v-if="selectedCase.text">
            <div class="text-subtitle-2 text-medium-emphasis mb-2">Description</div>
            <editor-component :text="selectedCase.text" :edit="false" />
          </div>
          <div v-if="selectedCase.preconditions" class="mt-4">
            <div class="text-subtitle-2 text-medium-emphasis mb-2">Preconditions</div>
            <editor-component :text="selectedCase.preconditions" :edit="false" />
          </div>
          <div v-if="selectedCase.steps" class="mt-4">
            <div class="text-subtitle-2 text-medium-emphasis mb-2">Steps</div>
            <editor-component :text="selectedCase.steps" :edit="false" />
          </div>
          <div v-if="selectedCase.expected_results" class="mt-4">
            <div class="text-subtitle-2 text-medium-emphasis mb-2">Expected Results</div>
            <editor-component :text="selectedCase.expected_results" :edit="false" />
          </div>
          <div v-if="!selectedCase.text && !selectedCase.preconditions && !selectedCase.steps && !selectedCase.expected_results" class="text-center text-grey py-8">
            No content
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { testPlanService, testCaseService, testSuiteService, testRunService } from '@/services';
import EditorComponent from "@/components/common/editor/editorComponent.vue";

export default {
  name: "testPlanDetailComponent",
  components: { EditorComponent },
  data: () => ({
    plan: {},
    cases: [],
    runs: [],
    spaceId: undefined,
    planId: undefined,
    loader: true,
    suites: [],
    selectedSuites: [],
    availableCases: [],
    selectedCases: [],
    caseSearch: '',
    caseDialogOpen: false,
    selectedCase: null
  }),
  computed: {
    filteredAvailableCases() {
      const q = this.caseSearch.toLowerCase().trim();
      if (!q) return this.availableCases;
      return this.availableCases.filter(tc => tc.title?.toLowerCase().includes(q));
    }
  },
  created() {
    this.spaceId = this.$route.params.spaceId;
    this.planId = this.$route.params.planId;
  },
  mounted() {
    this.loadPlan();
    this.loadSuites();
  },
  methods: {
    async loadPlan() {
      this.loader = true;
      try {
        const [planRes, casesRes] = await Promise.all([
          testPlanService.getById(this.planId),
          testPlanService.getCases(this.planId)
        ]);
        this.plan = planRes.data;
        this.cases = casesRes.data;
        // Load runs that were created from this plan
        const runsRes = await testRunService.listBySpace(this.spaceId, { page: 1, page_size: 100 });
        this.runs = (runsRes.data.items || []).filter(r => r.plan_id === this.planId);
      } catch (e) {
        console.error(e);
      } finally {
        this.loader = false;
      }
    },
    async loadSuites() {
      try {
        const res = await testSuiteService.listBySpace(this.spaceId, { page: 1, page_size: 1000 });
        this.suites = res.data.items || [];
      } catch (e) {
        console.error(e);
      }
    },
    async loadAvailableCases() {
      if (!this.selectedSuites.length) {
        this.availableCases = [];
        this.selectedCases = [];
        return;
      }
      try {
        const promises = this.selectedSuites.map(suiteId =>
          testCaseService.listBySuite(suiteId)
        );
        const responses = await Promise.all(promises);
        const allCases = responses.flatMap(r => r.data);
        // Deduplicate by id
        const seen = new Set();
        this.availableCases = allCases.filter(tc => {
          if (seen.has(tc.id)) return false;
          seen.add(tc.id);
          return true;
        });
      } catch (e) {
        console.error(e);
        this.availableCases = [];
      }
    },
    isCaseInPlan(caseId) {
      return this.cases.some(c => c.id === caseId);
    },
    async addCasesToPlan() {
      const currentIds = this.cases.map(c => c.id);
      const newIds = [...currentIds, ...this.selectedCases];
      try {
        await testPlanService.update(this.planId, { case_ids: newIds });
        this.selectedCases = [];
        this.loadPlan();
      } catch (e) {
        console.error(e);
      }
    },
    selectAllAvailable() {
      const availableIds = this.filteredAvailableCases
        .filter(tc => !this.isCaseInPlan(tc.id))
        .map(tc => tc.id);
      // Add only new ids, preserving existing selection
      const newSelection = new Set([...this.selectedCases, ...availableIds]);
      this.selectedCases = Array.from(newSelection);
    },
    deselectAll() {
      this.selectedCases = [];
    },
    async removeCase(caseId) {
      const newIds = this.cases.filter(c => c.id !== caseId).map(c => c.id);
      try {
        await testPlanService.update(this.planId, { case_ids: newIds });
        this.loadPlan();
      } catch (e) {
        console.error(e);
      }
    },
    async createRun() {
      try {
        const res = await testRunService.create({
          name: `Run for ${this.plan.name}`,
          space_id: this.spaceId,
          plan_id: this.planId
        });
        this.$router.push(`/space/${this.spaceId}/test-runs/${res.data.id}`);
      } catch (e) {
        console.error(e);
      }
    },
    openCaseDialog(id) {
      testCaseService.getById(id).then(res => {
        this.selectedCase = res.data;
        this.caseDialogOpen = true;
      });
    },
    typeIcon(type) {
      const map = { manual: 'mdi-hand-back-right-outline', checklist: 'mdi-check-box-outline', automated: 'mdi-robot' };
      return map[type] || 'mdi-test-tube';
    },
    typeColor(type) {
      const map = { manual: 'info', checklist: 'success', automated: 'warning' };
      return map[type] || 'grey';
    },
    statusColor(status) {
      const map = { draft: 'grey', active: 'success', deprecated: 'error' };
      return map[status] || 'grey';
    },
    runStatusColor(status) {
      const map = { draft: 'grey', active: 'primary', completed: 'success' };
      return map[status] || 'grey';
    }
  }
}
</script>

<style scoped>
.case-item {
  cursor: pointer;
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}
.case-item:last-child {
  border-bottom: none;
}
</style>
