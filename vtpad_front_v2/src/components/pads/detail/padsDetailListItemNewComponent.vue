<template>
  <v-list-item :class="`pads-detail--item `">
    <v-list-item-title
      contenteditable="true"
      class="pads-detail--item_main is-empty"
      data-placeholder="Type this…"
      @focusin="focusInItem($event)"
      @focusout="focusOutItem($event)"
      @keydown.alt.enter="newItem($event)"

    >

    </v-list-item-title>

  </v-list-item>

</template>

<script>
import axios from "axios";

export default {
  name: "padsDetailListItemNewComponent",
  emits: ['newItemEmit'],
  props: {
    items: Array,
    padId: String
  },
  data(){
    return{
      padsItems: {}
    }
  },
  mounted() {
    this.padsItems = this.items
  },
  methods:{
    newItem(event){
      axios.post(`/api/v1/items/${this.padId}`, {
        text: event.target.innerText,
        mainId: null
      }).then(() => {
        this.$emit('newItemEmit')
      })
    },
    focusInItem(event){
      event.target.classList.remove('is-empty')
    },
    focusOutItem(event){
      if(!event.target.innerText) event.target.classList.add('is-empty')
    },
  }
}
</script>

<style  lang="scss">
.pads-detail--item{
  &_main{
    background: rgba(var(--v-border-color), var(--v-border-opacity));
  }
  .v-list-item{
    min-height: 34px !important;

  }
  .v-list-item-title{
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
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
  }
}
</style>
