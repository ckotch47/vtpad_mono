<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>

  <div v-else>
    <!-- Header -->
    <v-container fluid class="pb-0">
      <breadcrumbs-component :items="breadcrumbItems" />
      <v-row align="center">
        <v-col>
          <v-btn
            variant="text"
            prepend-icon="mdi-arrow-left"
            :to="`/space/${spaceId}/test-suites`"
            class="pl-0"
          >
            Test Suites
          </v-btn>
          <h1 class="text-h4 font-weight-bold mt-1">{{ suite.name }}</h1>
          <p v-if="suite.description" class="text-body-1 text-medium-emphasis mt-1">
            {{ suite.description }}
          </p>
        </v-col>
        <v-col cols="auto">
          <v-btn color="primary" prepend-icon="mdi-play" @click="createRun">
            New Run
          </v-btn>
        </v-col>
      </v-row>
    </v-container>

    <!-- Stats -->
    <v-container fluid class="py-3">
      <v-row>
        <v-col cols="6" md="3">
          <v-card variant="outlined">
            <v-card-text class="d-flex align-center py-3">
              <v-icon size="32" color="primary" class="mr-3">mdi-test-tube</v-icon>
              <div>
                <div class="text-h6 font-weight-bold">{{ allCases.length }}</div>
                <div class="text-caption text-medium-emphasis">Total Cases</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="6" md="3">
          <v-card variant="outlined">
            <v-card-text class="d-flex align-center py-3">
              <v-icon size="32" color="info" class="mr-3">mdi-hand-back-right-outline</v-icon>
              <div>
                <div class="text-h6 font-weight-bold">{{ caseCountByType('manual') }}</div>
                <div class="text-caption text-medium-emphasis">Manual</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="6" md="3">
          <v-card variant="outlined">
            <v-card-text class="d-flex align-center py-3">
              <v-icon size="32" color="success" class="mr-3">mdi-check-box-outline</v-icon>
              <div>
                <div class="text-h6 font-weight-bold">{{ caseCountByType('checklist') }}</div>
                <div class="text-caption text-medium-emphasis">Checklist</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="6" md="3">
          <v-card variant="outlined">
            <v-card-text class="d-flex align-center py-3">
              <v-icon size="32" color="warning" class="mr-3">mdi-robot</v-icon>
              <div>
                <div class="text-h6 font-weight-bold">{{ caseCountByType('automated') }}</div>
                <div class="text-caption text-medium-emphasis">Automated</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Main Content -->
    <v-container fluid>
      <v-row>
        <!-- Sections -->
        <v-col cols="12" md="3">
          <v-card>
            <v-card-title class="d-flex align-center py-3">
              <v-icon class="mr-2">mdi-folder-open-outline</v-icon>
              Sections
              <v-spacer />
              <v-btn icon size="small" variant="text" @click="openSectionDialog()">
                <v-icon>mdi-plus</v-icon>
              </v-btn>
            </v-card-title>
            <v-divider />
            <v-card-text class="pa-0">
              <v-treeview
                :items="sectionTree"
                item-title="name"
                item-value="id"
                item-children="children"
                activatable
                @update:activated="onSectionSelect"
                class="section-tree"
              >
                <template v-slot:title="{ item }">
                  <span
                    v-if="editingSectionId !== item.id"
                    @dblclick="startInlineRename(item)"
                    class="tree-node-text"
                  >{{ item.name }}</span>
                  <v-text-field
                    v-else
                    v-model="editingSectionName"
                    density="compact"
                    hide-details
                    variant="outlined"
                    autofocus
                    class="inline-rename-field"
                    @blur="saveInlineRename"
                    @keydown.enter="saveInlineRename"
                    @keydown.esc="cancelInlineRename"
                  />
                  <v-chip size="x-small" color="primary" variant="outlined" class="ml-2">
                    {{ item.test_case_count || 0 }}
                  </v-chip>
                </template>
                <template v-slot:prepend="{ item }">
                  <v-icon size="small" color="primary">mdi-folder-outline</v-icon>
                </template>
                <template v-slot:append="{ item }">
                  <v-menu>
                    <template v-slot:activator="{ props }">
                      <v-btn
                        icon="mdi-dots-vertical"
                        size="x-small"
                        variant="text"
                        v-bind="props"
                        @click.stop
                      />
                    </template>
                    <v-list density="compact">
                      <v-list-item @click="openSectionDialog(item.id)">
                        <template v-slot:prepend>
                          <v-icon>mdi-plus</v-icon>
                        </template>
                        <v-list-item-title>Add sub-section</v-list-item-title>
                      </v-list-item>
                      <v-list-item @click="openRenameDialog(item)">
                        <template v-slot:prepend>
                          <v-icon>mdi-pencil</v-icon>
                        </template>
                        <v-list-item-title>Rename</v-list-item-title>
                      </v-list-item>
                      <v-list-item @click="deleteSection(item.id)" class="text-error">
                        <template v-slot:prepend>
                          <v-icon color="error">mdi-delete</v-icon>
                        </template>
                        <v-list-item-title>Delete</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </template>
              </v-treeview>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Test Cases -->
        <v-col cols="12" md="9">
          <v-card v-if="selectedSection">
            <v-card-title class="d-flex align-center flex-wrap py-3">
              <v-icon class="mr-2">mdi-test-tube</v-icon>
              {{ selectedSection.name }}
              <v-chip size="small" class="ml-2" color="primary">{{ filteredTestCases.length }}</v-chip>
              <v-spacer />
              <v-text-field
                v-model="caseSearch"
                label="Search cases"
                prepend-inner-icon="mdi-magnify"
                density="compact"
                hide-details
                variant="outlined"
                class="mr-2 mt-2 mt-md-0"
                style="max-width: 260px"
                clearable
              />
              <v-btn
                size="small"
                variant="outlined"
                prepend-icon="mdi-playlist-plus"
                class="mr-2 mt-2 mt-md-0"
                @click="openAddExistingCase = true; loadExistingCases()"
              >
                Existing
              </v-btn>
              <v-btn
                size="small"
                color="primary"
                prepend-icon="mdi-plus"
                class="mt-2 mt-md-0"
                @click="openAddCase = true"
              >
                New
              </v-btn>
            </v-card-title>
            <v-divider />
            <v-card-text class="pa-0">
              <v-list density="compact">
                <v-list-item
                  v-for="tc in filteredTestCases"
                  :key="tc.id"
                  class="case-item"
                  @click="openCaseDialog(tc.id)"
                >
                  <template v-slot:prepend>
                    <v-icon :color="typeColor(tc.type)">{{ typeIcon(tc.type) }}</v-icon>
                  </template>
                  <v-list-item-title class="font-weight-medium">
                    {{ tc.title }}
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip size="x-small" :color="statusColor(tc.status)" class="mr-1">
                      {{ tc.status }}
                    </v-chip>
                    <span v-if="tc.short_name" class="text-caption text-medium-emphasis">
                      {{ tc.short_name }}
                    </span>
                  </v-list-item-subtitle>
                  <template v-slot:append>
                    <v-btn
                      icon="mdi-link-off"
                      size="x-small"
                      variant="text"
                      color="grey"
                      @click.prevent="removeCaseFromSection(tc.id)"
                      title="Remove from section"
                    />
                  </template>
                </v-list-item>
              </v-list>
              <v-empty-state
                v-if="filteredTestCases.length === 0"
                icon="mdi-test-tube-off"
                text="No test cases in this section"
              />
            </v-card-text>
          </v-card>

          <v-card v-else class="text-center pa-10" variant="outlined">
            <v-icon size="64" color="grey-lighten-1">mdi-shape-outline</v-icon>
            <div class="text-h6 text-grey mt-4">Select a section to view test cases</div>
            <div class="text-body-2 text-grey mt-1">
              Choose a section from the left panel or create a new one
            </div>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Add / Rename Section Dialog -->
    <v-dialog v-model="sectionDialog.open" max-width="450">
      <v-card>
        <v-card-title>{{ sectionDialog.isRename ? 'Rename Section' : (sectionDialog.parentId ? 'Add Sub-Section' : 'Add Section') }}</v-card-title>
        <v-card-text>
          <v-text-field v-model="sectionDialog.name" label="Name" required autofocus />
          <v-textarea v-model="sectionDialog.description" label="Description (optional)" rows="2" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="sectionDialog.open = false">Cancel</v-btn>
          <v-btn color="primary" @click="saveSection">{{ sectionDialog.isRename ? 'Save' : 'Add' }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Add Existing Cases Dialog -->
    <v-dialog v-model="openAddExistingCase" max-width="560">
      <v-card>
        <v-card-title>Add Existing Test Cases</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="existingCaseSearch"
            label="Search"
            prepend-inner-icon="mdi-magnify"
            density="compact"
            hide-details
            class="mb-3"
            clearable
            autofocus
          />
          <v-list density="compact" style="max-height: 400px; overflow-y: auto;">
            <v-list-item
              v-for="tc in filteredExistingCases"
              :key="tc.id"
              :value="tc.id"
            >
              <template v-slot:prepend>
                <v-checkbox-btn
                  v-model="selectedExistingCases"
                  :value="tc.id"
                />
              </template>
              <v-list-item-title>{{ tc.title }}</v-list-item-title>
              <v-list-item-subtitle>
                <v-chip size="x-small" :color="typeColor(tc.type)">{{ tc.type }}</v-chip>
                <span class="text-caption text-medium-emphasis ml-1">{{ tc.status }}</span>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="openAddExistingCase = false">Cancel</v-btn>
          <v-btn
            color="primary"
            :disabled="selectedExistingCases.length === 0"
            @click="addExistingCases"
          >
            Add {{ selectedExistingCases.length ? `(${selectedExistingCases.length})` : '' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

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

    <!-- Add New Test Case Dialog -->
    <v-dialog v-model="openAddCase" max-width="500">
      <v-card>
        <v-card-title>Add Test Case</v-card-title>
        <v-card-text>
          <v-text-field v-model="newCase.title" label="Title" required autofocus />
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
          <v-btn variant="text" @click="openAddCase = false">Cancel</v-btn>
          <v-btn color="primary" @click="addTestCase">Add</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from "axios";
import EditorComponent from "@/components/common/editor/editorComponent.vue";
import BreadcrumbsComponent from "@/components/common/breadcrumbsComponent.vue";

export default {
  name: "testSuiteDetailComponent",
  components: { EditorComponent, BreadcrumbsComponent },
  data: () => ({
    suite: {},
    sectionTree: [],
    flatSections: [],
    selectedSection: null,
    testCases: [],
    allCases: [],
    spaceId: undefined,
    suiteId: undefined,
    loader: true,
    caseSearch: '',
    openAddCase: false,
    openAddExistingCase: false,
    existingCases: [],
    selectedExistingCases: [],
    existingCaseSearch: '',
    newCase: { title: '', type: 'manual', steps: '' },
    sectionDialog: {
      open: false,
      isRename: false,
      id: null,
      parentId: null,
      name: '',
      description: ''
    },
    caseDialogOpen: false,
    selectedCase: null,
    breadcrumbItems: [],
    editingSectionId: null,
    editingSectionName: ''
  }),
  computed: {
    filteredTestCases() {
      const q = this.caseSearch.toLowerCase().trim();
      if (!q) return this.testCases;
      return this.testCases.filter(tc =>
        tc.title?.toLowerCase().includes(q) ||
        tc.short_name?.toLowerCase().includes(q)
      );
    },
    filteredExistingCases() {
      const q = this.existingCaseSearch.toLowerCase().trim();
      if (!q) return this.existingCases;
      return this.existingCases.filter(tc => tc.title?.toLowerCase().includes(q));
    }
  },
  mounted() {
    this.spaceId = this.$route.params.spaceId;
    this.suiteId = this.$route.params.suiteId;
    this.loadSuite();
    this.loadSections();
    this.loadAllCases();
  },
  methods: {
    loadSuite() {
      axios.get(`/api/v2/test-suite/${this.suiteId}`).then(res => {
        this.suite = res.data;
        this.breadcrumbItems = [
          { title: 'Test Suites', to: `/space/${this.spaceId}/test-suites` },
          { title: this.suite.name }
        ];
        this.loader = false;
      });
    },
    loadSections() {
      axios.get(`/api/v2/section/suite/${this.suiteId}/tree`).then(res => {
        this.sectionTree = res.data;
        this.flatSections = this.flattenTree(res.data);
      });
    },
    loadAllCases() {
      axios.get(`/api/v2/test-case/suite/${this.suiteId}`).then(res => {
        this.allCases = res.data;
      }).catch(() => {
        this.allCases = [];
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
    caseCountByType(type) {
      return this.allCases.filter(tc => tc.type === type).length;
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
    openSectionDialog(parentId = null) {
      this.sectionDialog = {
        open: true,
        isRename: false,
        id: null,
        parentId,
        name: '',
        description: ''
      };
    },
    openRenameDialog(item) {
      this.sectionDialog = {
        open: true,
        isRename: true,
        id: item.id,
        parentId: null,
        name: item.name,
        description: item.description || ''
      };
    },
    saveSection() {
      if (this.sectionDialog.isRename) {
        axios.patch(`/api/v2/section/${this.sectionDialog.id}`, {
          name: this.sectionDialog.name,
          description: this.sectionDialog.description || null
        }).then(() => {
          this.sectionDialog.open = false;
          this.loadSections();
        });
      } else {
        axios.post('/api/v2/section/', {
          name: this.sectionDialog.name,
          description: this.sectionDialog.description || null,
          suite_id: this.suiteId,
          parent_id: this.sectionDialog.parentId
        }).then(() => {
          this.sectionDialog.open = false;
          this.loadSections();
        });
      }
    },
    deleteSection(id) {
      if (!confirm('Delete this section? Test cases will remain but become unassigned.')) return;
      axios.delete(`/api/v2/section/${id}`).then(() => {
        this.selectedSection = null;
        this.testCases = [];
        this.loadSections();
        this.loadAllCases();
      });
    },
    removeCaseFromSection(id) {
      axios.patch(`/api/v2/test-case/${id}`, {
        section_id: null,
        suite_id: null
      }).then(() => {
        this.loadTestCases(this.selectedSection.id);
        this.loadAllCases();
      });
    },
    loadExistingCases() {
      axios.get(`/api/v2/test-case/space/${this.spaceId}`).then(res => {
        const currentIds = new Set(this.testCases.map(tc => tc.id));
        this.existingCases = res.data.filter(tc => !currentIds.has(tc.id));
        this.selectedExistingCases = [];
      });
    },
    addExistingCases() {
      const promises = this.selectedExistingCases.map(id =>
        axios.patch(`/api/v2/test-case/${id}`, {
          suite_id: this.suiteId,
          section_id: this.selectedSection.id
        })
      );
      Promise.all(promises).then(() => {
        this.openAddExistingCase = false;
        this.loadTestCases(this.selectedSection.id);
        this.loadAllCases();
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
        this.loadAllCases();
      });
    },
    openCaseDialog(id) {
      axios.get(`/api/v2/test-case/${id}`).then(res => {
        this.selectedCase = res.data;
        this.caseDialogOpen = true;
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
    },
    startInlineRename(item) {
      this.editingSectionId = item.id;
      this.editingSectionName = item.name;
    },
    saveInlineRename() {
      if (!this.editingSectionId) return;
      axios.patch(`/api/v2/section/${this.editingSectionId}`, {
        name: this.editingSectionName
      }).then(() => {
        this.editingSectionId = null;
        this.editingSectionName = '';
        this.loadSections();
      });
    },
    cancelInlineRename() {
      this.editingSectionId = null;
      this.editingSectionName = '';
    }
  }
}
</script>

<style scoped>
.section-tree :deep(.v-treeview-item) {
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
