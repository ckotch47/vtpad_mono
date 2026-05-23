<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>

  <div v-else>
    <v-toolbar density="compact">
      <v-text-field
        v-model="search"
        prepend-inner-icon="mdi-magnify"
        label="Search test cases"
        density="compact"
        hide-details
        variant="solo"
        class="mx-2"
      />
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate = true">
        New Test Case
      </v-btn>
    </v-toolbar>

    <v-data-table
      :headers="headers"
      :items="filteredCases"
      :items-per-page="25"
      hover
      @click:row="(event, { item }) => $router.push(`/space/${spaceId}/test-cases/${item.id}`)"
    >
      <template v-slot:item.type="{ item }">
        <v-chip size="small" :color="typeColor(item.type)">{{ item.type }}</v-chip>
      </template>
      <template v-slot:item.status="{ item }">
        <v-chip size="small" :color="statusColor(item.status)">{{ item.status }}</v-chip>
      </template>
      <template v-slot:item.updated_at="{ item }">
        {{ formatDate(item.updated_at) }}
      </template>
    </v-data-table>

    <v-dialog v-model="openCreate" max-width="700">
      <v-card>
        <v-card-title>Create Test Case</v-card-title>
        <v-card-text>
          <v-text-field v-model="newCase.title" label="Title" required />
          <v-select
            v-model="newCase.type"
            :items="['manual','checklist','automated']"
            label="Type"
          />
          <v-textarea v-model="newCase.steps" label="Steps" rows="4" />
          <v-textarea v-model="newCase.expected_results" label="Expected Results" rows="3" />
          <v-textarea v-model="newCase.preconditions" label="Preconditions" rows="2" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="openCreate = false">Cancel</v-btn>
          <v-btn color="primary" @click="createCase">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "testCasesListComponent",
  data: () => ({
    cases: [],
    spaceId: undefined,
    loader: true,
    search: '',
    openCreate: false,
    newCase: { title: '', type: 'manual', steps: '', expected_results: '', preconditions: '' },
    headers: [
      { title: 'Title', key: 'title' },
      { title: 'Type', key: 'type', width: '120px' },
      { title: 'Status', key: 'status', width: '120px' },
      { title: 'Short Name', key: 'short_name' },
      { title: 'Updated', key: 'updated_at', width: '150px' }
    ]
  }),
  computed: {
    filteredCases() {
      if (!this.search) return this.cases;
      const q = this.search.toLowerCase();
      return this.cases.filter(c =>
        (c.title && c.title.toLowerCase().includes(q)) ||
        (c.short_name && c.short_name.toLowerCase().includes(q))
      );
    }
  },
  mounted() {
    this.spaceId = this.$route.params.spaceId;
    this.loadCases();
  },
  methods: {
    loadCases() {
      axios.get(`/api/v2/test-case/space/${this.spaceId}`).then(res => {
        this.cases = res.data;
        this.loader = false;
      }).catch(() => { this.loader = false; });
    },
    createCase() {
      axios.post('/api/v2/test-case/', {
        ...this.newCase,
        space_id: this.spaceId
      }).then(() => {
        this.openCreate = false;
        this.newCase = { title: '', type: 'manual', steps: '', expected_results: '', preconditions: '' };
        this.loadCases();
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
