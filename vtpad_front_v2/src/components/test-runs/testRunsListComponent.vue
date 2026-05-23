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
    </v-data-table-server>
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
    search: '',
    searchDebounce: null,
    optionsDebounce: null,
    headers: [
      { title: 'Name', key: 'name', sortable: true },
      { title: 'Status', key: 'status', width: '140px', sortable: true },
      { title: 'Created', key: 'created_at', width: '150px', sortable: true }
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
      const page = options?.page || this.page;
      const pageSize = options?.itemsPerPage || this.itemsPerPage;
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
        this.runs = res.data.items;
        this.totalRuns = res.data.total;
        this.itemsPerPage = res.data.page_size;
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
    }
  }
}
</script>
