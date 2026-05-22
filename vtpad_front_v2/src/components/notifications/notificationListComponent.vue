<template>
  <div v-if="loader">
    <v-progress-linear
      color="primary"
      indeterminate
    ></v-progress-linear>
  </div>
  <div class="d-flex justify-end my-2" v-if="!loader">
    <v-btn :prepend-icon="'mdi-notification-clear-all'" :text="'Read all'" variant="outlined" @click="readAllNotification"/>
  </div>

  <div v-if="!loader">

    <v-list v-if="items" >
      <v-list-item
        v-for="item in items"
        :key="item.id"
        :value="item.id"
        :prepend-icon="!item.read ? 'mdi-vector-point' : 'mdi'"
        @click="readNotification(item.id)"
        class="notification-list--item"
      >
        <notification-list-item-update-component v-if="item.event === 'UPDATE'" :elem="item" />
        <notification-list-item-comment-component v-if="item.event === 'COMMENT'" :elem="item" />
        <notification-list-item-assign-component v-if="item.event === 'ASSIGN'" :elem="item"/>
      </v-list-item>
    </v-list>

    <v-btn
      v-if="isInfiniteScroll"
      color="primary"
      width="100%"
      class="ma-4"
      text="Show more"
      @click="nextData"
      ref="infinityScrollBtn"
      v-element-visibility="nextData"
    />
  </div>
</template>

<script setup>
import { vElementVisibility } from '@vueuse/components'
</script>
<script>

import axios from "axios";
import NotificationListItemAssignComponent
  from "@/components/notifications/listItem/notificationListItemAssignComponent.vue";
import NotificationListItemCommentComponent
  from "@/components/notifications/listItem/notificationListItemCommentComponent.vue";
import NotificationListItemUpdateComponent
  from "@/components/notifications/listItem/notificationListItemUpdateComponent.vue";

export default {
  name: "notificationListComponent",
  components: {
    NotificationListItemUpdateComponent,
    NotificationListItemCommentComponent, NotificationListItemAssignComponent},
  data: () => ({
    loader: true,
    items: [],
    isInfiniteScroll: false,
    pageItems: 20,
    limit: 20,
    offset: 0
  }),
  mounted() {
    this.getNotification()
  },
  methods:{
    readAllNotification(){
      axios.put('/api/v1/notification/read-all').then(()=>{
        this.loader = true;
        this.getNotification()
      })
    },
    getNotification(append=false){
      axios.get('/api/v1/notification', {
        params: {
          limit: this.limit,
          skip: this.offset
        }
      }).then(res => {
        if(res.data.length === 0 || res.data.length < this.pageItems){
          this.isInfiniteScroll = false
        }else{
          this.isInfiniteScroll = true
        }
        if(res.data) {
          if(append){
            this.items = this.items.concat(res.data)
          }else{
            this.items = res.data
          }
        }
        this.loader = false
      })
    },
    readNotification(event){
      axios.put(`/api/v1/notification/${event}/read`).then(res => {
        if(res.status && res.status === 200){
          this.items.find(value => value.id === event).read = true;
        }
      })
    },
    nextData(){
      this.offset += this.pageItems;
      this.getNotification(true);
    }
  }
}
</script>

<style lang="scss">
.notification-list--item{
  a{
    color: rgb(var(--v-theme-primary));
  }
}
</style>
