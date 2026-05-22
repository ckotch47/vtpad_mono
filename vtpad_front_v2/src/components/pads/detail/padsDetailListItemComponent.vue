<template>
  <v-list-item
    v-for="item in items"
    :key="item.id"
    :class="`pads-detail--item `"
  >
    <v-list-item-title
      contenteditable="true"
      v-model="item.text"
      :class="`${item?.subItem[0] || item.mainId === null ? 'pads-detail--item_main' : 'pads-detail--item_sub'} ${!item.text ? 'is-empty' : ''}`"
      data-placeholder="Type this…"

      @focusin="focusInItem($event,  item)"
      @focusout="focusOutItem($event, item.id)"
      @keydown.ctrl.enter="newSubItem($event, item.id)"
      @keydown.alt.enter="newItem(item.mainId)"
      @keydown.ctrl.delete="deleteItem(item.id)"
      @keydown.alt.left="upMainItem(item.id)"
      @keydown.alt.right="downMainItem(item.id)"
      @keydown.ctrl.shift.left="upMainItem(item.id)"
      @keydown.ctrl.shift.right="downMainItem(item.id)"
    >

      {{item.text}}
    </v-list-item-title>

  <pads-detail-list-item-component v-if="item.subItem" :items="item.subItem" :pad-id="padId"/>
  </v-list-item>

</template>

<script>
import axios from "axios";
import {useAppStore} from "@/stores/app";
export default {
  name: "padsDetailListItemComponent",
  props: {
    items: Array,
    padId: String
  },
  data(){
    return{
      store: useAppStore(),
      padsItems: {}
    }
  },
  mounted() {
    this.padsItems = this.items
  },
  methods:{
    upMainItem(itemId){
      const itemIndex = this.items.findIndex(value => value.id === itemId)
      if(itemIndex <= 0){
        return
      }
      const prevIndex = itemIndex - 1;
      axios.patch(`/api/v1/items/${itemId}`, {
        sortBeforeId: this.items[prevIndex].id
      }).then(res => {
        if(res.status === 200){
          const tmp = this.items[itemIndex];
          this.items[itemIndex] = this.items[prevIndex];
          this.items[prevIndex] = tmp;
        }
      })
    },

    downMainItem(itemId){
      const itemIndex = this.items.findIndex(value => value.id === itemId)
      if(itemIndex > this.items.length){
        return
      }
      const nextIndex = itemIndex + 1;
      axios.patch(`/api/v1/items/${itemId}`, {
        sortAfterId: this.items[nextIndex].id
      }).then(res => {
        if(res.status === 200){
          const tmp = this.items[itemIndex];
          this.items[itemIndex] = this.items[nextIndex];
          this.items[nextIndex] = tmp;
        }
      })
    },

    newItem(mainId){
      axios.post(`/api/v1/items/${this.padId}`, {
        text: '',
        mainId: mainId
      }).then(res => {
        this.items.push(res.data)
      })


    },
    async newSubItem(event, mainId){
      await this.focusOutItem(event, mainId)
      axios.post(`/api/v1/items/${this.padId}`, {
        text: '',
        mainId: mainId
      }).then(res => {
        this.items.find(item => item.id === mainId).subItem.push(res.data)
      })
    },
    deleteItem(itemId){
      axios.delete(`/api/v1/items/${itemId}`).then(()=>{
        const indexItem = this.items.findIndex((value) => value.id === itemId);
        if(indexItem === -1) return ;
        this.items.splice(indexItem,1);
      })
    },
    updateItem(itemId, text, event){
      axios.put(`/api/v1/items/${itemId}`,{
        text: text
      }).then(res=> {
        this.items.find(item => item.id === itemId).text = text;
        console.log(this.items.find(item => item.id === itemId))
        event.target.innerText = text;
      })
    },
    focusInItem(event, item){
      event.target.classList.remove('is-empty');

      this.store.openItem = {
        id: item.id,
        text: item.text,
        sort: item.sort,
        description: item.description,
        mainId: item.mainId,
        pad_id: item.pad_id
      };

    },
    focusOutItem(event, itemId){
      if(!event.target.innerText) event.target.classList.add('is-empty')
      else event.target.classList.remove('is-empty')

      if(event.target.innerText !== this.items.find(value => value.id === itemId)?.text){
        this.updateItem(itemId, event.target.innerText, event)
      }
    },

    pasteAsPlainText(event) {
      event.preventDefault();
      event.target.innerText = event.clipboardData.getData("text/plain");
    },
  }
}
</script>

<style  lang="scss">
.pads-detail--item{

  .pads-detail--item {
    border-left: 1px dashed;

  }
  .v-list-item__content {
    //background: rgb(var(--v-theme-surface-light));
  }
  &_main{
    background: rgba(var(--v-theme-surface-variant), .4);
    margin-bottom: 2px;
  }
  &_sub{
    background: rgba(var(--v-theme-surface-light), var(--v-theme-surface-light-overlay-multiplier))
  }
  .v-list-item{
    min-height: 34px !important;

  }

  .v-list-item-title{
    padding-top: 0.3rem;
    //padding-bottom: 0.5rem;
    white-space: nowrap;
    div{
      display: none !important;
    }
    &.is-empty:first-child::before {
      color: #adb5bd;
      content: attr(data-placeholder);
    }
  }
  .v-list-item--density-default:not(.v-list-item--nav).v-list-item--one-line{
    padding-right: 0 !important;
    padding-top: 0;
    padding-bottom: 2px;
  }

  .v-list-item--density-default:not(.v-list-item--nav).v-list-item--one-line:last-child{
    padding-bottom: 0;
  }
}
</style>
