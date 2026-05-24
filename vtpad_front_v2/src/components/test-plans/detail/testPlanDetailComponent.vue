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
          <v-btn color="primary" prepend-icon="mdi-play" @click="createRun">
            New Run
          </v-btn>
        </v-col>
      </v-row>
    </v-container>

    <v-container fluid>
      <v-row>
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
                  :to="`/space/${spaceId}/test-cases/${tc.id}`"
                >
                  <template v-slot:prepend>
                    <v-icon :color="typeColor(tc.type)">{{ typeIcon(tc.type) }}</v-icon>
                  </template>
                  <v-list-item-title>{{ tc.title }}</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip size="x-small" :color="statusColor(tc.status)">{{ tc.status }}</v-chip>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
              <v-empty-state
                v-if="cases.length === 0"
                icon="mdi-test-tube-off"
                text="No cases match this plan's filters"
              />
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>Info</v-card-title>
            <v-card-text>
              <v-list density="compact">
                <v-list-item>
                  <v-list-item-title>Suite</v-list-item-title>
                  <v-list-item-subtitle>{{ plan.suite?.name || '-' }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>Filters</v-list-item-title>
                  <v-list-item-subtitle>
                    <code v-if="plan.filters && Object.keys(plan.filters).length">{{ JSON.stringify(plan.filters) }}</code>
                    <span v-else>All cases</span>
                  </v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>Created</v-list-item-title>
                  <v-list-item-subtitle>{{ formatDate(plan.created_at) }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
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
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "testPlanDetailComponent",
  data: () => ({
    plan: {},
    cases: [],
    runs: [],
    spaceId: undefined,
    planId: undefined,
    loader: true
  }),
  created() {
    this.spaceId = this.$route.params.spaceId;
    this.planId = this.$route.params.planId;
  },
  mounted() {
    this.loadPlan();
  },
  methods: {
    async loadPlan() {
      this.loader = true;
      try {
        const [planRes, casesRes] = await Promise.all([
          axios.get(`/api/v2/test-plan/${this.planId}`),
          axios.get(`/api/v2/test-plan/${this.planId}/cases`)
        ]);
        this.plan = planRes.data;
        this.cases = casesRes.data;
        // Load runs that were created from this plan
        const runsRes = await axios.get(`/api/v2/test-run/space/${this.spaceId}`, {
          params: { page: 1, page_size: 100 }
        });
        this.runs = (runsRes.data.items || []).filter(r => r.plan_id === this.planId);
      } catch (e) {
        console.error(e);
      } finally {
        this.loader = false;
      }
    },
    async createRun() {
      try {
        const res = await axios.post('/api/v2/test-run/', {
          name: `Run for ${this.plan.name}`,
          space_id: this.spaceId,
          plan_id: this.planId
        });
        this.$router.push(`/space/${this.spaceId}/test-runs/${res.data.id}`);
      } catch (e) {
        console.error(e);
      }
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
    },
    formatDate(date) {
      return date ? new Date(date).toLocaleDateString() : '';
    }
  }
}
</script>
