<template>
  <div>
    <v-toolbar density="compact">
      <v-text-field
        v-model="search"
        prepend-inner-icon="mdi-magnify"
        label="Search test cases"
        density="compact"
        hide-details
        variant="solo"
        class="mx-2"
        clearable
        @update:model-value="onSearch"
        style="max-width: 260px"
      />
      <v-select
        v-model="filterType"
        :items="[{title:'All', value:''}, {title:'Manual', value:'manual'}, {title:'Checklist', value:'checklist'}, {title:'Automated', value:'automated'}]"
        item-title="title"
        item-value="value"
        label="Type"
        density="compact"
        hide-details
        variant="solo"
        class="mx-2"
        style="max-width: 140px"
        @update:model-value="onFilterChange"
      />
      <v-select
        v-model="filterStatus"
        :items="[{title:'All', value:''}, {title:'Draft', value:'draft'}, {title:'Active', value:'active'}, {title:'Deprecated', value:'deprecated'}]"
        item-title="title"
        item-value="value"
        label="Status"
        density="compact"
        hide-details
        variant="solo"
        class="mx-2"
        style="max-width: 140px"
        @update:model-value="onFilterChange"
      />
      <v-spacer />
      <v-btn v-if="selectedCases.length" size="small" variant="text" color="error" class="mr-2" @click="bulkDelete">
        Delete ({{ selectedCases.length }})
      </v-btn>
      <v-btn v-if="selectedCases.length" size="small" variant="text" class="mr-2" @click="bulkStatusDialog = true">
        Change Status ({{ selectedCases.length }})
      </v-btn>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate = true">
        New Test Case
      </v-btn>
    </v-toolbar>

    <v-data-table-server
      v-model="selectedCases"
      v-model:items-per-page="itemsPerPage"
      v-model:page="page"
      :headers="headers"
      :items="cases"
      :items-length="totalCases"
      :loading="tableLoading"
      :sort-by="sortBy"
      hover
      show-select
      item-value="id"
      @update:options="loadCases"
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
    </v-data-table-server>

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

    <v-dialog v-model="bulkStatusDialog" max-width="300">
      <v-card>
        <v-card-title>Change Status</v-card-title>
        <v-card-text>
          <v-select
            v-model="bulkStatus"
            :items="['draft','active','deprecated']"
            label="New Status"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="bulkStatusDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="bulkChangeStatus">Apply</v-btn>
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
    totalCases: 0,
    page: 1,
    itemsPerPage: 25,
    sortBy: [{ key: 'created_at', order: 'desc' }],
    spaceId: undefined,
    tableLoading: false,
    search: '',
    filterType: '',
    filterStatus: '',
    searchDebounce: null,
    openCreate: false,
    newCase: { title: '', type: 'manual', steps: '', expected_results: '', preconditions: '' },
    selectedCases: [],
    bulkStatusDialog: false,
    bulkStatus: 'active',
    headers: [
      { title: 'Title', key: 'title', sortable: true },
      { title: 'Type', key: 'type', width: '120px', sortable: true },
      { title: 'Status', key: 'status', width: '120px', sortable: true },
      { title: 'Short Name', key: 'short_name', sortable: true },
      { title: 'Updated', key: 'updated_at', width: '150px', sortable: true }
    ]
  }),
  created() {
    this.spaceId = this.$route.params.spaceId;
    const q = this.$route.query;
    this.page = parseInt(q.page) || 1;
    this.itemsPerPage = parseInt(q.page_size) || 25;
    this.search = q.search || '';
    this.filterType = q.type || '';
    this.filterStatus = q.status || '';
    if (q.sort_by && q.sort_order) {
      this.sortBy = [{ key: q.sort_by, order: q.sort_order }];
    }
  },
  methods: {
    loadCases(options) {
      if (!this.spaceId) return;
      this.tableLoading = true;
      const page = options?.page || this.page;
      const pageSize = options?.itemsPerPage || this.itemsPerPage;
      const sortBy = options?.sortBy?.[0];
      const sortKey = sortBy?.key || 'created_at';
      const sortOrder = sortBy?.order || 'desc';

      // Update URL
      const query = { page, page_size: pageSize };
      if (this.search) query.search = this.search;
      if (this.filterType) query.type = this.filterType;
      if (this.filterStatus) query.status = this.filterStatus;
      if (sortKey !== 'created_at' || sortOrder !== 'desc') {
        query.sort_by = sortKey;
        query.sort_order = sortOrder;
      }
      this.$router.replace({ query });

      axios.get(`/api/v2/test-case/space/${this.spaceId}`, {
        params: {
          page,
          page_size: pageSize,
          sort_by: sortKey,
          sort_order: sortOrder,
          search: this.search || undefined,
          type: this.filterType || undefined,
          status: this.filterStatus || undefined
        }
      }).then(res => {
        this.cases = res.data.items;
        this.totalCases = res.data.total;
        this.page = res.data.page;
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
        this.loadCases({ page: 1, itemsPerPage: this.itemsPerPage, sortBy: this.sortBy });
      }, 400);
    },
    onFilterChange() {
      this.page = 1;
      this.loadCases({ page: 1, itemsPerPage: this.itemsPerPage, sortBy: this.sortBy });
    },
    createCase() {
      axios.post('/api/v2/test-case/', {
        ...this.newCase,
        space_id: this.spaceId
      }).then(() => {
        this.openCreate = false;
        this.newCase = { title: '', type: 'manual', steps: '', expected_results: '', preconditions: '' };
        this.loadCases({ page: this.page, itemsPerPage: this.itemsPerPage, sortBy: this.sortBy });
      });
    },
    bulkDelete() {
      if (!confirm(`Delete ${this.selectedCases.length} test cases?`)) return;
      Promise.all(this.selectedCases.map(id => axios.delete(`/api/v2/test-case/${id}`)))
        .then(() => {
          this.selectedCases = [];
          this.loadCases({ page: this.page, itemsPerPage: this.itemsPerPage, sortBy: this.sortBy });
        });
    },
    bulkChangeStatus() {
      Promise.all(this.selectedCases.map(id =>
        axios.patch(`/api/v2/test-case/${id}`, { status: this.bulkStatus })
      )).then(() => {
        this.selectedCases = [];
        this.bulkStatusDialog = false;
        this.loadCases({ page: this.page, itemsPerPage: this.itemsPerPage, sortBy: this.sortBy });
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
