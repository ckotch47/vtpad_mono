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
      <v-btn
        icon
        class="ml-2"
        :to="`/space/${spaceId}/test-cases/edit-${caseId}`"
      >
        <v-icon>mdi-pencil</v-icon>
      </v-btn>
    </v-toolbar>

    <v-container fluid>
      <v-row>
        <v-col cols="12" md="8">
          <v-card class="mb-4">
            <v-card-title>Description</v-card-title>
            <v-card-text>
              <editor-component
                :text="testcase.text || ''"
                :edit="false"
                :show-menu-bubble="false"
                :show-menu-floating="false"
                :show-menu-fixed="false"
              />
            </v-card-text>
          </v-card>

          <v-card class="mb-4">
            <v-card-title>Preconditions</v-card-title>
            <v-card-text>
              <editor-component
                :text="testcase.preconditions || ''"
                :edit="false"
                :show-menu-bubble="false"
                :show-menu-floating="false"
                :show-menu-fixed="false"
              />
            </v-card-text>
          </v-card>

          <v-card class="mb-4">
            <v-card-title>Steps</v-card-title>
            <v-card-text>
              <editor-component
                :text="testcase.steps || ''"
                :edit="false"
                :show-menu-bubble="false"
                :show-menu-floating="false"
                :show-menu-fixed="false"
              />
            </v-card-text>
          </v-card>

          <v-card class="mb-4">
            <v-card-title>Expected Results</v-card-title>
            <v-card-text>
              <editor-component
                :text="testcase.expected_results || ''"
                :edit="false"
                :show-menu-bubble="false"
                :show-menu-floating="false"
                :show-menu-fixed="false"
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
  </div>
</template>

<script>
import axios from "axios";
import EditorComponent from "@/components/common/editor/editorComponent.vue";

export default {
  name: "testCaseDetailComponent",
  components: { EditorComponent },
  data: () => ({
    testcase: {},
    versions: [],
    spaceId: undefined,
    caseId: undefined,
    loader: true
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
        this.loader = false;
      }).catch(() => { this.loader = false; });
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
