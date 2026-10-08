<template>
  <v-table class="bugs-table" :class="settings.compact ? 'compact' : ''" :aria-busy="loading">
    <thead>
      <tr>
        <th class="text-left" width="80">
          <bugs-list-filter-table-component
            title="Id"
            :select-array="filterParam?.external_link"
            :item="filter.external_link.map(val => val.split('/').pop())"
            :multi="true"
            @change-filter="$emit('change-filter', $event, 'external_link')"
          />
        </th>
        <th class="text-left">Title</th>
        <th class="text-left" :class="settings.compact ? 'text-center username-compact' : ''">
          <bugs-list-filter-table-component
            title="Assigner"
            :select-array="filterParam?.assigner_id"
            :item="filter.user"
            :multi="true"
            @change-filter="$emit('change-filter', $event, 'assigner_id')"
          />
        </th>
        <th class="text-left" width="100">
          <bugs-list-filter-table-component
            title="Status"
            :select-array="filterParam?.state"
            :item="filter.state"
            :multi="true"
            @change-filter="$emit('change-filter', $event, 'state')"
          />
        </th>
        <th class="text-left" width="300">
          <bugs-list-filter-table-component
            title="Tags"
            :select-array="filterParam.tag"
            :item="filter.tag"
            :multi="true"
            @change-filter="$emit('change-filter', $event, 'tag')"
          />
        </th>
        <th class="text-left" :class="settings.compact ? 'text-center username-compact' : ''">
          <bugs-list-filter-table-component
            title="Create"
            :select-array="filterParam?.create_user"
            :item="filter.user"
            :multi="true"
            @change-filter="$emit('change-filter', $event, 'create_user')"
          />
        </th>
        <th v-if="!settings.compact" class="text-left" width="100">Date</th>
      </tr>
    </thead>
    <tbody>
      <tr v-if="initialLoading">
        <td :colspan="settings.compact ? 6 : 7" class="pa-0">
          <list-loading-skeleton variant="table" :rows="5" :columns="settings.compact ? 6 : 7" label="bugs" />
        </td>
      </tr>
      <tr v-else-if="initialError">
        <td :colspan="settings.compact ? 6 : 7" class="pa-4">
          <v-alert type="error" variant="tonal" density="compact" role="alert">
            {{ permissionError ? 'You do not have permission to view bugs in this space.' : 'Bugs could not be loaded.' }}
            <v-btn v-if="!permissionError" size="small" variant="text" @click="$emit('retry')">Retry</v-btn>
          </v-alert>
        </td>
      </tr>
      <template v-else>
        <tr v-if="items.length === 0">
          <td :colspan="settings.compact ? 6 : 7" class="pa-2">
            <contextual-empty-state
              :icon="hasFilters ? 'mdi-filter-off-outline' : 'mdi-bug-outline'"
              :title="hasFilters ? 'No matching bugs' : 'No bugs yet'"
              :text="hasFilters ? 'Change the filters or use New Bug above if you have permission to add bugs.' : 'Use New Bug above if you have permission to add bugs to this space.'"
            />
          </td>
        </tr>
        <tr v-if="items.length">
          <td />
          <td class="title color-state--OPEN" @click="$emit('create-bug')">Create…</td>
          <td class="username-compact" />
          <td class="color-state--OPEN"><span class="color-state--OPEN">OPEN</span></td>
          <td />
          <td />
          <td v-if="!settings.compact" />
        </tr>
        <bugs-list-row-component
          v-for="item in items"
          :key="item.name"
          :item="item"
          :settings="settings"
          @openBug="$emit('open-bug', item)"
          @ClickTagEmit="$emit('click-tag', $event)"
        />
      </template>
    </tbody>
  </v-table>
</template>

<script setup>
import BugsListRowComponent from './list/bugsListRowComponent.vue'
import BugsListFilterTableComponent from './list/bugsListFilterTableComponent.vue'
import ListLoadingSkeleton from '@/components/common/ListLoadingSkeleton.vue'
import { computed } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  filter: { type: Object, default: () => ({}) },
  filterParam: { type: Object, default: () => ({}) },
  settings: { type: Object, default: () => ({}) },
  initialLoading: { type: Boolean, default: false },
  initialError: { type: Boolean, default: false },
  permissionError: { type: Boolean, default: false }
})

const hasFilters = computed(() => {
  const active = props.filterParam || {}
  const hasValue = value => Array.isArray(value)
    ? value.length > 0
    : value !== undefined && value !== null && value !== false && value !== ''
  return [
    active.create_date,
    active.create_date_end,
    active.create_user,
    active.assigner_id,
    active.state,
    active.external_link,
    active.estimate_date,
    active.estimate_date_end,
    active.not_assigner,
    active.show_closed,
    active.q,
    active.tag
  ].some(hasValue)
})

defineEmits(['change-filter', 'create-bug', 'open-bug', 'click-tag', 'retry'])
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
</style>
