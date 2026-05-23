<template>
  <div>
    <v-toolbar density="compact">
      <v-text-field
        v-model="search"
        prepend-inner-icon="mdi-magnify"
        label="Search test runs"
        density="compact"
        hide-details
        variant="solo"
        class="mx-2"
        clearable
        @update:model-value="onSearch"
      />
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreateDialog">
        New Test Run
      </v-btn>
    </v-toolbar>

    <v-data-table-server
      v-model:items-per-page="itemsPerPage"
      :headers="headers"
      :items="runs"
      :items-length="totalRuns"
      :loading="tableLoading"
      :page="page"
      hover
      @update:options="loadRuns"
      @click:row="(event, { item }) => $router.push(`/space/${spaceId}/test-runs/${item.id}`)"
    >
      <template v-slot:item.status="{ item }">
        <v-icon :color="statusColor(item.status)">{{ statusIcon(item.status) }}</v-icon>
        <span class="ml-1 text-capitalize">{{ item.status }}</span>
      </template>
      <template v-slot:item.created_at="{ item }">
        {{ formatDate(item.created_at) }}
      </template>
      <template v-slot:item.actions="{ item }">
        <v-btn icon="mdi-delete" size="x-small" variant="text" color="error" @click.stop="deleteRun(item)" />
      </template>
    </v-data-table-server>

    <v-dialog v-model="openCreate" max-width="500">
      <v-card>
        <v-card-title>Create Test Run</v-card-title>
        <v-card-text>
          <v-text-field v-model="newRun.name" label="Name" required autofocus />
          <v-textarea v-model="newRun.description" label="Description" rows="2" />
          <v-select
            v-model="newRun.suite_id"
            :items="suites"
            item-title="name"
            item-value="id"
            label="Test Suite"
            required
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="openCreate = false">Cancel</v-btn>
          <v-btn color="primary" @click="createRun">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "testRunsListComponent",
  data: () => ({
    runs: [],
    totalRuns: 0,
    page: 1,
    itemsPerPage: 25,
    spaceId: undefined,
    tableLoading: false,
    firstLoad: true,
    search: '',
    searchDebounce: null,
    optionsDebounce: null,
    openCreate: false,
    suites: [],
    newRun: { name: '', description: '', suite_id: null },
    headers: [
      { title: 'Name', key: 'name', sortable: true },
      { title: 'Status', key: 'status', width: '140px', sortable: true },
      { title: 'Created', key: 'created_at', width: '150px', sortable: true },
      { title: 'Actions', key: 'actions', width: '100px', sortable: false }
    ]
  }),
  created() {
    this.spaceId = this.$route.params.spaceId;
  },
  methods: {
    loadRuns(options) {
      clearTimeout(this.optionsDebounce);
      this.optionsDebounce = setTimeout(() => {
        this._doLoadRuns(options);
      }, 150);
    },
    _doLoadRuns(options) {
      if (!this.spaceId || this.tableLoading) return;
      this.tableLoading = true;
      const page = this.firstLoad ? this.page : (options?.page || this.page);
      const pageSize = this.firstLoad ? this.itemsPerPage : (options?.itemsPerPage || this.itemsPerPage);
      this.firstLoad = false;
      const sortBy = options?.sortBy?.[0];
      const sortKey = sortBy?.key || 'created_at';
      const sortOrder = sortBy?.order || 'desc';

      axios.get(`/api/v2/test-run/space/${this.spaceId}`, {
        params: {
          page,
          page_size: pageSize,
          sort_by: sortKey,
          sort_order: sortOrder,
          search: this.search || undefined
        }
      }).then(res => {
        this.runs = res.data.items || res.data;
        this.totalRuns = res.data.total !== undefined ? res.data.total : (res.data.length || 0);
        this.itemsPerPage = res.data.page_size || this.itemsPerPage;
        this.tableLoading = false;
      }).catch(() => {
        this.tableLoading = false;
      });
    },
    onSearch() {
      clearTimeout(this.searchDebounce);
      this.searchDebounce = setTimeout(() => {
        this.page = 1;
        this.loadRuns({ page: 1, itemsPerPage: this.itemsPerPage, sortBy: [] });
      }, 400);
    },
    statusColor(status) {
      const map = { completed: 'success', active: 'primary', draft: 'grey' };
      return map[status] || 'grey';
    },
    statusIcon(status) {
      const map = { completed: 'mdi-check-circle', active: 'mdi-play-circle', draft: 'mdi-circle-outline' };
      return map[status] || 'mdi-circle-outline';
    },
    formatDate(date) {
      return date ? new Date(date).toLocaleDateString() : '';
    },
    openCreateDialog() {
      this.newRun = { name: '', description: '', suite_id: null };
      this.loadSuites();
      this.openCreate = true;
    },
    loadSuites() {
      axios.get(`/api/v2/test-suite/space/${this.spaceId}`, {
        params: { page: 1, page_size: 100, status: 'active' }
      }).then(res => {
        this.suites = res.data.items || [];
      });
    },
    createRun() {
      axios.post('/api/v2/test-run/', {
        name: this.newRun.name,
        description: this.newRun.description,
        suite_id: this.newRun.suite_id,
        space_id: this.spaceId
      }).then(() => {
        this.openCreate = false;
        this.loadRuns({ page: 1, itemsPerPage: this.itemsPerPage, sortBy: [] });
      });
    },
    deleteRun(item) {
      if (!confirm(`Delete test run "${item.name}"?`)) return;
      axios.delete(`/api/v2/test-run/${item.id}`).then(() => {
        this.loadRuns({ page: this.page, itemsPerPage: this.itemsPerPage, sortBy: [] });
      });
    }
  }
}
</script>
