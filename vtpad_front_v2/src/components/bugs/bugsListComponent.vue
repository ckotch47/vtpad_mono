<template>
  <page-header-component title="Bugs" />

  <list-page-toolbar>
    <template #filters>
    <v-text-field
      v-model="search"
      prepend-inner-icon="mdi-magnify"
      label="Search bugs"
      density="compact"
      hide-details
      variant="solo"
      class="list-filter-search"
      clearable
      @update:model-value="onSearch"
    />
    </template>
    <template #actions>
    <v-btn variant="outlined" text="Filter" @click="isModalFilter = true" />
    <v-btn v-if="canManageBugs" color="primary" prepend-icon="mdi-plus" class="ml-2" @click="createBug">
      New Bug
    </v-btn>
    </template>
  </list-page-toolbar>

  <bugs-modal-filter-component
    v-if="isModalFilter"
    :is-active="isModalFilter"
    :filter="filter"
    :filter-param="filterParam"
    :settings="settings"
    @closeModalEmit="isModalFilter = false"
    @changeFilterFromModalEmit="changeFilter"
    @changeSettingsFromModalEmit="changeSettings"
  />

  <v-alert v-if="loadError && hasLoaded && desserts.length" type="error" variant="tonal" density="compact" class="mb-3" role="alert">
    Bugs could not be refreshed. Existing results are still shown.
    <v-btn size="small" variant="text" @click="retryLoad">Retry</v-btn>
  </v-alert>
  <v-progress-linear v-if="loader && hasLoaded" color="primary" indeterminate aria-hidden="true" />

  <bugs-data-table
    :items="desserts"
    :loading="loader"
    :initial-loading="initialLoading"
    :initial-error="loadError && hasLoaded && !desserts.length"
    :permission-error="loadErrorStatus === 403"
    :filter="filter"
    :filter-param="filterParam"
    :settings="settings"
    @change-filter="changeFilter"
    @open-bug="openBug"
    @click-tag="clickTag"
    @retry="retryLoad"
  />

  <v-btn
    v-if="isInfiniteScroll && hasLoaded && !loader && !loadError"
    ref="infinityScrollBtn"
    v-element-visibility="nextData"
    color="primary"
    width="100%"
    class="ma-4"
    text="Show more"
    @click="nextData"
  />

  <bugs-modal-component
    v-if="dialog"
    :is-active="dialog"
    :bug-item="store.openBug"
    :filters="filter"
    :can-manage-bugs="canManageBugs"
    :can-manage-comments="canManageComments"
    :can-edit-tags="canEditTags"
    @close-bug-modal="closeBugModal()"
    @updateBug="updateBugInList"
  />
</template>

<script setup>
import { ref, computed, watch, onBeforeMount } from 'vue'
import { useRoute } from 'vue-router'
import { vElementVisibility } from '@vueuse/components'
import { useAppStore } from '@/stores/app'
import { bugService } from '@/services'
import BugsModalComponent from '@/components/bugs/modal/bugsModalComponent.vue'
import BugsDataTable from './BugsDataTable.vue'
import PageHeaderComponent from '@/components/common/pageHeaderComponent.vue'
import ListPageToolbar from '@/components/common/ListPageToolbar.vue'
import { useSpaceCapabilitiesStore } from '@/stores/spaceCapabilities'
const route = useRoute()
const store = useAppStore()
const capabilityStore = useSpaceCapabilitiesStore()

const spaceId = computed(() => route.params.spaceId)
const canManageBugs = computed(() => capabilityStore.can(spaceId.value, 'bugs'))
const canManageComments = computed(() => capabilityStore.can(spaceId.value, 'bug_comments'))
const canEditTags = computed(() => capabilityStore.can(spaceId.value, 'tags'))

const props = defineProps({
  spaseIdFrom: undefined
})

const dialog = ref(false)
const isModalFilter = ref(false)
const desserts = ref([])
const search = ref('')
const searchDebounce = ref(null)

const loader = ref(true)
const hasLoaded = ref(false)
const initialLoading = computed(() => loader.value && !hasLoaded.value)
const loadError = ref(false)
const loadErrorStatus = ref(0)
const requestId = ref(0)
const retryAppend = ref(false)
const isInfiniteScroll = ref(true)
const itemPerPage = ref(15)
const filterParam = ref({
  space_id: undefined,
  create_date: undefined,
  create_date_end: undefined,
  create_user: undefined,
  assigner_id: undefined,
  state: undefined,
  external_link: undefined,
  estimate_date: undefined,
  estimate_date_end: undefined,
  not_assigner: false,
  order_by: undefined,
  order_arrow: undefined,
  show_closed: false,
  tag: [],
  skip: 0,
  limit: itemPerPage.value
})
const filter = ref({
  create_date: true,
  create_date_end: true,
  estimate_date: true,
  estimate_date_end: true,
  state: ['string'],
  user: [{ id: 'string', username: 'string', mail: 'string', avatar_id: 'string', avatar: { id: 'string', filepath: 'string' }, spaceId: 'string', role: 'OWNER', right: 'string' }],
  order_by: ['string'],
  tag: [{ id: 'string', title: 'string', color: 'string', create_date: '2024-06-07T21:47:25.431Z', space_id: 'string' }],
  external_link: ['string']
})
const openBugItem = ref(undefined)
const settings = ref({})
const infinityScrollBtn = ref(null)

watch(() => props.spaseIdFrom, () => {
  openPage()
}, { deep: true })

watch(() => route.params.spaceId, () => {
  if (route.params.spaceId) capabilityStore.load(route.params.spaceId)
  openPage()
}, { immediate: true })

onBeforeMount(() => {
  const setting = localStorage.getItem('bugsTableSettings')
  if (!setting) {
    localStorage.setItem('bugsTableSettings', JSON.stringify(settings.value))
  } else {
    settings.value = JSON.parse(setting)
  }
})

function openPage() {
  loader.value = true
  hasLoaded.value = false
  loadError.value = false
  loadErrorStatus.value = 0
  desserts.value = []
  requestId.value += 1
  filter.value = {
    create_date: true,
    create_date_end: true,
    estimate_date: true,
    estimate_date_end: true,
    state: ['string'],
    user: [{ id: 'string', username: 'string', mail: 'string', avatar_id: 'string', avatar: { id: 'string', filepath: 'string' }, spaceId: 'string', role: 'OWNER', right: 'string' }],
    order_by: ['string'],
    tag: [{}],
    external_link: ['string']
  }
  filterParam.value = {
    space_id: undefined,
    create_date: undefined,
    create_date_end: undefined,
    create_user: undefined,
    assigner_id: undefined,
    state: undefined,
    external_link: undefined,
    estimate_date: undefined,
    estimate_date_end: undefined,
    not_assigner: false,
    order_by: 'create_date',
    order_arrow: 'DESC',
    show_closed: false,
    tag: [],
    q: undefined,
    skip: 0,
    limit: itemPerPage.value
  }
  filterParam.value.space_id = spaceId.value
  filterParam.value.limit = itemPerPage.value
  if (spaceId.value !== undefined) {
    getFilter()
    getData(false)
  }
}

async function getFilter() {
  bugService.getFilters(spaceId.value).then(res => {
    filter.value = res.data
    for (const item of filter.value.user) {
      item.title = item.username
    }
  })
}

async function getData(append = true) {
  if (!append) {
    filterParam.value.skip = 0
  }
  const currentRequest = ++requestId.value
  retryAppend.value = append
  loadError.value = false
  loader.value = true
  try {
    const res = await bugService.list(filterParam.value)
    if (currentRequest !== requestId.value) return
    if (append) {
      desserts.value = desserts.value.concat(res.data)
    } else {
      desserts.value = res.data
    }
    isInfiniteScroll.value = false
    if (res.data.length < itemPerPage.value) {
      isInfiniteScroll.value = false
    } else {
      isInfiniteScroll.value = true
    }
    if (res.data.length === 0 && filterParam.value.skip > 0) {
      filterParam.value.skip -= itemPerPage.value
    }
  } catch (error) {
    if (currentRequest === requestId.value) {
      loadError.value = true
      loadErrorStatus.value = Number(error?.response?.status || 0)
      if (loadErrorStatus.value === 403) desserts.value = []
    }
  } finally {
    if (currentRequest === requestId.value) {
      hasLoaded.value = true
      loader.value = false
    }
  }
}

function retryLoad() {
  getData(retryAppend.value)
}

function createBug() {
  bugService.create({
    space_id: spaceId.value,
    state: 'OPEN',
    title: ''
  }).then(res => {
    desserts.value.unshift(res.data)
    openBug(res.data)
  })
}

function changeFilter(event, name) {
  filterParam.value[name] = event
  getData(false)
}

function changeSettings(event, name) {
  settings.value[name] = event
  localStorage.setItem('bugsTableSettings', JSON.stringify(settings.value))
}

function onSearch() {
  clearTimeout(searchDebounce.value)
  searchDebounce.value = setTimeout(() => {
    changeFilter(search.value || undefined, 'q')
  }, 400)
}

function clickTag(tagId) {
  const tmp = filterParam.value.tag.findIndex(value => value === tagId)
  if (tmp !== -1) {
    filterParam.value.tag.splice(tmp, 1)
    changeFilter(filterParam.value.tag, 'tag')
  } else {
    changeFilter([...filterParam.value.tag, tagId], 'tag')
  }
  getData(false)
}

function nextData() {
  filterParam.value.skip += itemPerPage.value
  getData(true)
}

function openBug(bugItem) {
  dialog.value = !dialog.value
  openBugItem.value = bugItem
  store.openBug = bugItem
}

function closeBugModal() {
  dialog.value = false
  openBugItem.value = undefined
  store.openBug = undefined
}

function updateBugInList(bug) {
  const bugListIndex = desserts.value.findIndex(val => val.id === bug.id)
  desserts.value[bugListIndex] = bug
}
</script>

<style scoped>
.list-filter-search {
  flex: 1 1 320px;
  min-width: 220px;
  max-width: 520px;
}
</style>

<style scoped lang="scss">
</style>
