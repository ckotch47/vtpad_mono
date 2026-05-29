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
              class="command-item"
              @click="navigate(item)"
            >
              <template #prepend>
                <v-icon :color="item.color">{{ item.icon }}</v-icon>
              </template>
              <v-list-item-title>{{ item.title }}</v-list-item-title>
              <v-list-item-subtitle>{{ item.subtitle }}</v-list-item-subtitle>
              <template #append>
                <v-chip size="x-small" :color="item.color" variant="outlined">{{ item.type }}</v-chip>
              </template>
            </v-list-item>
          </template>
          <v-empty-state v-else-if="query.length > 1" icon="mdi-magnify" text="No results found" />
        </v-list>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { testCaseService, testSuiteService, testRunService } from '@/services'

const route = useRoute()
const router = useRouter()

const isOpen = ref(false)
const query = ref('')
const searchTimer = ref(null)
const results = ref([])

function onKeyDown(e) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    open()
  }
}

function open() {
  isOpen.value = true
  query.value = ''
  results.value = []
}

function close() {
  isOpen.value = false
}

function selectFirst() {
  if (results.value.length) {
    navigate(results.value[0])
  }
}

function navigate(item) {
  close()
  router.push(item.to)
}

async function doSearch(q) {
  const spaceId = route.params.spaceId
  if (!spaceId) return

  const all = []

  try {
    const casesRes = await testCaseService.listBySpace(spaceId, { search: q, page: 1, page_size: 5 })
    for (const c of (casesRes.data.items || [])) {
      all.push({
        id: c.id,
        type: 'Case',
        title: c.title,
        subtitle: c.short_name || '',
        icon: 'mdi-test-tube',
        color: 'primary',
        to: `/space/${spaceId}/test-cases/${c.id}`
      })
    }
  } catch (e) { /* ignore */ }

  try {
    const suitesRes = await testSuiteService.listBySpace(spaceId, { search: q, page: 1, page_size: 5 })
    for (const s of (suitesRes.data.items || [])) {
      all.push({
        id: s.id,
        type: 'Suite',
        title: s.name,
        subtitle: s.description || '',
        icon: 'mdi-folder-open-outline',
        color: 'info',
        to: `/space/${spaceId}/test-suites/${s.id}`
      })
    }
  } catch (e) { /* ignore */ }

  try {
    const runsRes = await testRunService.listBySpace(spaceId, { search: q, page: 1, page_size: 5 })
    for (const r of (runsRes.data.items || [])) {
      all.push({
        id: r.id,
        type: 'Run',
        title: r.name,
        subtitle: r.status || '',
        icon: 'mdi-play-circle-outline',
        color: 'success',
        to: `/space/${spaceId}/test-runs/${r.id}`
      })
    }
  } catch (e) { /* ignore */ }

  results.value = all
}

watch(query, (val) => {
  clearTimeout(searchTimer.value)
  if (!val || val.length < 2) {
    results.value = []
    return
  }
  searchTimer.value = setTimeout(() => {
    doSearch(val)
  }, 200)
})

onMounted(() => {
  document.addEventListener('keydown', onKeyDown)
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKeyDown)
})
</script>

<style scoped>
.command-item {
  cursor: pointer;
}
.command-item:hover {
  background-color: rgba(var(--v-theme-primary), 0.05);
}
</style>
