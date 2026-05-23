<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>

  <div v-else>
    <v-toolbar density="compact">
      <v-btn icon @click="$router.back()">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <v-toolbar-title>{{ testcase.title }}</v-toolbar-title>
      <v-spacer />
      <v-chip size="small" :color="typeColor(testcase.type)" class="mr-2">{{ testcase.type }}</v-chip>
      <v-chip size="small" :color="statusColor(testcase.status)">{{ testcase.status }}</v-chip>
      <v-btn icon class="ml-2" @click="openEdit = true">
        <v-icon>mdi-pencil</v-icon>
      </v-btn>
    </v-toolbar>

    <v-container fluid>
      <v-row>
        <v-col cols="12" md="8">
          <v-card class="mb-4">
            <v-card-title>Description</v-card-title>
            <v-card-text>
              <div v-html="testcase.text || 'No description'" />
            </v-card-text>
          </v-card>

          <v-card class="mb-4">
            <v-card-title>Preconditions</v-card-title>
            <v-card-text>
              <div v-html="testcase.preconditions || 'None'" />
            </v-card-text>
          </v-card>

          <v-card class="mb-4">
            <v-card-title>Steps</v-card-title>
            <v-card-text>
              <div v-html="testcase.steps || 'None'" />
            </v-card-text>
          </v-card>

          <v-card class="mb-4">
            <v-card-title>Expected Results</v-card-title>
            <v-card-text>
              <div v-html="testcase.expected_results || 'None'" />
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>Info</v-card-title>
            <v-card-text>
              <v-list density="compact">
                <v-list-item>
                  <v-list-item-title>ID</v-list-item-title>
                  <v-list-item-subtitle>{{ testcase.id }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>Short Name</v-list-item-title>
                  <v-list-item-subtitle>{{ testcase.short_name || '-' }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>External ID</v-list-item-title>
                  <v-list-item-subtitle>{{ testcase.external_id || '-' }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>Link</v-list-item-title>
                  <v-list-item-subtitle>
                    <a v-if="testcase.link" :href="testcase.link" target="_blank">{{ testcase.link }}</a>
                    <span v-else>-</span>
                  </v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>Created</v-list-item-title>
                  <v-list-item-subtitle>{{ formatDate(testcase.created_at) }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>Updated</v-list-item-title>
                  <v-list-item-subtitle>{{ formatDate(testcase.updated_at) }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>

          <v-card class="mt-4">
            <v-card-title>Versions</v-card-title>
            <v-card-text>
              <v-list density="compact">
                <v-list-item v-for="ver in versions" :key="ver.id">
                  <v-list-item-title>v{{ ver.version_number }}</v-list-item-title>
                  <v-list-item-subtitle>{{ formatDate(ver.created_at) }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <v-dialog v-model="openEdit" max-width="700">
      <v-card>
        <v-card-title>Edit Test Case</v-card-title>
        <v-card-text>
          <v-text-field v-model="editCase.title" label="Title" required />
          <v-select
            v-model="editCase.type"
            :items="['manual','checklist','automated']"
            label="Type"
          />
          <v-select
            v-model="editCase.status"
            :items="['draft','active','deprecated']"
            label="Status"
          />
          <v-text-field v-model="editCase.short_name" label="Short Name" />
          <v-text-field v-model="editCase.external_id" label="External ID" />
          <v-text-field v-model="editCase.link" label="Link" />
          <v-textarea v-model="editCase.text" label="Description" rows="3" />
          <v-textarea v-model="editCase.preconditions" label="Preconditions" rows="2" />
          <v-textarea v-model="editCase.steps" label="Steps" rows="4" />
          <v-textarea v-model="editCase.expected_results" label="Expected Results" rows="3" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="openEdit = false">Cancel</v-btn>
          <v-btn color="primary" @click="saveCase">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "testCaseDetailComponent",
  data: () => ({
    testcase: {},
    versions: [],
    spaceId: undefined,
    caseId: undefined,
    loader: true,
    openEdit: false,
    editCase: {}
  }),
  mounted() {
    this.spaceId = this.$route.params.spaceId;
    this.caseId = this.$route.params.caseId;
    this.loadCase();
  },
  methods: {
    loadCase() {
      axios.get(`/api/v2/test-case/${this.caseId}`).then(res => {
        this.testcase = res.data;
        this.editCase = { ...res.data };
        this.loader = false;
      }).catch(() => { this.loader = false; });
    },
    saveCase() {
      axios.patch(`/api/v2/test-case/${this.caseId}`, this.editCase).then(() => {
        this.openEdit = false;
        this.loadCase();
      });
    },
    typeColor(type) {
      const map = { manual: 'primary', checklist: 'warning', automated: 'success' };
      return map[type] || 'grey';
    },
    statusColor(status) {
      const map = { active: 'success', draft: 'grey', deprecated: 'error' };
      return map[status] || 'grey';
    },
    formatDate(date) {
      return date ? new Date(date).toLocaleDateString() : '';
    }
  }
}
</script>
