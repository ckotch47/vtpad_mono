<template>
  <bugs-modal-component
    v-if="bugItem && filters"
    :is-active="isActive"
    :bug-item="bugItem"
    :filters="filters"
    :full="true"
    @closeBugModal="isActive = false"
  />
</template>

<script>

import BugsModalComponent from "@/components/bugs/modal/bugsModalComponent.vue";
import axios from "axios";
import {useAppStore} from "@/stores/app";
export default {
  name: "indexIssuePage",
  components: {BugsModalComponent},
  data(){
    return{
      store: useAppStore(),
      isActive: true,
      shortName: this.$route.params.id,
      bugItem: undefined,
      filters: undefined
    }
  },
  mounted() {
    console.log(this.$route.params)
    this.getBugDetail()
  },
  methods:{
    getBugDetail(){
      axios.get(`/api/v2/bugs/short/${this.shortName}`).then(res => {
        this.bugItem = res.data;
        this.store = res.data;
        this.getFilter()
      })
    },
    getFilter(){
      if(!this.bugItem) return
      axios.get(`/api/v1/bugs/filters?space_id=${this.bugItem.spaces_id}`).then(res => {
        this.filters = res.data
      })
    }
  }
}
</script>

<style lang="scss">
.bug-modal--full {
  .bug-modal--content{
    flex-direction: row;
    justify-content: space-between;
    width: 100%;
    margin: 0 auto;
    max-width: 1440px;
  }
  .bug-modal--content_right{
    width: 50%;
    max-width: 732px;
  }
  .bug-modal--content_left{
    //max-width: unset;
  }
  .v-timeline-item__body{
    width: 100%;
  }
  //.editor-custom{
  //  max-width: unset;
  //  box-shadow: 0 0 4px #d6d6d6;
  //  max-height: 372px;
  //  overflow-y: auto;
  //  margin: 20px 10px;
  //}
  .custom-title{
    width: 90%;
    display: flex;
    flex-direction: row;
    flex-wrap: nowrap;
    justify-content: space-between;
    align-items: center;
  }
  .custom-text--input{
    max-height: 56px;
    max-width: 1440px;
    margin: 20px auto 0;
    width: 100%;
    padding-right: 10px;
    input{
      border: none
    }

  }
}

@media (width <= 900px) {
  .custom-title{
    div:nth-child(1), div:nth-child(3){
      display: none;
    }
  }
  .bug-modal--full,  {
    .bug-modal--content_right{
      width: 100%;

      margin: 20px auto;
    }
    .bug-modal--content_left{
      margin: 5px auto;
      //margin: auto;
    }
    .editor-custom{
      max-width: unset;
      width: 100%;
    }
    //.send-comment--btn{
    //  width: 100%;
    //}
    .v-overlay__content {
      width: 100vw !important;
      right: 0;
      margin: 0;
      left: unset !important;
      min-width: unset!important;
    }
    .v-card {
      min-width: unset!important;
      width: 100vw !important;
    }
    .bug-modal--content{

      flex-direction: column-reverse;
    }
  }
}

</style>
