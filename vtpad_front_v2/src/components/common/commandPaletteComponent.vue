<template>
  <v-dialog v-model="isOpen" max-width="600" scrollable @keydown.esc="close">
    <v-card>
      <v-card-text class="pa-2">
        <v-text-field
          v-model="query"
          prepend-inner-icon="mdi-magnify"
          placeholder="Search cases, suites, runs, plans..."
          variant="solo"
          hide-details
          autofocus
          @keydown.enter="selectFirst"
        />

        <v-list density="compact" class="mt-2" style="max-height: 400px; overflow-y: auto;">
          <template v-if="results.length">
            <v-list-subheader>{{ results.length }} results</v-list-subheader>
            <v-list-item
              v-for="item in results"
              :key="item.id + item.type"
              @click="navigate(item)"
              class="command-item"
            >
              <template v-slot:prepend>
                <v-icon :color="item.color">{{ item.icon }}</v-icon>
              </template>
              <v-list-item-title>{{ item.title }}</v-list-item-title>
              <v-list-item-subtitle>{{ item.subtitle }}</v-list-item-subtitle>
              <template v-slot:append>
                <v-chip size="x-small" :color="item.color" variant="outlined">{{ item.type }}</v-chip>
              </template>
            </v-list-item>
          </template>
          <v-empty-state
            v-else-if="query.length > 1"
            icon="mdi-magnify"
            text="No results found"
          />
        </v-list>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from "axios";

export default {
  name: "commandPaletteComponent",
  data: () => ({
    isOpen: false,
    query: '',
    searchTimer: null,
    results: []
  }),
  mounted() {
    document.addEventListener('keydown', this.onKeyDown);
  },
  beforeUnmount() {
    document.removeEventListener('keydown', this.onKeyDown);
  },
  methods: {
    onKeyDown(e) {
      // Cmd+K or Ctrl+K
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        this.open();
      }
    },
    open() {
      this.isOpen = true;
      this.query = '';
      this.results = [];
    },
    close() {
      this.isOpen = false;
    },
    selectFirst() {
      if (this.results.length) {
        this.navigate(this.results[0]);
      }
    },
    navigate(item) {
      this.close();
      this.$router.push(item.to);
    }
  },
  watch: {
    query(val) {
      clearTimeout(this.searchTimer);
      if (!val || val.length < 2) {
        this.results = [];
        return;
      }
      this.searchTimer = setTimeout(() => {
        this.doSearch(val);
      }, 200);
    }
  },
  methods: {
    async doSearch(q) {
      const spaceId = this.$route.params.spaceId;
      if (!spaceId) return;

      const results = [];

      // Search test cases
      try {
        const casesRes = await axios.get(`/api/v2/test-case/space/${spaceId}`, {
          params: { search: q, page: 1, page_size: 5 }
        });
        (casesRes.data.items || []).forEach(c => {
          results.push({
            id: c.id,
            type: 'Case',
            title: c.title,
            subtitle: c.short_name || '',
            icon: 'mdi-test-tube',
            color: 'primary',
            to: `/space/${spaceId}/test-cases/${c.id}`
          });
        });
      } catch (e) { /* ignore */ }

      // Search suites
      try {
        const suitesRes = await axios.get(`/api/v2/test-suite/space/${spaceId}`, {
          params: { search: q, page: 1, page_size: 5 }
        });
        (suitesRes.data.items || []).forEach(s => {
          results.push({
            id: s.id,
            type: 'Suite',
            title: s.name,
            subtitle: s.description || '',
            icon: 'mdi-folder-open-outline',
            color: 'info',
            to: `/space/${spaceId}/test-suites/${s.id}`
          });
        });
      } catch (e) { /* ignore */ }

      // Search runs
      try {
        const runsRes = await axios.get(`/api/v2/test-run/space/${spaceId}`, {
          params: { search: q, page: 1, page_size: 5 }
        });
        (runsRes.data.items || []).forEach(r => {
          results.push({
            id: r.id,
            type: 'Run',
            title: r.name,
            subtitle: r.status || '',
            icon: 'mdi-play-circle-outline',
            color: 'success',
            to: `/space/${spaceId}/test-runs/${r.id}`
          });
        });
      } catch (e) { /* ignore */ }

      this.results = results;
    },
    onKeyDown(e) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        this.open();
      }
    },
    open() {
      this.isOpen = true;
      this.query = '';
      this.results = [];
    },
    close() {
      this.isOpen = false;
    },
    selectFirst() {
      if (this.results.length) {
        this.navigate(this.results[0]);
      }
    },
    navigate(item) {
      this.close();
      this.$router.push(item.to);
    }
  }
}
</script>

<style scoped>
.command-item {
  cursor: pointer;
}
.command-item:hover {
  background-color: rgba(var(--v-theme-primary), 0.05);
}
</style>
