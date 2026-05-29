<template>
  <v-table>
    <thead>
      <tr>
        <th class="text-left" width="400">Username</th>
        <th class="text-left" width="400">Mail</th>
        <th class="text-left" width="100">Status</th>
        <th class="text-left" width="100">Edit</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="item in items" :key="item.id">
        <td>{{ item.user.username }}</td>
        <td>{{ item.user.mail }}</td>
        <td>{{ item.status }}</td>
        <td>
          <v-btn
            color="grey-lighten-1"
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

<script setup>
import { ref, onMounted } from 'vue'
import { companyUserService } from '@/services'
import CompanyUserListModalComponent from '@/components/company/list/companyUserListModalComponent.vue'
import CompanyUserNewModal from '@/components/company/list/companyUserNewModal.vue'

const activeUser = ref(undefined)
const items = ref([])
const showModal = ref(false)
const isNewUserModal = ref(false)

function getUserList() {
  companyUserService.list().then(res => {
    items.value = res.data
  })
}

function closeUserModal() {
  showModal.value = false
  activeUser.value = undefined
  getUserList()
}

function editUserShow(userId) {
  showModal.value = true
  activeUser.value = items.value.find(value => value.id === userId)
}

function saveNewUserModal(user) {
  companyUserService.create(user).then(() => getUserList())
  isNewUserModal.value = false
}

onMounted(getUserList)
</script>

<style lang="scss">
.add-user--btn {
  display: flex;
  flex-direction: column;
  flex-wrap: nowrap;
  position: fixed;
  bottom: 5px;
  right: 60px;
  height: 120px;
}
</style>
