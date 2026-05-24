<template>
  <v-container fluid>
    <v-row align="center" class="mb-2">
      <v-col>
        <h1 class="text-h4 font-weight-bold">Test Plans</h1>
      </v-col>
      <v-col cols="auto">
        <v-btn color="primary" prepend-icon="mdi-plus" @click="openDialog = true">
          New Plan
        </v-btn>
      </v-col>
    </v-row>

    <v-data-table-server
      v-model:items-per-page="pageSize"
      :headers="headers"
      :items="plans"
      :items-length="total"
      :loading="loading"
      item-value="id"
      @update:options="loadPlans"
    >
      <template v-slot:item.name="{ item }">
        <router-link :to="`/space/${spaceId}/test-plans/${item.id}`" class="font-weight-medium">
          {{ item.name }}
        </router-link>
      </template>
      <template v-slot:item.suite="{ item }">
        {{ item.suite?.name || '-' }}
      </template>
      <template v-slot:item.actions="{ item }">
        <v-btn icon size="small" variant="text" :to="`/space/${spaceId}/test-plans/${item.id}`">
          <v-icon>mdi-eye</v-icon>
        </v-btn>
        <v-btn icon size="small" variant="text" @click="deletePlan(item.id)">
          <v-icon color="error">mdi-delete</v-icon>
        </v-btn>
      </template>
    </v-data-table-server>

    <!-- Create Dialog -->
    <v-dialog v-model="openDialog" max-width="500">
      <v-card>
        <v-card-title>Create Test Plan</v-card-title>
        <v-card-text>
          <v-text-field v-model="newPlan.name" label="Name" required autofocus />
          <v-textarea v-model="newPlan.description" label="Description" rows="2" />
          <v-select
            v-model="newPlan.suite_id"
            :items="suites"
            item-title="name"
            item-value="id"
            label="Suite (optional)"
            clearable
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="openDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="createPlan">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from "axios";

export default {
  name: "testPlansListComponent",
  data: () => ({
    spaceId: undefined,
    plans: [],
    suites: [],
    total: 0,
    page: 1,
    pageSize: 25,
    loading: false,
    openDialog: false,
    newPlan: { name: '', description: '', suite_id: null }
  }),
  computed: {
    headers() {
      return [
        { title: 'Name', key: 'name', sortable: false },
        { title: 'Suite', key: 'suite', sortable: false },
        { title: 'Description', key: 'description', sortable: false },
        { title: 'Created', key: 'created_at', sortable: false },
        { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
      ];
    }
  },
  mounted() {
    this.spaceId = this.$route.params.spaceId;
    this.loadSuites();
  },
  methods: {
    async loadPlans({ page, itemsPerPage }) {
      this.loading = true;
      this.page = page;
      this.pageSize = itemsPerPage;
      try {
        const res = await axios.get(`/api/v2/test-plan/space/${this.spaceId}`, {
          params: { page, page_size: itemsPerPage }
        });
        this.plans = res.data.items;
        this.total = res.data.total;
      } catch (e) {
        console.error(e);
      } finally {
        this.loading = false;
      }
    },
    async loadSuites() {
      try {
        const res = await axios.get(`/api/v2/test-suite/space/${this.spaceId}`, {
          params: { page: 1, page_size: 1000 }
        });
        this.suites = res.data.items;
      } catch (e) {
        console.error(e);
      }
    },
    async createPlan() {
      try {
        await axios.post('/api/v2/test-plan/', {
          name: this.newPlan.name,
          description: this.newPlan.description,
          space_id: this.spaceId,
          suite_id: this.newPlan.suite_id
        });
        this.openDialog = false;
        this.newPlan = { name: '', description: '', suite_id: null };
        this.loadPlans({ page: this.page, itemsPerPage: this.pageSize });
      } catch (e) {
        console.error(e);
      }
    },
    async deletePlan(id) {
      if (!confirm('Delete this test plan?')) return;
      try {
        await axios.delete(`/api/v2/test-plan/${id}`);
        this.loadPlans({ page: this.page, itemsPerPage: this.pageSize });
      } catch (e) {
        console.error(e);
      }
    }
  }
}
</script>
