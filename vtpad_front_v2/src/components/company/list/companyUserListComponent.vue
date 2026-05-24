<template>
  <v-table>
    <thead>
    <tr>
      <th class="text-left" width="400">
        Username
      </th>
      <th class="text-left" width="400">
        Mail
      </th>
      <th class="text-left" width="100">
        Status
      </th>
      <th class="text-left" width="100">
        Edit
      </th>
    </tr>
    </thead>
    <tbody>
    <tr v-for="item in items" :key="item.id">
      <td>{{item.user.username}}</td>
      <td>{{item.user.mail}}</td>
      <td>{{item.status}}</td>
      <td>
        <v-btn
          color="text-grey-lighten-1"
          icon="mdi-pencil"
          variant="plain"
          @click="editUserShow(item.id)"
        />
      </td>
    </tr>

    </tbody>
  </v-table>

  <company-user-list-modal-component
    v-if="showModal"
    :is-active="showModal"
    :user="activeUser"
    @closeUserModalEmit="closeUserModal"
  />
  <company-user-new-modal
    v-if="isNewUserModal"
    :is-active="isNewUserModal"
    @closeNewUserModalEmit="isNewUserModal = false"
    @saveNewUserModalEmit="saveNewUserModal"
  />

  <div class="add-user--btn">
    <v-fab
      color="primary"
      icon="mdi-plus"
      @click="isNewUserModal = true"
    />
  </div>
</template>

<script>
import { companyUserService } from '@/services'
import CompanyUserListModalComponent from "@/components/company/list/companyUserListModalComponent.vue";
import CompanyUserNewModal from "@/components/company/list/companyUserNewModal.vue";

export default {
  name: "companyUserListComponent",
  components: {CompanyUserNewModal, CompanyUserListModalComponent},
  data(){
    return{
      activeUser: undefined,
      items: [

      ],
      showModal: false,
      isNewUserModal: false
    }
  },
  mounted() {
    this.getUserList()
  },
  methods:{
    getUserList(){
      companyUserService.list().then(res => {
        this.items = res.data
      })
    },
    closeUserModal(active){
      this.showModal = false;
      this.activeUser = undefined;
      this.getUserList()
    },
    editUserShow(userId){
      this.showModal = true;
      this.activeUser = this.items.find(value => value.id === userId);
      console.log(this.activeUser)
    },
    saveNewUserModal(user){
      companyUserService.create(user).then(()=>this.getUserList())
      this.isNewUserModal = false
    }
  },
}
</script>

<style lang="scss">
.add-user--btn{
  display: flex;
  flex-direction: column;
  flex-wrap: nowrap;
  position: fixed;
  bottom: 5px;
  right: 60px;
  height: 120px;
}
</style>
