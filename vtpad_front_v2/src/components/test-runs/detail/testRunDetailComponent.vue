<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>

  <div v-else>
    <!-- Header -->
    <v-container fluid class="pb-0">
      <v-row align="center">
        <v-col>
          <v-btn
            variant="text"
            prepend-icon="mdi-arrow-left"
            :to="`/space/${spaceId}/test-runs`"
            class="pl-0"
          >
            Test Runs
          </v-btn>
          <h1 class="text-h4 font-weight-bold mt-1">{{ run.name }}</h1>
          <p v-if="run.description" class="text-body-1 text-medium-emphasis mt-1">
            {{ run.description }}
          </p>
        </v-col>
        <v-col cols="auto">
          <v-chip :color="statusColor(run.status)" size="large" class="text-uppercase font-weight-bold">
            {{ run.status }}
          </v-chip>
        </v-col>
      </v-row>
    </v-container>

    <!-- Stats -->
    <v-container fluid class="py-3">
      <v-row>
        <v-col cols="4" md="2">
          <v-card variant="outlined">
            <v-card-text class="text-center py-3">
              <div class="text-h5 font-weight-bold">{{ stats.total }}</div>
              <div class="text-caption text-medium-emphasis">Total</div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="4" md="2">
          <v-card variant="outlined">
            <v-card-text class="text-center py-3">
              <div class="text-h5 font-weight-bold text-success">{{ stats.passed }}</div>
              <div class="text-caption text-medium-emphasis">Passed</div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="4" md="2">
          <v-card variant="outlined">
            <v-card-text class="text-center py-3">
              <div class="text-h5 font-weight-bold text-error">{{ stats.failed }}</div>
              <div class="text-caption text-medium-emphasis">Failed</div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="4" md="2">
          <v-card variant="outlined">
            <v-card-text class="text-center py-3">
              <div class="text-h5 font-weight-bold text-warning">{{ stats.blocked }}</div>
              <div class="text-caption text-medium-emphasis">Blocked</div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="4" md="2">
          <v-card variant="outlined">
            <v-card-text class="text-center py-3">
              <div class="text-h5 font-weight-bold text-grey">{{ stats.skipped }}</div>
              <div class="text-caption text-medium-emphasis">Skipped</div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="4" md="2">
          <v-card variant="outlined">
            <v-card-text class="text-center py-3">
              <div class="text-h5 font-weight-bold">{{ stats.not_run }}</div>
              <div class="text-caption text-medium-emphasis">Not Run</div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Actions -->
    <v-container fluid class="py-0">
      <v-row>
        <v-col>
          <v-btn v-if="run.status === 'draft'" color="primary" prepend-icon="mdi-play" @click="startRun" class="mr-2">
            Start Run
          </v-btn>
          <v-btn v-if="run.status === 'active'" color="success" prepend-icon="mdi-check" @click="completeRun" class="mr-2">
            Complete Run
          </v-btn>
        </v-col>
      </v-row>
    </v-container>

    <!-- Results by Section -->
    <v-container fluid>
      <v-row>
        <v-col>
          <v-card v-for="group in groupedResults" :key="group.sectionId || 'no-section'" class="mb-4">
            <v-card-title class="d-flex align-center py-3">
              <v-icon class="mr-2">mdi-folder-outline</v-icon>
              {{ group.sectionName }}
              <v-chip size="small" class="ml-2" color="primary">
                {{ group.results.length }}
              </v-chip>
            </v-card-title>
            <v-divider />
            <v-card-text class="pa-0">
              <v-list density="compact">
                <v-list-item
                  v-for="result in group.results"
                  :key="result.id"
                  class="result-item"
                >
                  <template v-slot:prepend>
                    <v-icon :color="statusColor(result.status)">
                      {{ statusIcon(result.status) }}
                    </v-icon>
                  </template>
                  <v-list-item-title class="font-weight-medium">
                    {{ result.testcase?.title || 'Unknown Case' }}
                    <v-chip size="x-small" :color="typeColor(result.testcase?.type)" class="ml-2">
                      {{ result.testcase?.type }}
                    </v-chip>
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    <span v-if="result.comment" class="text-medium-emphasis">{{ result.comment }}</span>
                    <span v-else class="text-grey">No comment</span>
                    <span v-if="result.duration_seconds" class="ml-2 text-caption">({{ result.duration_seconds }}s)</span>
                  </v-list-item-subtitle>
                  <template v-slot:append>
                    <v-chip
                      v-for="bugId in result.linked_bug_ids"
                      :key="bugId"
                      size="x-small"
                      color="error"
                      class="mr-1"
                      :to="`/space/${spaceId}/bugs?shortName=${bugId}`"
                    >
                      #{{ bugId }}
                    </v-chip>
                    <v-btn icon size="x-small" variant="text" @click="openResultModal(result)">
                      <v-icon>mdi-pencil</v-icon>
                    </v-btn>
                  </template>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>

          <v-card v-if="groupedResults.length === 0" class="text-center pa-10" variant="outlined">
            <v-icon size="64" color="grey-lighten-1">mdi-playlist-remove</v-icon>
            <div class="text-h6 text-grey mt-4">No test cases in this run</div>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Edit Result Dialog -->
    <v-dialog v-model="editModal" max-width="600" scrollable>
      <v-card v-if="editingResult">
        <v-card-title class="d-flex align-center">
          <span>Update Result</span>
          <v-spacer />
          <v-btn v-if="editingResult.status === 'failed'" color="error" size="small" prepend-icon="mdi-bug" @click="openBugModal">
            Create Bug
          </v-btn>
        </v-card-title>
        <v-divider />
        <v-card-text>
          <div class="text-subtitle-1 font-weight-medium mb-3">{{ editingResult.testcase?.title }}</div>

          <v-tabs v-model="editTab" class="mb-3">
            <v-tab value="result">Result</v-tab>
            <v-tab value="steps">Steps</v-tab>
          </v-tabs>

          <v-window v-model="editTab">
            <v-window-item value="result">
              <v-select
                v-model="editingResult.status"
                :items="['not_run','passed','failed','blocked','skipped']"
                label="Status"
                class="mb-2"
              />
              <v-text-field
                v-model="editingResult.duration_seconds"
                label="Duration (seconds)"
                type="number"
                class="mb-2"
              />
              <v-textarea v-model="editingResult.comment" label="Comment" rows="2" class="mb-2" />
              <v-combobox
                v-model="editingResult.linked_bug_ids"
                :items="spaceBugs"
                item-title="short_name"
                item-value="short_name"
                label="Linked Bugs"
                multiple
                chips
                closable-chips
                clearable
                :return-object="false"
              />
            </v-window-item>

            <v-window-item value="steps">
              <v-list density="compact">
                <v-list-item v-for="(step, idx) in stepResults" :key="idx" class="step-item">
                  <v-row align="center" no-gutters>
                    <v-col cols="1">
                      <span class="text-caption text-medium-emphasis">{{ idx + 1 }}</span>
                    </v-col>
                    <v-col cols="7">
                      <span class="text-body-2">{{ step.step_text }}</span>
                    </v-col>
                    <v-col cols="4">
                      <v-select
                        v-model="step.status"
                        :items="['not_run','passed','failed','blocked','skipped']"
                        density="compact"
                        hide-details
                        variant="outlined"
                        class="step-status-select"
                      />
                    </v-col>
                  </v-row>
                  <v-textarea
                    v-model="step.comment"
                    label="Step comment"
                    rows="1"
                    density="compact"
                    hide-details
                    variant="outlined"
                    class="mt-1"
                  />
                </v-list-item>
              </v-list>
              <v-empty-state
                v-if="stepResults.length === 0"
                icon="mdi-format-list-bulleted"
                text="No steps recorded for this case"
              />
            </v-window-item>
          </v-window>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="editModal = false">Cancel</v-btn>
          <v-btn color="primary" @click="saveResult">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Quick Bug Modal -->
    <v-dialog v-model="bugModal" max-width="560">
      <v-card>
        <v-card-title>Create Bug</v-card-title>
        <v-card-text>
          <v-text-field v-model="newBug.title" label="Title" required autofocus />
          <v-textarea v-model="newBug.steps" label="Steps to Reproduce" rows="3" />
          <v-textarea v-model="newBug.expected" label="Expected Result" rows="2" />
          <v-textarea v-model="newBug.actual" label="Actual Result" rows="2" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="bugModal = false">Cancel</v-btn>
          <v-btn color="error" @click="createBug">Create Bug</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { testRunService, bugService } from '@/services';

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
    editingResult: null,
    spaceBugs: [],
    editTab: 'result',
    stepResults: [],
    bugModal: false,
    newBug: { title: '', steps: '', expected: '', actual: '' }
  }),
  computed: {
    groupedResults() {
      const map = {};
      for (const r of this.results) {
        const sectionId = r.testcase?.section?.id || 'no-section';
        const sectionName = r.testcase?.section?.name || 'No Section';
        if (!map[sectionId]) {
          map[sectionId] = { sectionId, sectionName, results: [] };
        }
        map[sectionId].results.push(r);
      }
      return Object.values(map);
    }
  },
  mounted() {
    this.spaceId = this.$route.params.spaceId;
    this.runId = this.$route.params.runId;
    this.loadRun();
    this.loadBugs();
  },
  methods: {
    loadRun() {
      testRunService.getDetail(this.runId).then(res => {
        this.run = res.data.run;
        this.stats = res.data.stats;
        this.results = res.data.results;
        this.loader = false;
      }).catch(() => { this.loader = false; });
    },
    loadBugs() {
      bugService.list({
        space_id: this.spaceId,
        state: ['OPEN', 'REOPEN', 'FIXED'],
        limit: 100
      }).then(res => {
        this.spaceBugs = res.data || [];
      }).catch(() => {
        this.spaceBugs = [];
      });
    },
    startRun() {
      testRunService.start(this.runId).then(() => this.loadRun());
    },
    completeRun() {
      testRunService.complete(this.runId).then(() => this.loadRun());
    },
    openResultModal(result) {
      this.editingResult = {
        ...result,
        linked_bug_ids: result.linked_bug_ids || []
      };
      this.editTab = 'result';
      this.stepResults = [];
      this.loadStepResults(result.id);
      this.editModal = true;
    },
    loadStepResults(resultId) {
      testRunService.getStepResults(resultId).then(res => {
        this.stepResults = res.data;
      }).catch(() => {
        this.stepResults = [];
      });
    },
    saveResult() {
      // Save main result
      testRunService.updateResult(this.editingResult.id, {
        status: this.editingResult.status,
        duration_seconds: parseInt(this.editingResult.duration_seconds) || null,
        comment: this.editingResult.comment,
        linked_bug_ids: this.editingResult.linked_bug_ids
      }).then(() => {
        // Save step results if any
        if (this.stepResults.length > 0) {
          return testRunService.updateStepResults(this.editingResult.id, {
            steps: this.stepResults.map(s => ({
              step_index: s.step_index,
              step_text: s.step_text,
              status: s.status,
              comment: s.comment,
              screenshot_url: s.screenshot_url
            }))
          });
        }
      }).then(() => {
        this.editModal = false;
        this.loadRun();
      });
    },
    openBugModal() {
      this.newBug = {
        title: `Bug: ${this.editingResult.testcase?.title || 'Failed test'}`,
        steps: this.editingResult.testcase?.steps || '',
        expected: this.editingResult.testcase?.expected_results || '',
        actual: this.editingResult.comment || ''
      };
      this.bugModal = true;
    },
    createBug() {
      bugService.create({
        title: this.newBug.title,
        text: this.newBug.actual,
        steps: this.newBug.steps,
        spaces: this.spaceId,
        state: 'OPEN'
      }).then(res => {
        const bugShortName = res.data.short_name;
        // Link bug to result
        const bugs = [...(this.editingResult.linked_bug_ids || []), bugShortName];
        return testRunService.updateResult(this.editingResult.id, {
          linked_bug_ids: bugs
        });
      }).then(() => {
        this.bugModal = false;
        this.editModal = false;
        this.loadRun();
      }).catch(err => {
        console.error(err);
      });
    },
    statusColor(status) {
      const map = { passed: 'success', failed: 'error', blocked: 'warning', skipped: 'grey', not_run: 'default' };
      return map[status] || 'default';
    },
    statusIcon(status) {
      const map = {
        passed: 'mdi-check-circle',
        failed: 'mdi-close-circle',
        blocked: 'mdi-minus-circle',
        skipped: 'mdi-arrow-right-circle',
        not_run: 'mdi-circle-outline'
      };
      return map[status] || 'mdi-help-circle';
    },
    typeColor(type) {
      const map = { manual: 'primary', checklist: 'success', automated: 'warning' };
      return map[type] || 'grey';
    }
  }
}
</script>

<style scoped>
.result-item {
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}
.result-item:last-child {
  border-bottom: none;
}
.step-item {
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  padding: 8px 0;
}
.step-item:last-child {
  border-bottom: none;
}
.step-status-select {
  min-width: 120px;
}
</style>
