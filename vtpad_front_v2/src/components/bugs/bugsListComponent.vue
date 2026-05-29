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

  <v-table v-if="!loader" class="bugs-table" :class="settings.compact ? 'compact' : ''">
    <thead>
      <tr>
        <th class="text-left" width="80">
          <bugs-list-filter-table-component title="Id" :select-array="filterParam?.external_link" :item="filter.external_link.map(val => val = val.split('/').pop())" :multi="true" @change-filter="changeFilter($event, 'external_link')" />
        </th>
        <th class="text-left">Title</th>
        <th class="text-left" :class="settings.compact ? 'text-center username-compact' : ''">
          <bugs-list-filter-table-component title="Assigner" :select-array="filterParam?.assigner_id" :item="filter.user" :multi="true" @change-filter="changeFilter($event, 'assigner_id')" />
        </th>
        <th class="text-left" width="100">
          <bugs-list-filter-table-component title="Status" :select-array="filterParam?.state" :item="filter.state" :multi="true" @change-filter="changeFilter($event, 'state')" />
        </th>
        <th class="text-left" width="300">
          <bugs-list-filter-table-component title="Tags" :select-array="filterParam.tag" :item="filter.tag" :multi="true" @change-filter="changeFilter($event, 'tag')" />
        </th>
        <th class="text-left" :class="settings.compact ? 'text-center username-compact' : ''">
          <bugs-list-filter-table-component title="Create" :select-array="filterParam?.create_user" :item="filter.user" :multi="true" @change-filter="changeFilter($event, 'create_user')" />
        </th>
        <th v-if="!settings.compact" class="text-left" width="100">Date</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td />
        <td class="title color-state--OPEN" @click="createBug">Create…</td>
        <td class="username-compact" />
        <td :class="`color-state--OPEN`">
          <span class="color-state--OPEN">OPEN</span>
        </td>
        <td />
        <td />
        <td v-if="!settings.compact" />
      </tr>

      <bugs-list-row-component
        v-for="item in desserts"
        :key="item.name"
        :item="item"
        :settings="settings"
        @openBug="openBug(item)"
        @ClickTagEmit="clickTag"
      />
    </tbody>
  </v-table>

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
import BugsListRowComponent from '@/components/bugs/list/bugsListRowComponent.vue'
import BugsListFilterTableComponent from '@/components/bugs/list/bugsListFilterTableComponent.vue'

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
.bugs-table table {
  overflow-y: auto;
  max-width: 100%;
}
.bugs-table {
  tr:hover {
    background-color: rgba(var(--v-border-color), var(--v-hover-opacity));
  }
  a {
    color: rgb(var(--v-theme-primary));
  }
  .select-overflow {
    width: 100%;
    white-space: nowrap;
    overflow-y: auto;
  }
  .v-field__input {
    flex-wrap: nowrap;
  }
  .show-one {
    .v-field__input {
      .v-select__selection:nth-child(n+2) {
        display: none;
      }
    }
  }
  .show-three {
    .v-field__input {
      .v-select__selection:nth-child(n+3) {
        display: none;
      }
    }
  }
}
.bugs-table.compact {
  .username-compact {
    max-width: 100px !important;
  }
  table {
    min-width: 100%;
  }
}
.bugs-table > table {
  overflow-y: auto;
  min-width: 100%;
}
td .v-input {}
td.title {
  cursor: pointer;
  width: 440px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 440px;
}
td.username-no-wrap {
  width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}
td.tag-chip {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  align-items: center;
}
td.short-name {
  white-space: nowrap;
}
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
