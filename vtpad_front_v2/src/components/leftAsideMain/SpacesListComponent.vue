<template>
  <div class="d-flex">
    <v-text-field
      class="hide-v-input__details"
      label="Search"
      @update:modelValue="updateFilterSpace($event)"
    />
    <v-btn
      :class="!company ? 'd-none' : ''"
      color="text-grey-lighten-1"
       icon="mdi-plus"
       variant="plain"
       height="56px"
        width="56px"
        @click="createSpace"
    />
  </div>

    <v-list >
      <v-list-item
        v-for="item in resItems"
        :key="item.id"
        :to="`/space/${item.id}/bugs`"
        :value="item.id"
        >
        <v-list-item-title>{{item.name}}</v-list-item-title>
          <template v-slot:append>

            <v-btn
              v-if="item.role==='OWNER' || company"
              color="grey-lighten-1"
              icon="mdi-cog"
              variant="text"
              size="32"
              :to="`/space/${item.id}/settings`"
            ></v-btn>

            <v-btn
              v-if="item.role==='OWNER' || company"

              color="grey-lighten-1"
              icon="mdi-chart-arc"
              variant="text"
              size="32"
              :to="`/space/${item.id}/report/statistic`"
            ></v-btn>

          </template>
      </v-list-item>
    </v-list>

</template>



<script>
import { spaceService } from '@/services'

export default {
  name: "SpacesListComponent",
  props:{
    company: Boolean
  },
  data:()=>({
    filterValue: '',
    resItems: [],
    items: [
        {
          "id": "string",
          "name": "string",
          "role": "OWNER",
          "sort": 0,
          "short_name": "string"
        },
    ],
  }),
  beforeMount() {
    if(!this.company) {
      spaceService.list().then(res => {
        this.items = res.data;
        this.resItems = this.items
      })
    }else{
      spaceService.listCompany().then(res => {
        this.items = res.data;
        this.resItems = this.items
      })
    }
  },
  methods:{
    updateFilterSpace(event){
      this.resItems = this.items.filter(value => value.name.toLowerCase().includes(event.toLowerCase()))
    },
    async createSpace(){
      const temp = (await spaceService.create({
        name: 'new space'
      })).data;
      location.href = `/space/${temp.id}/settings`

    },
  }

}
</script>

<style lang="scss" scoped>
.hide-v-input__details{
  .v-input__details {
    display: none;
  }
}
:deep(.v-list-item__append){
  display: none;
}
:deep(.v-list-item:hover .v-list-item__append){
  display: unset;
}
</style>
