<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>

  <div v-else>
    <v-toolbar density="compact">
      <v-btn icon @click="$router.back()">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <v-toolbar-title>{{ run.name }}</v-toolbar-title>
      <v-spacer />
      <v-chip v-if="run.status === 'completed'" color="success">Completed</v-chip>
      <v-chip v-else-if="run.status === 'active'" color="primary">Active</v-chip>
      <v-chip v-else color="grey">Draft</v-chip>
    </v-toolbar>

    <v-container fluid>
      <v-row>
        <v-col cols="12" md="3">
          <v-card>
            <v-card-title>Statistics</v-card-title>
            <v-card-text>
              <v-row dense>
                <v-col cols="6"><div class="text-h6">{{ stats.total }}</div><div class="text-caption">Total</div></v-col>
                <v-col cols="6"><div class="text-h6 text-success">{{ stats.passed }}</div><div class="text-caption">Passed</div></v-col>
                <v-col cols="6"><div class="text-h6 text-error">{{ stats.failed }}</div><div class="text-caption">Failed</div></v-col>
                <v-col cols="6"><div class="text-h6 text-warning">{{ stats.blocked }}</div><div class="text-caption">Blocked</div></v-col>
                <v-col cols="6"><div class="text-h6">{{ stats.not_run }}</div><div class="text-caption">Not Run</div></v-col>
                <v-col cols="6"><div class="text-h6">{{ stats.skipped }}</div><div class="text-caption">Skipped</div></v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <v-card class="mt-4">
            <v-card-title>Actions</v-card-title>
            <v-card-text>
              <v-btn v-if="run.status === 'draft'" block color="primary" class="mb-2" @click="startRun">Start Run</v-btn>
              <v-btn v-if="run.status === 'active'" block color="success" @click="completeRun">Complete Run</v-btn>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="9">
          <v-card>
            <v-card-title>Results</v-card-title>
            <v-card-text>
              <v-table>
                <thead>
                  <tr>
                    <th>Test Case</th>
                    <th>Status</th>
                    <th>Duration</th>
                    <th>Comment</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="result in results" :key="result.id">
                    <td>{{ result.testcase?.title || result.testcase_id }}</td>
                    <td>
                      <v-chip
                        :color="statusColor(result.status)"
                        size="small"
                        @click="openResultModal(result)"
                        style="cursor:pointer"
                      >
                        {{ result.status }}
                      </v-chip>
                    </td>
                    <td>{{ result.duration_seconds ? result.duration_seconds + 's' : '-' }}</td>
                    <td>{{ result.comment || '-' }}</td>
                    <td>
                      <v-btn icon size="x-small" @click="openResultModal(result)">
                        <v-icon>mdi-pencil</v-icon>
                      </v-btn>
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <v-dialog v-model="editModal" max-width="500">
      <v-card v-if="editingResult">
        <v-card-title>Update Result</v-card-title>
        <v-card-text>
          <v-select
            v-model="editingResult.status"
            :items="['not_run','passed','failed','blocked','skipped']"
            label="Status"
          />
          <v-text-field v-model="editingResult.duration_seconds" label="Duration (seconds)" type="number" />
          <v-textarea v-model="editingResult.comment" label="Comment" rows="2" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="editModal = false">Cancel</v-btn>
          <v-btn color="primary" @click="saveResult">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "testRunDetailComponent",
  data: () => ({
    run: {},
    stats: {},
    results: [],
    spaceId: undefined,
    runId: undefined,
    loader: true,
    editModal: false,
    editingResult: null
  }),
  mounted() {
    this.spaceId = this.$route.params.spaceId;
    this.runId = this.$route.params.runId;
    this.loadRun();
  },
  methods: {
    loadRun() {
      axios.get(`/api/v2/test-run/${this.runId}/detail`).then(res => {
        this.run = res.data.run;
        this.stats = res.data.stats;
        this.results = res.data.results;
        this.loader = false;
      }).catch(() => { this.loader = false; });
    },
    statusColor(status) {
      const map = { passed: 'success', failed: 'error', blocked: 'warning', skipped: 'grey', not_run: 'default' };
      return map[status] || 'default';
    },
    startRun() {
      axios.post(`/api/v2/test-run/${this.runId}/start`).then(() => this.loadRun());
    },
    completeRun() {
      axios.post(`/api/v2/test-run/${this.runId}/complete`).then(() => this.loadRun());
    },
    openResultModal(result) {
      this.editingResult = { ...result };
      this.editModal = true;
    },
    saveResult() {
      axios.patch(`/api/v2/test-run/result/${this.editingResult.id}`, {
        status: this.editingResult.status,
        duration_seconds: parseInt(this.editingResult.duration_seconds) || null,
        comment: this.editingResult.comment
      }).then(() => {
        this.editModal = false;
        this.loadRun();
      });
    }
  }
}
</script>
