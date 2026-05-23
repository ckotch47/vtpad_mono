<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>

  <v-list v-if="!loader">
    <v-list-item
      v-for="run in runs"
      :key="run.id"
      @click="$router.push(`/space/${spaceId}/test-runs/${run.id}`)"
    >
      <template v-slot:prepend>
        <v-icon v-if="run.status === 'completed'" icon="mdi-check-circle" color="success" />
        <v-icon v-else-if="run.status === 'active'" icon="mdi-play-circle" color="primary" />
        <v-icon v-else icon="mdi-circle-outline" color="grey" />
      </template>
      <v-list-item-title>{{ run.name }}</v-list-item-title>
      <v-list-item-subtitle>
        Status: {{ run.status }} | Created: {{ formatDate(run.created_at) }}
      </v-list-item-subtitle>
    </v-list-item>
  </v-list>
</template>

<script>
import axios from "axios";

export default {
  name: "testRunsListComponent",
  data: () => ({
    runs: [],
    spaceId: undefined,
    loader: true
  }),
  mounted() {
    this.spaceId = this.$route.params.spaceId;
    this.loadRuns();
  },
  methods: {
    loadRuns() {
      axios.get(`/api/v2/test-run/space/${this.spaceId}`).then(res => {
        this.runs = res.data;
        this.loader = false;
      }).catch(() => { this.loader = false; });
    },
    formatDate(date) {
      return date ? new Date(date).toLocaleDateString() : '';
    }
  }
}
</script>
