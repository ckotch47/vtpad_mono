<template>
  <div v-if="loader">
    <v-progress-linear
      color="primary"
      indeterminate
    ></v-progress-linear>
  </div>

  <div class="fab_btn">
    <v-fab
      @click="createBug"
      color="info"
      icon="mdi-plus"
    />
  </div>

  <div class="d-flex justify-end">
    <v-btn class="my-2" variant="outlined" :text="'Filter'" @click="isModalFilter = true"/>


    <bugs-modal-filter-component
      :is-active="isModalFilter"
      :filter="filter"
      :filter-param="filterParam"
      :settings="settings"
      v-if="isModalFilter"
      @closeModalEmit="isModalFilter=false"
      @changeFilterFromModalEmit="changeFilter"
      @changeSettingsFromModalEmit="changeSettings"
    />
  </div>

  <v-table v-if="!loader" class="bugs-table" :class="settings.compact ? 'compact' :''">
    <thead >
    <tr>
      <th class="text-left" width="80">
        <bugs-list-filter-table-component title="Id"  :select-array="filterParam?.external_link" :item="filter.external_link.map(val => val = val.split('/').pop())" :multi="true" @change-filter="changeFilter($event, 'external_link')"/>
      </th>
      <th class="text-left" >
        Title
      </th>
      <th class="text-left " :class="settings.compact ? 'text-center username-compact' : ''">
        <bugs-list-filter-table-component title="Assigner" :select-array="filterParam?.assigner_id"  :item="filter.user" :multi="true" @change-filter="changeFilter($event, 'assigner_id')"/>
      </th>
      <th class="text-left" width="100">
        <bugs-list-filter-table-component title="Status" :select-array="filterParam?.state" :item="filter.state" :multi="true" @change-filter="changeFilter($event, 'state')"/>
      </th>
      <th class="text-left" width="300">
        <bugs-list-filter-table-component title="Tags" :select-array="filterParam.tag" :item="filter.tag" :multi="true" @change-filter="changeFilter($event, 'tag')"/>
      </th>
      <th class="text-left " :class="settings.compact ? 'text-center username-compact' : ''">
        <bugs-list-filter-table-component title="Create" :select-array="filterParam?.create_user" :item="filter.user" :multi="true" @change-filter="changeFilter($event, 'create_user')"/>
      </th>
      <th class="text-left" width="100" v-if="!settings.compact">
        Date
      </th>
    </tr>
    </thead>
    <tbody>
    <tr  >
      <td></td>
      <td class="title color-state--OPEN" @click="createBug">Create…</td>
      <td class="username-compact"></td>
      <td :class="`color-state--OPEN`">
        <span class="color-state--OPEN"> OPEN </span>
      </td>
      <td></td>
      <td></td>
      <td  v-if="!settings.compact"></td>
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
      v-if="isInfiniteScroll && !loader "
      color="primary"
      width="100%"
      class="ma-4"
      text="Show more"
      @click="nextData"
      ref="infinityScrollBtn"
      v-element-visibility="nextData"
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
import { ref } from 'vue'
import { vElementVisibility } from '@vueuse/components'
import BugsModalFilterComponent from "@/components/bugs/modal/modalFilter/bugsModalFilterComponent.vue";

const infinityScrollBtn = ref(null)
const isVisible = ref(false)


</script>

<script>
import BugsModalComponent from "@/components/bugs/modal/bugsModalComponent.vue";
import BugsListRowComponent from "@/components/bugs/list/bugsListRowComponent.vue";
import BugsListFilterTableComponent from "@/components/bugs/list/bugsListFilterTableComponent.vue";
import { bugService } from '@/services'
import {useAppStore} from "@/stores/app";


export default {
  name: "bugsListComponent",
  components: {BugsListFilterTableComponent, BugsListRowComponent, BugsModalComponent},
  props: {
    spaseIdFrom: undefined
  },
  data () {
    return {
      store: useAppStore(),
      dialog: false,
      isModalFilter: false,
      desserts: [
      ],
      spaceId: undefined,
      loader: true,
      isInfiniteScroll: true,
      itemPerPage: 15,
      filterParam: {
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
        limit: this.itemPerPage,
      },
      filter: {
        "create_date": true,
        "create_date_end": true,
        "estimate_date": true,
        "estimate_date_end": true,
        "state": [
          "string"
        ],
        "user": [
          {
            "id": "string",
            "username": "string",
            "mail": "string",
            "avatar_id": "string",
            "avatar": {
              "id": "string",
              "filepath": "string"
            },
            "spaceId": "string",
            "role": "OWNER",
            "right": "string"
          }
        ],
        "order_by": [
          "string"
        ],
        "tag": [
          {
            "id": "string",
            "title": "string",
            "color": "string",
            "create_date": "2024-06-07T21:47:25.431Z",
            "space_id": "string"
          }
        ],
        "external_link": [
          "string"
        ]
      },
      openBugItem: undefined,
      settings: {}
    }
  },
  watch:{
    External_link: {
      handler(newValue, oldValue) {
        console.log(newValue, oldValue)
      },
      deep: true
    },
    spaseIdFrom:{
      handler() {
        this.openPage()
      },
      deep: true
    }
  },
  updated() {
    // this.openPage()
  },
  async mounted() {
    // this.openPage()
  },
  beforeMount() {
    let setting = localStorage.getItem('bugsTableSettings')
    if(!setting){
      localStorage.setItem('bugsTableSettings', JSON.stringify(this.settings))
    }else{
      this.settings = JSON.parse(setting)
    }
  },
  methods: {
    onElementVisibility(){

    },
    openPage(){

      this.loader = true;

      this.filter = {"create_date": true,
        "create_date_end": true,
        "estimate_date": true,
        "estimate_date_end": true,
        "state": [
          "string"
        ],
        "user": [
          {
            "id": "string",
            "username": "string",
            "mail": "string",
            "avatar_id": "string",
            "avatar": {
              "id": "string",
              "filepath": "string"
            },
            "spaceId": "string",
            "role": "OWNER",
            "right": "string"
          }
        ],
        "order_by": [
          "create_date"
        ],
        "tag": [
          {

          }
        ],
        "external_link": [
          "string"
        ]}
      this.filterParam= {
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
        limit: this.itemPerPage,
      };
        this.filterParam.space_id = this.$route.params.spaceId;
      this.filterParam.limit = this.itemPerPage;
      this.spaceId = this.$route.params.spaceId;
      this.filterParam.space_id = this.spaceId;
      if(this.spaceId !== undefined) {
        this.getFilter().then();
        this.getData(false).then();
      }

    },
    async getFilter(){
      bugService.getFilters(this.spaceId).then(res => {
        this.filter = res.data;
        for(const item of this.filter.user){
          item.title = item.username
        }
      })
    },
    async getData(append=true){
      if(!append) {
        this.filterParam.skip = 0;

      }
      bugService.list(this.filterParam).then(res => {
        if(append)
          this.desserts = this.desserts.concat(res.data)
        else
          this.desserts = res.data

        this.isInfiniteScroll = false

        if(res.data.length < this.itemPerPage)
          this.isInfiniteScroll = false
        else
          this.isInfiniteScroll = true

        if(res.data.length === 0 && this.skip > 0){
          this.skip -= this.itemPerPage;
        }
        this.loader = false
      })
    },
    createBug(){
      bugService.create({
        space_id: this.spaceId,
        state: 'OPEN',
        title: ''
      }).then(res => {
        this.desserts.unshift(res.data)
        this.openBug(res.data)
      })
    },
    changeFilter(event, name){
      this.filterParam[name] = event;
      this.getData(false);
    },
    changeSettings(event, name){
      this.settings[name] = event;
      localStorage.setItem('bugsTableSettings', JSON.stringify(this.settings))
    },
    clickTag(tagId){
      const tmp = this.filterParam.tag.findIndex(value => value === tagId)
      if(tmp !== -1) {
        this.filterParam.tag.splice(tmp, 1)
        this.changeFilter(this.filterParam.tag, 'tag')
      }
      else
        this.changeFilter([...this.filterParam.tag, tagId], 'tag')
      this.getData(false);
    },
    nextData(){
      // this.loader = true;
      this.filterParam.skip += this.itemPerPage;
      this.getData(true)
    },
    openBug(bugItem){
      this.dialog = !this.dialog;
      this.openBugItem = bugItem;
      this.store.openBug = bugItem;
    },
    closeBugModal(){

      this.dialog = false;
      this.openBugItem = undefined
      this.store.openBug = undefined;
    },
    updateBugInList(bug){
      let bugListIndex = this.desserts.findIndex(val => val.id === bug.id)
      this.desserts[bugListIndex]= bug
    }
  },

}
</script>

<style lang="scss">

.bugs-table table{
  overflow-y: auto;
  //min-width: 1100px;
  max-width: 1500px !important;


}
.bugs-table{
  tr:hover{
    background-color: rgba(var(--v-border-color), var(--v-hover-opacity));
  }
  a{
    color: rgb(var(--v-theme-primary));;
  }
  .select-overflow{
    width: 100%;
    white-space: nowrap;
    overflow-y: auto;
  }
  .v-field__input{
    flex-wrap: nowrap;
  }
  .show-one{
    .v-field__input{
      .v-select__selection:nth-child(n+2){
        display: none;
      }
    }
  }
  .show-three{
    .v-field__input{
      .v-select__selection:nth-child(n+3){
        display: none;
      }
    }
  }
  //.v-avatar::before{
  //  color: white;
  //  content: attr(data-placeholder);
  //  font-size: 18px;
  //  margin-left: 24px;
  //}

}
.bugs-table.compact{
  .username-compact{
    max-width: 100px !important;
  }
  table{
    min-width: 900px !important;
  }
}
.bugs-table > table{
  overflow-y: auto;
  min-width: 1500px !important;
}
td .v-input{
  //height: 55px;
  //margin: 24px 0;
}
td.title{
  cursor: pointer;
  width: 440px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 440px;
}
td.username-no-wrap{
  width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}
td.tag-chip{
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  align-items: center;
}
td.short-name{
  white-space: nowrap;
}
.fab_btn{
  display: flex;
  flex-direction: column;
  flex-wrap: nowrap;
  position: fixed;
  bottom: 5px;
  right: 60px;
  height: 120px;
  .v-fab__container{
    bottom: 0;
  }
}
</style>
