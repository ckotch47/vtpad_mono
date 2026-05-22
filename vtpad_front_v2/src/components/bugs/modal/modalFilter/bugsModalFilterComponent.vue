<template>
  <v-dialog
    :model-value="isActive"
    fullscreen
    @update:modelValue="$emit('closeModalEmit')"
    @close="$emit('closeModalEmit')"
    class="bug-modal--filter"
  >

    <v-card >
      <v-toolbar>
        <v-btn
          icon="mdi-close"
          @click="$emit('closeModalEmit')"
        ></v-btn>
        <v-toolbar-title />

      </v-toolbar>
      <v-card-text class="d-flex flex-column ">
        <div>
          Filters

          <bugs-list-filter-table-component display  title="External link" :select-array="filterParam?.external_link" :item="filter.external_link.map(val => val = val.split('/').pop())" :multi="true" @change-filter="changeFilter($event, 'external_link')" />
          <bugs-list-filter-table-component display title="Assigner" :select-array="filterParam?.assigner_id" :item="filter.user" :multi="true" @change-filter="changeFilter($event, 'assigner_id')"/>
          <bugs-list-filter-table-component display title="Status" :select-array="filterParam?.state" :item="filter.state" :multi="true" @change-filter="changeFilter($event, 'state')"/>
          <bugs-list-filter-table-component display title="Tags" :select-array="filterParam.tag" :item="filter.tag" :multi="true" @change-filter="changeFilter($event, 'tag')"/>
          <bugs-list-filter-table-component display title="Create user" :select-array="filterParam?.create_user"  :item="filter.user" :multi="true" @change-filter="changeFilter($event, 'create_user')"/>

          <div class="d-flex justify-space-between  align-center">
            <div class="w-90">
              <bugs-list-filter-table-component display title="Order By" :select-array="filterParam?.order_by" :item="filter?.order_by" :multi="false" @change-filter="changeFilter($event, 'order_by')"/>
            </div>
            <v-btn :icon="filterParam?.order_arrow === 'ASC' ? 'mdi-sort-reverse-variant' : 'mdi-sort-variant'" :text="'Arrow order'" variant="plain" @click="reverseOrderArrow"/>
          </div>

          <v-checkbox label="Not assigner" :model-value="filterParam.not_assigner" @update:modelValue="changeFilter($event, 'not_assigner')"></v-checkbox>
        </div>
        <v-divider></v-divider>
        <div class="my-4">
          Settings
          <v-checkbox color="primary" label="Compact table" :model-value="settings.compact" @update:modelValue="changeSetting($event, 'compact')"></v-checkbox>
        </div>
      </v-card-text>

    </v-card>
  </v-dialog>
</template>

<script>
import BugsListFilterTableComponent from "@/components/bugs/list/bugsListFilterTableComponent.vue";

export default {
  name: "bugsModalFilterComponent",
  components: {BugsListFilterTableComponent},
  emits: ['closeModalEmit', 'changeFilterFromModalEmit', 'changeSettingsFromModalEmit'],
  props: {
    isActive: Boolean,
    filter: Object,
    filterParam: Object,
    settings: Object
  },
  data(){
    return{
      orderArrow: {
        'ASC': 'DESC',
        'DESC': 'ASC',
        null: 'ASC',
        undefined: 'ASC'
      },
      orderArrowValue: null
    }
  },
  mounted() {

  },
  methods:{
    changeFilter(event, name){
      this.$emit('changeFilterFromModalEmit', event, name)
    },
    changeSetting(event, name){
      this.$emit('changeSettingsFromModalEmit', event, name)
    },
    reverseOrderArrow(){
      // eslint-disable-next-line vue/no-mutating-props
      this.filterParam.order_arrow = this.orderArrow[this.filterParam.order_arrow];
      this.changeFilter(this.filterParam.order_arrow, 'order_arrow')
    }
  }
}
</script>

<style lang="scss">
.bug-modal--filter{
    .v-overlay__content{
      width: 425px !important;
      min-width: unset !important;
      position: absolute !important;
      right: 0 !important;
      left: unset !important;;
    }
}
</style>
