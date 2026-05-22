<template>
  <v-list-item
  v-for="item in items"
  :key="item.id"
  :class="`runs-detail--item `"
  >
    <div class="d-flex justify-space-between">
      <v-list-item-title
        @click="openRunItem(item)"
        :class="`${item?.subItem[0] || item.mainId === null ? 'runs-detail--item_main' : 'runs-detail--item_sub'} ${showState === false ? item.state ?? '' : ''} ${item.id === store.openRunItem?.id ? 'focused' : ''}`"
      >
          {{item.text}}
      </v-list-item-title>

      <div
        v-if="showState"
        class="runs-item--state"
        :class="`${item?.subItem[0] || item.mainId === null ? 'runs-detail--item_main' : 'runs-detail--item_sub'}`"
        @click="changeState(item.id)"
      >
       <runs-detail-state-component :state="item.state" />
      </div>
    </div>
  <runs-detail-list-item-component
    v-if="item.subItem"
    :items="item.subItem"
    @changeStateEmit="changestateFrom"
    :show-state="showState"
  />

  </v-list-item>
</template>

<script>
import RunsDetailStateComponent from "@/components/runs/detail/runsDetailStateComponent.vue";
import axios from "axios";
import {useAppStore} from "@/stores/app";
export default {
  name: "runsDetailListItemComponent",
  components: {RunsDetailStateComponent},
  emits: ['changeStateEmit'],
  props: {
    items: Array,
    showState: Boolean
  },
  data(){
    return{
      store: useAppStore(),
      stateArr: {
         null: 'pass',
        'pass': 'fail',
        'fail': 'skip',
        'skip': 'pass'
      }
    }
  },
  methods:{
    async changeState(itemId){
      let runItem = this.items.find(val => val.id === itemId)
      const res = await axios.patch(`/api/v1/runitems/${itemId}?state=${this.stateArr[runItem.state]}`);
      if(res.status === 200) {
        this.$emit('changeStateEmit', {from: runItem.state, to: this.stateArr[runItem.state]})
        runItem.state = this.stateArr[runItem.state]
      }
    },
    changestateFrom(value){
      this.$emit('changeStateEmit', value)
    },
    openRunItem(runItem){
      this.store.openRunItem=runItem;
      this.store.openItem = {
        id: runItem.itemId
      }
    }
  }
}
</script>

<style lang="scss">
.runs-detail--item_main, .runs-detail--item_sub{
  &.focused{
    border: 1.5px solid rgb(var(--v-border-color)) !important;
  }
  &.pass{
    //&::before{
    //  content: '🟢';
    //  position: absolute;
    //  left: 0;
    //}
    box-shadow: 20px -15px 15px 6px #1de9b6;
  }
  &.fail{
    //&::before{
    //  content: '🔴';
    //  position: absolute;
    //  left: 0;
    //}
    box-shadow: 20px -15px 15px 6px red;
  }
  &.skip{
    //&::before{
    //  content: '🟠';
    //  position: absolute;
    //  left: 0;
    //}
    box-shadow: 20px -15px 15px 6px orange
  }
}
.runs-detail--item{

  .runs-detail--item {
    border-left: 1px dashed;

  }
  &_main{
    background: rgba(var(--v-theme-surface-variant), .4);

    border: 1px solid transparent;
    margin-bottom: 2px;
  }
  &_sub{
    background: rgba(var(--v-theme-surface-light), var(--v-theme-surface-light-overlay-multiplier))
  }

  .v-list-item{
    min-height: 34px !important;
    //min-height: 42px !important;
  }
  .v-list-item-title{
    min-height: 36px !important;
    padding-top: 0.3rem;
    //padding-bottom: 0.2rem;
    //padding: auto 0;
    white-space: nowrap;
    width: 100%;
    margin-right: 8px;
    border: 1px solid transparent;
  }
  .v-list-item--density-default:not(.v-list-item--nav).v-list-item--one-line{
    padding-right: 0 !important;
    padding-top: 0;
    padding-bottom: 2px;
  }
  .v-list-item--density-default:not(.v-list-item--nav).v-list-item--one-line:last-child{
    padding-bottom: 0;
  }
  .runs-item--state{
    text-align: center;
    width: 130px;
    padding: 8px;
    cursor: pointer;
    user-select: none;

    border: 1px solid transparent;
    &:hover{
      border: 1px dashed rgb(var(--v-theme-primary)) ;
    }
  }
}

</style>
