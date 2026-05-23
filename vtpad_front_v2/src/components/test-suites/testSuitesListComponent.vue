<template>
  <div>
    <v-toolbar density="compact">
      <v-text-field
        v-model="search"
        prepend-inner-icon="mdi-magnify"
        label="Search test suites"
        density="compact"
        hide-details
        variant="solo"
        class="mx-2"
        clearable
        @update:model-value="onSearch"
        style="max-width: 260px"
      />
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate = true">
        New Test Suite
      </v-btn>
    </v-toolbar>

    <v-data-table-server
      v-model:items-per-page="itemsPerPage"
      v-model:page="page"
      :headers="headers"
      :items="suites"
      :items-length="totalSuites"
      :loading="tableLoading"
      :sort-by="sortBy"
      hover
      @update:options="loadSuites"
      @click:row="(event, { item }) => $router.push(`/space/${spaceId}/test-suites/${item.id}`)"
    >
      <template v-slot:item.name="{ item }">
        <div class="font-weight-medium">{{ item.name }}</div>
        <div v-if="item.description" class="text-caption text-medium-emphasis text-truncate" style="max-width: 400px">
          {{ item.description }}
        </div>
      </template>
      <template v-slot:item.cases_count="{ item }">
        <v-chip size="small" color="primary">{{ item.cases_count || 0 }}</v-chip>
      </template>
      <template v-slot:item.sections_count="{ item }">
        <v-chip size="small" color="info">{{ item.sections_count || 0 }}</v-chip>
      </template>
      <template v-slot:item.created_at="{ item }">
        {{ formatDate(item.created_at) }}
      </template>
    </v-data-table-server>

    <v-dialog v-model="openCreate" max-width="500">
      <v-card>
        <v-card-title>Create Test Suite</v-card-title>
        <v-card-text>
          <v-text-field v-model="newSuite.name" label="Name" required autofocus />
          <v-textarea v-model="newSuite.description" label="Description" rows="2" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="openCreate = false">Cancel</v-btn>
          <v-btn color="primary" @click="createSuite">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "testSuitesListComponent",
  data: () => ({
    suites: [],
    totalSuites: 0,
    page: 1,
    itemsPerPage: 25,
    sortBy: [{ key: 'created_at', order: 'desc' }],
    spaceId: undefined,
    tableLoading: false,
    firstLoad: true,
    search: '',
    searchDebounce: null,
    optionsDebounce: null,
    openCreate: false,
    newSuite: { name: '', description: '' },
    headers: [
      { title: 'Name', key: 'name', sortable: true },
      { title: 'Cases', key: 'cases_count', width: '100px', sortable: false },
      { title: 'Sections', key: 'sections_count', width: '100px', sortable: false },
      { title: 'Created', key: 'created_at', width: '150px', sortable: true }
    ]
  }),
  created() {
    this.spaceId = this.$route.params.spaceId;
    const q = this.$route.query;
    this.page = parseInt(q.page) || 1;
    this.itemsPerPage = parseInt(q.page_size) || 25;
    this.search = q.search || '';
    if (q.sort_by && q.sort_order) {
      this.sortBy = [{ key: q.sort_by, order: q.sort_order }];
    }
  },
  methods: {
    loadSuites(options) {
      clearTimeout(this.optionsDebounce);
      this.optionsDebounce = setTimeout(() => {
        this._doLoadSuites(options);
      }, 150);
    },
    _doLoadSuites(options) {
      if (!this.spaceId || this.tableLoading) return;
      this.tableLoading = true;
      const page = this.firstLoad ? this.page : (options?.page || this.page);
      const pageSize = this.firstLoad ? this.itemsPerPage : (options?.itemsPerPage || this.itemsPerPage);
      this.firstLoad = false;
      const sortBy = options?.sortBy?.[0];
      const sortKey = sortBy?.key || 'created_at';
      const sortOrder = sortBy?.order || 'desc';

      const query = { page, page_size: pageSize };
      if (this.search) query.search = this.search;
      if (sortKey !== 'created_at' || sortOrder !== 'desc') {
        query.sort_by = sortKey;
        query.sort_order = sortOrder;
      }
      this.$router.replace({ query });

      axios.get(`/api/v2/test-suite/space/${this.spaceId}`, {
        params: {
          page,
          page_size: pageSize,
          sort_by: sortKey,
          sort_order: sortOrder,
          search: this.search || undefined
        }
      }).then(res => {
        this.suites = res.data.items;
        this.totalSuites = res.data.total;
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
        this.loadSuites({ page: 1, itemsPerPage: this.itemsPerPage, sortBy: this.sortBy });
      }, 400);
    },
    createSuite() {
      axios.post('/api/v2/test-suite/', {
        name: this.newSuite.name,
        description: this.newSuite.description,
        space_id: this.spaceId
      }).then(() => {
        this.openCreate = false;
        this.newSuite = { name: '', description: '' };
        this.loadSuites({ page: this.page, itemsPerPage: this.itemsPerPage, sortBy: this.sortBy });
      });
    },
    formatDate(date) {
      return date ? new Date(date).toLocaleDateString() : '';
    }
  }
}
</script>
