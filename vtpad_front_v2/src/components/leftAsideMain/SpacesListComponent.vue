<template>
  <div class="d-flex">
    <v-text-field
      class="hide-v-input__details"
      label="Search spaces"
      @update:modelValue="updateFilterSpace"
    />
    <v-btn
      :class="!company ? 'd-none' : ''"
      color="grey-lighten-1"
      icon="mdi-plus"
      variant="plain"
      height="56px"
      width="56px"
      aria-label="Create space"
      @click="createSpace"
    />
  </div>

  <v-progress-linear v-if="loading" indeterminate color="primary" />
  <v-list v-else-if="resItems.length">
    <v-list-item
      v-for="item in resItems"
      :key="item.id"
      :to="`/space/${item.id}/dashboard`"
      :value="item.id"
      :aria-label="spaceName(item)"
    >
      <v-list-item-title>{{ spaceName(item) }}</v-list-item-title>
      <template #append>
        <v-btn
          v-if="item.role === 'OWNER' || company"
          color="grey-lighten-1"
          icon="mdi-cog"
          variant="text"
          size="32"
          aria-label="Space settings"
          :to="`/space/${item.id}/settings`"
        />
        <v-btn
          v-if="item.role === 'OWNER' || company"
          color="grey-lighten-1"
          icon="mdi-chart-arc"
          variant="text"
          size="32"
          aria-label="Space report"
          :to="`/space/${item.id}/report/statistic`"
        />
      </template>
    </v-list-item>
  </v-list>
  <v-card v-else flat class="pa-4 text-center text-grey">
    <v-icon size="48" class="mb-2">mdi-folder-open-outline</v-icon>
    <div>No spaces</div>
  </v-card>
</template>

<script setup>
import { ref, onBeforeMount } from 'vue'
import { spaceService } from '@/services'

const props = defineProps({
  company: Boolean
})

const loading = ref(true)
const resItems = ref([])
const items = ref([])

onBeforeMount(() => {
  loading.value = true
  const service = !props.company ? spaceService.list() : spaceService.listCompany()
  service.then(res => {
    items.value = res.data
    resItems.value = items.value
  }).finally(() => {
    loading.value = false
  })
})

function updateFilterSpace(event) {
  const query = String(event ?? '').trim().toLocaleLowerCase()
  resItems.value = items.value.filter(value => spaceName(value).toLocaleLowerCase().includes(query))
}

function spaceName(item) {
  const name = typeof item?.name === 'string' ? item.name.trim() : ''
  if (!name || ['null', 'undefined'].includes(name.toLocaleLowerCase())) return 'Unnamed space'
  return name
}

async function createSpace() {
  const temp = (await spaceService.create({
    name: 'new space'
  })).data
  location.href = `/space/${temp.id}/settings`
}
</script>

<style lang="scss" scoped>
.hide-v-input__details {
  .v-input__details {
    display: none;
  }
}
:deep(.v-list-item__append) {
  display: none;
}
:deep(.v-list-item:hover .v-list-item__append) {
  display: unset;
}
</style>
