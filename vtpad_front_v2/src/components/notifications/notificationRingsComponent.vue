<template>
  <div> {{unreadCount}}
    <v-btn
      color="text-grey-lighten-1"
      icon="mdi-bell-ring"
      variant="plain"
      :to="'/profile/notification'"
    />
  </div>
</template>

<script>
import axios from "axios";
import {toast} from "vue3-toastify";
import { EventSource } from 'extended-eventsource';

export default {
  name: "notificationRingsComponent",
  props:{
    count: Number,
    userId: String,
  },
  data(){
    return{
      unreadCount: 0,
      audio: new Audio('/ring.mp3')
    }
  },
  mounted() {
    this.sseNotification();
    this.getNotificationCount();
  },
  methods:{
    getNotificationCount(){
      axios.get('/api/v1/notification/unread-count').then(res => {
        if(res.data)
          this.unreadCount = res.data
      })
    },

    sseNotification(){
      const eventSource = new EventSource(`/api/v1/notification/stream`,{
        headers: {
          Authorization: 'Bearer '+localStorage.getItem('auth_token')
        }
      })
      this.subscribeEvents(eventSource)
    },
    subscribeEvents(eventSource) {
      eventSource.addEventListener('UPDATE', async e => {
        let res = JSON.parse(e.data)
        if(res.short_name)
          this.showToast(`UPDATE ${res.short_name}`)
      }, {once: false})

      eventSource.addEventListener('ASSIGN', async e => {
        let res = JSON.parse(e.data)
        if(res.short_name)
          this.showToast(`You assigned ${res.short_name}`)
      }, {once: false})

      eventSource.addEventListener('COMMENT', async e => {
        let res = JSON.parse(e.data)
        if(res.short_name)
          this.showToast(`New comment in ${res.short_name}`)
      }, {once: false})
    },

    showToast(text){
      this.unreadCount ++;
      this.audio.play();
      toast.info(`${text}`, {
        autoClose: 9000
      });
    }
  }
}
</script>

<style scoped>

</style>
