<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>

  <div v-else>
    <v-toolbar density="compact">
      <v-btn icon @click="$router.back()">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <v-toolbar-title>{{ suite.name }}</v-toolbar-title>
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-play" @click="createRun">
        New Run
      </v-btn>
    </v-toolbar>

    <v-container fluid>
      <v-row>
        <v-col cols="3">
          <v-card>
            <v-card-title class="d-flex align-center">
              Sections
              <v-spacer />
              <v-btn icon size="small" @click="openAddSection = true">
                <v-icon>mdi-plus</v-icon>
              </v-btn>
            </v-card-title>
            <v-card-text>
              <v-treeview
                :items="sectionTree"
                item-title="name"
                item-value="id"
                item-children="children"
                activatable
                @update:activated="onSectionSelect"
              />
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="9">
          <v-card v-if="selectedSection">
            <v-card-title>
              {{ selectedSection.name }}
              <v-spacer />
              <v-btn icon size="small" @click="openAddCase = true">
                <v-icon>mdi-plus</v-icon>
              </v-btn>
            </v-card-title>
            <v-card-text>
              <v-list>
                <v-list-item
                  v-for="tc in testCases"
                  :key="tc.id"
                  @click="$router.push(`/space/${spaceId}/test-cases/${tc.id}`)"
                >
                  <template v-slot:prepend>
                    <v-icon v-if="tc.type === 'manual'" icon="mdi-test-tube" />
                    <v-icon v-else-if="tc.type === 'checklist'" icon="mdi-check-box-outline" />
                    <v-icon v-else icon="mdi-robot" />
                  </template>
                  <v-list-item-title>{{ tc.title }}</v-list-item-title>
                  <v-list-item-subtitle>{{ tc.status }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>

          <v-card v-else class="text-center pa-10">
            <v-icon size="64" color="grey">mdi-shape-outline</v-icon>
            <div class="text-h6 text-grey mt-4">Select a section to view test cases</div>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <v-dialog v-model="openAddSection" max-width="400">
      <v-card>
        <v-card-title>Add Section</v-card-title>
        <v-card-text>
          <v-text-field v-model="newSection.name" label="Name" required />
          <v-select
            v-model="newSection.parent_id"
            :items="flatSections"
            item-title="name"
            item-value="id"
            label="Parent section (optional)"
            clearable
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="openAddSection = false">Cancel</v-btn>
          <v-btn color="primary" @click="addSection">Add</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="openAddCase" max-width="500">
      <v-card>
        <v-card-title>Add Test Case</v-card-title>
        <v-card-text>
          <v-text-field v-model="newCase.title" label="Title" required />
          <v-select
            v-model="newCase.type"
            :items="[{title:'Manual', value:'manual'}, {title:'Checklist', value:'checklist'}, {title:'Automated', value:'automated'}]"
            item-title="title"
            item-value="value"
            label="Type"
          />
          <v-textarea v-model="newCase.steps" label="Steps" rows="3" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="openAddCase = false">Cancel</v-btn>
          <v-btn color="primary" @click="addTestCase">Add</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "testSuiteDetailComponent",
  data: () => ({
    suite: {},
    sectionTree: [],
    flatSections: [],
    selectedSection: null,
    testCases: [],
    spaceId: undefined,
    suiteId: undefined,
    loader: true,
    openAddSection: false,
    openAddCase: false,
    newSection: { name: '', parent_id: null },
    newCase: { title: '', type: 'manual', steps: '' }
  }),
  mounted() {
    this.spaceId = this.$route.params.spaceId;
    this.suiteId = this.$route.params.suiteId;
    this.loadSuite();
    this.loadSections();
  },
  methods: {
    loadSuite() {
      axios.get(`/api/v2/test-suite/${this.suiteId}`).then(res => {
        this.suite = res.data;
        this.loader = false;
      });
    },
    loadSections() {
      axios.get(`/api/v2/section/suite/${this.suiteId}/tree`).then(res => {
        this.sectionTree = res.data;
        this.flatSections = this.flattenTree(res.data);
      });
    },
    flattenTree(nodes, list = []) {
      for (const n of nodes || []) {
        list.push({ id: n.id, name: n.name });
        this.flattenTree(n.children, list);
      }
      return list;
    },
    onSectionSelect(ids) {
      const id = ids[0];
      this.selectedSection = this.flatSections.find(s => s.id === id) || { id, name: 'Section' };
      this.loadTestCases(id);
    },
    loadTestCases(sectionId) {
      axios.get(`/api/v2/test-case/section/${sectionId}`).then(res => {
        this.testCases = res.data;
      });
    },
    addSection() {
      axios.post('/api/v2/section/', {
        name: this.newSection.name,
        suite_id: this.suiteId,
        parent_id: this.newSection.parent_id || null
      }).then(() => {
        this.openAddSection = false;
        this.newSection = { name: '', parent_id: null };
        this.loadSections();
      });
    },
    addTestCase() {
      axios.post('/api/v2/test-case/', {
        title: this.newCase.title,
        type: this.newCase.type,
        steps: this.newCase.steps,
        space_id: this.spaceId,
        suite_id: this.suiteId,
        section_id: this.selectedSection.id
      }).then(() => {
        this.openAddCase = false;
        this.newCase = { title: '', type: 'manual', steps: '' };
        this.loadTestCases(this.selectedSection.id);
      });
    },
    createRun() {
      axios.post('/api/v2/test-run/', {
        name: `Run for ${this.suite.name}`,
        space_id: this.spaceId,
        suite_id: this.suiteId
      }).then(res => {
        this.$router.push(`/space/${this.spaceId}/test-runs/${res.data.id}`);
      });
    }
  }
}
</script>
