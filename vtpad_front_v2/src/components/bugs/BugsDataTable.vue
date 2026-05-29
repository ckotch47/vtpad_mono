<template>
  <v-table class="bugs-table" :class="settings.compact ? 'compact' : ''">
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
      <tr>
        <td />
        <td class="title color-state--OPEN" @click="$emit('create-bug')">Create…</td>
        <td class="username-compact" />
        <td :class="`color-state--OPEN`"><span class="color-state--OPEN">OPEN</span></td>
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
    </tbody>
  </v-table>
</template>

<script setup>
import BugsListRowComponent from './list/bugsListRowComponent.vue'
import BugsListFilterTableComponent from './list/bugsListFilterTableComponent.vue'

defineProps({
  items: { type: Array, default: () => [] },
  filter: { type: Object, default: () => ({}) },
  filterParam: { type: Object, default: () => ({}) },
  settings: { type: Object, default: () => ({}) }
})

defineEmits(['change-filter', 'create-bug', 'open-bug', 'click-tag'])
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
