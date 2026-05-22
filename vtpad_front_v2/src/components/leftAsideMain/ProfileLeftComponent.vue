<template>
  <v-card
    class="mx-auto"
    min-height="150"
    rounded="0"

  >
    <div class="d-flex ">
      <div class="w-75" >

          <v-avatar
            class="left-avatar_top"
            color="grey"
            size="60"
            @click="showProfileModal = !showProfileModal"
          >
            <span class="text-h5" v-if="!profile.avatar.filepath">{{profile.username[0].toLowerCase()}}</span>
            <v-img :src="profile.avatar.filepath" cover v-else></v-img>
          </v-avatar>
        <v-list-item

          :title="profile.username"
          :subtitle="profile.mail"
        ></v-list-item>
      </div>

      <div class="w-25 d-flex flex-column icon-profile">

       <notification-rings-component :count="0"/>

        <v-btn
          color="text-grey-lighten-1"
          v-if="profile.role === 'company_admin'"
          icon="mdi-domain"
          variant="plain"
          :to="'/company/users'"
        />
        <v-btn
          color="text-grey-lighten-1"
          icon="mdi-arrow-collapse-left"
          variant="plain"
          @click="$emit('hideLeftMenu')"
        />

      </div>

    </div>
  </v-card>
  <profile-modal-component
    v-if="showProfileModal"
    @close-profile-modal="closeProfileModal"
    @updateUserProfileEmit="updateUserProfile"
    :is-active="showProfileModal"
    :profile="profile"/>

</template>

<script>

import ProfileModalComponent from "@/components/leftAsideMain/profile/profileModalComponent.vue";
import axios from "axios";
import NotificationRingsComponent from "@/components/notifications/notificationRingsComponent.vue";

export default {
  name: "ProfileLeftComponent",
  components: {NotificationRingsComponent, ProfileModalComponent},
  emits:['hideLeftMenu'],

  data(){
    return{
      showProfileModal: false,
      profile: {
        "id": "string",
        "username": "string",
        "mail": "string",
        "status": "string",
        "role": "string",
        "avatar": {
          "avatar": "string",
          "filepath":"string",
        },
        "company": {
          "id": "string",
          "name": "string",
          "status": "string",
        }
      }
    }
  },
  async beforeMount() {
    this.getUserProfile()
  },
  mounted() {
  },
  methods:{
    closeProfileModal(){
      this.showProfileModal = false
    },
    getUserProfile(){
      axios.get('/api/v2/user').then(res => {
        this.profile = res.data
      })
    },
    updateUserProfile(){
      this.getUserProfile();
    }
  }
}
</script>

<style lang="scss">
.left-avatar_top{
  margin: 8px 0 0 16px;
  cursor: pointer;
  //&::before{
  //  color: white;
  //  content: attr(data-placeholder);
  //  font-size: 36px;
  //  margin-left: 60px;
  //}
}
.menu-show{
  .v-fab__container {
    right: -15px !important;
    bottom: 15px !important;
  }

}
.icon-profile{
  align-items: flex-end;
  justify-content: space-between;
  span{
    //margin-right: 8px;
  }
}
</style>
