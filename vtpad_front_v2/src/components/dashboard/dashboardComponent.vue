<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>

  <div v-else>
    <v-container fluid class="pb-0">
      <h1 class="text-h4 font-weight-bold">Dashboard</h1>
    </v-container>

    <!-- Stats Cards -->
    <v-container fluid>
      <v-row>
        <v-col cols="6" md="3">
          <v-card variant="outlined">
            <v-card-text class="d-flex align-center py-3">
              <v-icon size="32" color="primary" class="mr-3">mdi-test-tube</v-icon>
              <div>
                <div class="text-h6 font-weight-bold">{{ stats.cases.total }}</div>
                <div class="text-caption text-medium-emphasis">Total Cases</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="6" md="3">
          <v-card variant="outlined">
            <v-card-text class="d-flex align-center py-3">
              <v-icon size="32" color="info" class="mr-3">mdi-folder-open-outline</v-icon>
              <div>
                <div class="text-h6 font-weight-bold">{{ stats.suites }}</div>
                <div class="text-caption text-medium-emphasis">Suites</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="6" md="3">
          <v-card variant="outlined">
            <v-card-text class="d-flex align-center py-3">
              <v-icon size="32" color="success" class="mr-3">mdi-play-circle-outline</v-icon>
              <div>
                <div class="text-h6 font-weight-bold">{{ stats.runs.total }}</div>
                <div class="text-caption text-medium-emphasis">Total Runs</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="6" md="3">
          <v-card variant="outlined">
            <v-card-text class="d-flex align-center py-3">
              <v-icon size="32" color="warning" class="mr-3">mdi-run-fast</v-icon>
              <div>
                <div class="text-h6 font-weight-bold">{{ stats.runs.active }}</div>
                <div class="text-caption text-medium-emphasis">Active Runs</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Case Type Breakdown -->
      <v-row class="mt-2">
        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>Case Types</v-card-title>
            <v-card-text>
              <v-list density="compact">
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="info">mdi-hand-back-right-outline</v-icon>
                  </template>
                  <v-list-item-title>Manual</v-list-item-title>
                  <template v-slot:append>
                    <v-chip size="small" color="info">{{ stats.cases.manual }}</v-chip>
                  </template>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="success">mdi-check-box-outline</v-icon>
                  </template>
                  <v-list-item-title>Checklist</v-list-item-title>
                  <template v-slot:append>
                    <v-chip size="small" color="success">{{ stats.cases.checklist }}</v-chip>
                  </template>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="warning">mdi-robot</v-icon>
                  </template>
                  <v-list-item-title>Automated</v-list-item-title>
                  <template v-slot:append>
                    <v-chip size="small" color="warning">{{ stats.cases.automated }}</v-chip>
                  </template>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>Latest Results</v-card-title>
            <v-card-text>
              <v-list density="compact">
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="success">mdi-check-circle</v-icon>
                  </template>
                  <v-list-item-title>Passed</v-list-item-title>
                  <template v-slot:append>
                    <v-chip size="small" color="success">{{ stats.latest_results.passed }}</v-chip>
                  </template>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="error">mdi-close-circle</v-icon>
                  </template>
                  <v-list-item-title>Failed</v-list-item-title>
                  <template v-slot:append>
                    <v-chip size="small" color="error">{{ stats.latest_results.failed }}</v-chip>
                  </template>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="warning">mdi-minus-circle</v-icon>
                  </template>
                  <v-list-item-title>Blocked</v-list-item-title>
                  <template v-slot:append>
                    <v-chip size="small" color="warning">{{ stats.latest_results.blocked }}</v-chip>
                  </template>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="grey">mdi-alert-circle-outline</v-icon>
                  </template>
                  <v-list-item-title>Skipped</v-list-item-title>
                  <template v-slot:append>
                    <v-chip size="small" color="grey">{{ stats.latest_results.skipped }}</v-chip>
                  </template>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>Top Failed Cases</v-card-title>
            <v-card-text>
              <v-list density="compact" v-if="topFailed.length">
                <v-list-item
                  v-for="tc in topFailed"
                  :key="tc.id"
                  :to="`/space/${spaceId}/test-cases/${tc.id}`"
                >
                  <v-list-item-title class="text-truncate" style="max-width: 220px">
                    {{ tc.title }}
                  </v-list-item-title>
                  <template v-slot:append>
                    <v-chip size="x-small" color="error">{{ tc.fail_count }} fails</v-chip>
                  </template>
                </v-list-item>
              </v-list>
              <v-empty-state
                v-else
                icon="mdi-check-circle"
                text="No failed cases recently"
              />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Trend Chart -->
      <v-row class="mt-2">
        <v-col cols="12">
          <v-card>
            <v-card-title>Run Trend (Last 30 Days)</v-card-title>
            <v-card-text>
              <v-table v-if="trend.length">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Run</th>
                    <th>Total</th>
                    <th class="text-success">Passed</th>
                    <th class="text-error">Failed</th>
                    <th class="text-warning">Blocked</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in trend" :key="row.run_id">
                    <td>{{ row.date }}</td>
                    <td>
                      <router-link :to="`/space/${spaceId}/test-runs/${row.run_id}`">
                        {{ row.run_name }}
                      </router-link>
                    </td>
                    <td>{{ row.total }}</td>
                    <td class="text-success">{{ row.passed }}</td>
                    <td class="text-error">{{ row.failed }}</td>
                    <td class="text-warning">{{ row.blocked }}</td>
                  </tr>
                </tbody>
              </v-table>
              <v-empty-state
                v-else
                icon="mdi-chart-line"
                text="No completed runs in the last 30 days"
              />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { analyticsService } from '@/services'

export default {
  name: "dashboardComponent",
  data: () => ({
    spaceId: undefined,
    loader: true,
    stats: {
      cases: { total: 0, manual: 0, checklist: 0, automated: 0 },
      suites: 0,
      runs: { total: 0, active: 0 },
      latest_results: { total: 0, passed: 0, failed: 0, blocked: 0, skipped: 0, not_run: 0 }
    },
    topFailed: [],
    trend: []
  }),
  created() {
    this.spaceId = this.$route.params.spaceId;
  },
  mounted() {
    this.loadDashboard();
  },
  methods: {
    async loadDashboard() {
      this.loader = true;
      try {
        const [statsRes, topRes, trendRes] = await Promise.all([
          analyticsService.getSpaceStats(this.spaceId),
          analyticsService.getTopFailed(this.spaceId),
          analyticsService.getTrend(this.spaceId)
        ]);
        this.stats = statsRes.data;
        this.topFailed = topRes.data;
        this.trend = trendRes.data;
      } catch (e) {
        console.error(e);
      } finally {
        this.loader = false;
      }
    }
  }
}
</script>
