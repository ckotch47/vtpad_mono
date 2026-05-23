<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>

  <v-list v-if="!loader">
    <v-list-item
      v-for="suite in suites"
      :key="suite.id"
      :value="suite.id"
      @click="$router.push(`/space/${spaceId}/test-suites/${suite.id}`)"
    >
      <template v-slot:prepend>
        <v-icon icon="mdi-book-open-variant" />
      </template>
      <v-list-item-title>{{ suite.name }}</v-list-item-title>
      <v-list-item-subtitle v-if="suite.description">{{ suite.description }}</v-list-item-subtitle>
    </v-list-item>

    <v-divider class="my-2" />

    <v-list-item @click="openCreate = true">
      <template v-slot:prepend>
        <v-icon icon="mdi-plus" color="primary" />
      </template>
      <v-list-item-title class="text-primary">Create Test Suite</v-list-item-title>
    </v-list-item>
  </v-list>

  <v-dialog v-model="openCreate" max-width="500">
    <v-card>
      <v-card-title>Create Test Suite</v-card-title>
      <v-card-text>
        <v-text-field v-model="newSuite.name" label="Name" required />
        <v-textarea v-model="newSuite.description" label="Description" rows="2" />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="openCreate = false">Cancel</v-btn>
        <v-btn color="primary" @click="createSuite">Create</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from "axios";

export default {
  name: "testSuitesListComponent",
  data: () => ({
    suites: [],
    spaceId: undefined,
    loader: true,
    openCreate: false,
    newSuite: { name: '', description: '' }
  }),
  mounted() {
    this.spaceId = this.$route.params.spaceId;
    this.loadSuites();
  },
  methods: {
    loadSuites() {
      this.loader = true;
      axios.get(`/api/v2/test-suite/space/${this.spaceId}`).then(res => {
        this.suites = res.data;
        this.loader = false;
      }).catch(() => { this.loader = false; });
    },
    createSuite() {
      axios.post('/api/v2/test-suite/', {
        name: this.newSuite.name,
        description: this.newSuite.description,
        space_id: this.spaceId
      }).then(res => {
        this.suites.push(res.data);
        this.openCreate = false;
        this.newSuite = { name: '', description: '' };
      });
    }
  }
}
</script>
