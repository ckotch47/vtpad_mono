<template>
  <v-dialog
    :model-value="isActive"
    fullscreen
    class="bug-modal--filter"
    @update:modelValue="$emit('closeModalEmit')"
    @close="$emit('closeModalEmit')"
  >
    <v-card>
      <v-toolbar>
        <v-btn
          icon="mdi-close"
          @click="$emit('closeModalEmit')"
        />
        <v-toolbar-title />
      </v-toolbar>
      <v-card-text class="d-flex flex-column">
        <div>
          Filters
          <bugs-list-filter-table-component display title="External link" :select-array="filterParam?.external_link" :item="filter.external_link.map(val => val = val.split('/').pop())" :multi="true" @change-filter="changeFilter($event, 'external_link')" />
          <bugs-list-filter-table-component display title="Assigner" :select-array="filterParam?.assigner_id" :item="filter.user" :multi="true" @change-filter="changeFilter($event, 'assigner_id')" />
          <bugs-list-filter-table-component display title="Status" :select-array="filterParam?.state" :item="filter.state" :multi="true" @change-filter="changeFilter($event, 'state')" />
          <bugs-list-filter-table-component display title="Tags" :select-array="filterParam.tag" :item="filter.tag" :multi="true" @change-filter="changeFilter($event, 'tag')" />
          <bugs-list-filter-table-component display title="Create user" :select-array="filterParam?.create_user" :item="filter.user" :multi="true" @change-filter="changeFilter($event, 'create_user')" />

          <div class="d-flex justify-space-between align-center">
            <div class="w-90">
              <bugs-list-filter-table-component display title="Order By" :select-array="filterParam?.order_by" :item="filter?.order_by" :multi="false" @change-filter="changeFilter($event, 'order_by')" />
            </div>
            <v-btn :icon="filterParam?.order_arrow === 'ASC' ? 'mdi-sort-reverse-variant' : 'mdi-sort-variant'" text="Arrow order" variant="plain" @click="reverseOrderArrow" />
          </div>

          <v-checkbox label="Not assigner" :model-value="filterParam.not_assigner" @update:modelValue="changeFilter($event, 'not_assigner')" />
          <v-checkbox label="Show closed" :model-value="filterParam.show_closed" @update:modelValue="changeFilter($event, 'show_closed')" />
        </div>
        <v-divider />
        <div class="my-4">
          Settings
          <v-checkbox color="primary" label="Compact table" :model-value="settings.compact" @update:modelValue="changeSetting($event, 'compact')" />
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref } from 'vue'
import BugsListFilterTableComponent from '@/components/bugs/list/bugsListFilterTableComponent.vue'

const props = defineProps({
  isActive: Boolean,
  filter: Object,
  filterParam: Object,
  settings: Object
})

const emit = defineEmits(['closeModalEmit', 'changeFilterFromModalEmit', 'changeSettingsFromModalEmit'])

const orderArrow = ref({
  'ASC': 'DESC',
  'DESC': 'ASC',
  null: 'ASC',
  undefined: 'ASC'
})

function changeFilter(event, name) {
  emit('changeFilterFromModalEmit', event, name)
}

function changeSetting(event, name) {
  emit('changeSettingsFromModalEmit', event, name)
}

function reverseOrderArrow() {
  props.filterParam.order_arrow = orderArrow.value[props.filterParam.order_arrow]
  changeFilter(props.filterParam.order_arrow, 'order_arrow')
}
</script>

<style lang="scss">
.bug-modal--filter {
  .v-overlay__content {
    width: 425px !important;
    min-width: unset !important;
    position: absolute !important;
    right: 0 !important;
    left: unset !important;
  }
}
</style>
