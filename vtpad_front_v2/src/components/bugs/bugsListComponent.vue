<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>

  <div class="fab_btn">
    <v-fab color="info" icon="mdi-plus" @click="createBug" />
  </div>

  <div class="d-flex justify-end">
    <v-btn class="my-2" variant="outlined" text="Filter" @click="isModalFilter = true" />

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
  </div>

  <bugs-data-table
    v-if="!loader"
    :items="desserts"
    :filter="filter"
    :filter-param="filterParam"
    :settings="settings"
    @change-filter="changeFilter"
    @create-bug="createBug"
    @open-bug="openBug"
    @click-tag="clickTag"
  />

  <v-btn
    v-if="isInfiniteScroll && !loader"
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

const route = useRoute()
const store = useAppStore()

const spaceId = computed(() => route.params.spaceId)

const props = defineProps({
  spaseIdFrom: undefined
})

const dialog = ref(false)
const isModalFilter = ref(false)
const desserts = ref([])

const loader = ref(true)
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
  bugService.list(filterParam.value).then(res => {
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
    loader.value = false
  })
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

<style lang="scss">
.fab_btn {
  display: flex;
  flex-direction: column;
  flex-wrap: nowrap;
  position: fixed;
  bottom: 5px;
  right: 60px;
  height: 120px;
  .v-fab__container {
    bottom: 0;
  }
}
</style>
