<template>
  <div>
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
      @click:row="(event, { item }) => $router.push(`/space/${spaceId}/test-plans/${item.id}`)"
    >
      <template v-slot:item.name="{ item }">
        <span class="font-weight-medium">{{ item.name }}</span>
      </template>
      <template v-slot:item.case_count="{ item }">
        <v-chip size="small" color="primary">{{ (item.case_ids || []).length }}</v-chip>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-btn icon size="small" variant="text" @click.stop="deletePlan(item.id)">
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
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="openDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="createPlan">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { testPlanService } from '@/services';

export default {
  name: "testPlansListComponent",
  data: () => ({
    spaceId: undefined,
    plans: [],
    total: 0,
    page: 1,
    pageSize: 25,
    loading: false,
    openDialog: false,
    newPlan: { name: '', description: '' }
  }),
  computed: {
    headers() {
      return [
        { title: 'Name', key: 'name', sortable: false },
        { title: 'Cases', key: 'case_count', sortable: false },
        { title: 'Description', key: 'description', sortable: false },
        { title: 'Created', key: 'created_at', sortable: false },
        { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
      ];
    }
  },
  created() {
    this.spaceId = this.$route.params.spaceId;
  },
  mounted() {
    // v-data-table-server triggers loadPlans on mount; spaceId must be set in created()
  },
  methods: {
    async loadPlans({ page, itemsPerPage }) {
      if (!this.spaceId || this.spaceId === 'undefined') return;
      this.loading = true;
      this.page = page;
      this.pageSize = itemsPerPage;
      try {
        const res = await testPlanService.listBySpace(this.spaceId, { page, page_size: itemsPerPage });
        this.plans = res.data.items;
        this.total = res.data.total;
      } catch (e) {
        console.error(e);
      } finally {
        this.loading = false;
      }
    },
    async createPlan() {
      try {
        await testPlanService.create({
          name: this.newPlan.name,
          description: this.newPlan.description,
          space_id: this.spaceId
        });
        this.openDialog = false;
        this.newPlan = { name: '', description: '' };
        this.loadPlans({ page: this.page, itemsPerPage: this.pageSize });
      } catch (e) {
        console.error(e);
      }
    },
    async deletePlan(id) {
      if (!confirm('Delete this test plan?')) return;
      try {
        await testPlanService.delete(id);
        this.loadPlans({ page: this.page, itemsPerPage: this.pageSize });
      } catch (e) {
        console.error(e);
      }
    }
  }
}
</script>
