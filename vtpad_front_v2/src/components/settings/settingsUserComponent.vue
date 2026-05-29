<template>
  <div v-if="loader">
    <v-progress-linear
      color="primary"
      indeterminate
    ></v-progress-linear>
  </div>

  <settings-user-find-user-component @addUserIntoSpaceEmit="addUserIntoSpace"/>

  <v-card
    class="mx-auto my-2 custom-user"
    elevation="2"
    v-for="user in users"
    :key="user.id"
  >
    <v-card-item >
      <template v-slot:prepend>
        <v-avatar
          class="custom-user--avatar"
          color="grey"
          image=""
          size="40"
        >
          <span class="text-h5" v-if="!user.avatar.filepath">{{user?.username ? user?.username[0].toLowerCase() : '@'}}</span>
          <v-img :src="user.avatar.filepath" cover v-else></v-img>
        </v-avatar>
      </template>
      <div >
        <v-card-title v-if="user.id">
          <div class="user-username">
          {{user?.username ?? '@username'}}
          </div>

        </v-card-title>
        <v-card-subtitle>
          {{user.mail}} - {{user.role}}
        </v-card-subtitle>
      </div>
      <v-card-actions>
        <div class="user-action--btn">
          <v-btn v-if="user.role !== 'OWNER'" class="user-owner--btn" color="primary" text="Owner" @click="makeOwnerUser(user.id)"></v-btn>

          <settings-user-right-menu-component
            v-if="user.role !== 'OWNER'"
            :user-right="user.right"
            :space-id="spaceId"
            :user-id="user.id"
          />

          <v-btn class="user-delete--btn" color="red" text="Delete" @click="deleteUserFromSpace(user.id)"></v-btn>
        </div>
      </v-card-actions>
    </v-card-item>

  </v-card>
</template>

<script>
import { spaceService } from '@/services'
import SettingsUserRightMenuComponent from "@/components/settings/user/settingsUserRightMenuComponent.vue";
import SettingsUserFindUserComponent from "@/components/settings/user/settingsUserFindUserComponent.vue";

export default {
  name: "settingsUserComponent",
  components: {SettingsUserFindUserComponent, SettingsUserRightMenuComponent},
  data(){
    return{
      loader: true,
      spaceId: this.$route.params.spaceId,
      users: []
    }
  },
  mounted() {
    this.getUsers()
  },
  methods:{
    getUsers(){
      spaceService.getUsers(this.spaceId).then(res => {
        this.users = res.data
        this.loader = false
      })
    },
    makeOwnerUser(userId){
      this.loader = true
      spaceService.makeOwner(this.spaceId, userId).then(res => {
        this.users = res.data
        this.loader = false
      })
    },
    deleteUserFromSpace(userId){
      this.loader = true
      spaceService.removeUser(this.spaceId, userId).then(res => {
        this.users = res.data
        this.loader = false
      }).catch(()=>{
        this.loader = false})
    },
    addUserIntoSpace(userMail){
      if(!userMail) return
      this.loader = true
      spaceService.addUser(this.spaceId,{
        mail: userMail
      }).then(res => {
        if(!res.data) {
          this.loader = false
          return
        }
        this.users = res.data
        this.loader = false
      })
    }
  }
}
</script>

<style lang="scss">
.user-action--btn{
    //position: absolute;
    top: 30%;
    right: 0;
  button{
    margin-left: 20px;
  }
}
.custom-user {
  .v-card-item .v-card-title {
    display: flex;
    justify-content: space-between;
  }
  &--avatar{
    margin: auto;
  }
  .v-card-item__content{
    display: flex;
    justify-content: space-between;
  }
  .show-one{
    .v-field__input{
      .v-select__selection:nth-child(n+2){
        display: none;
      }
    }
  }
  //.v-avatar::before{
  //  color: white;
  //  content: attr(data-placeholder);
  //  margin-left: 40px;
  //}
}
</style>
