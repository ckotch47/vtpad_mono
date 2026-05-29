<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>

  <settings-user-find-user-component @add-user-into-space-emit="addUserIntoSpace" />

  <v-card
    v-for="user in users"
    :key="user.id"
    class="mx-auto my-2 custom-user"
    elevation="2"
  >
    <v-card-item>
      <template #prepend>
        <v-avatar class="custom-user--avatar" color="grey" size="40">
          <span v-if="!user.avatar?.filepath" class="text-h5">
            {{ user?.username ? user.username[0].toLowerCase() : '@' }}
          </span>
          <v-img v-else :src="user.avatar.filepath" cover />
        </v-avatar>
      </template>
      <div>
        <v-card-title v-if="user.id">
          <div class="user-username">{{ user?.username ?? '@username' }}</div>
        </v-card-title>
        <v-card-subtitle>{{ user.mail }} - {{ user.role }}</v-card-subtitle>
      </div>
      <v-card-actions>
        <div class="user-action--btn">
          <v-btn
            v-if="user.role !== 'OWNER'"
            class="user-owner--btn"
            color="primary"
            text="Owner"
            @click="makeOwnerUser(user.id)"
          />
          <settings-user-right-menu-component
            v-if="user.role !== 'OWNER'"
            :user-right="user.right"
            :space-id="spaceId"
            :user-id="user.id"
          />
          <v-btn class="user-delete--btn" color="red" text="Delete" @click="deleteUserFromSpace(user.id)" />
        </div>
      </v-card-actions>
    </v-card-item>
  </v-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { spaceService } from '@/services'
import SettingsUserRightMenuComponent from '@/components/settings/user/settingsUserRightMenuComponent.vue'
import SettingsUserFindUserComponent from '@/components/settings/user/settingsUserFindUserComponent.vue'

const route = useRoute()
const spaceId = computed(() => route.params.spaceId)

const loader = ref(true)
const users = ref([])

function getUsers() {
  spaceService.getUsers(spaceId.value).then(res => {
    users.value = res.data
    loader.value = false
  })
}

function makeOwnerUser(userId) {
  loader.value = true
  spaceService.makeOwner(spaceId.value, userId).then(res => {
    users.value = res.data
    loader.value = false
  })
}

function deleteUserFromSpace(userId) {
  loader.value = true
  spaceService.removeUser(spaceId.value, userId).then(res => {
    users.value = res.data
    loader.value = false
  }).catch(() => {
    loader.value = false
  })
}

function addUserIntoSpace(userMail) {
  if (!userMail) return
  loader.value = true
  spaceService.addUser(spaceId.value, { mail: userMail }).then(res => {
    if (!res.data) {
      loader.value = false
      return
    }
    users.value = res.data
    loader.value = false
  })
}

onMounted(() => getUsers())
</script>

<style lang="scss">
.user-action--btn {
  top: 30%;
  right: 0;
  button {
    margin-left: 20px;
  }
}
.custom-user {
  .v-card-item .v-card-title {
    display: flex;
    justify-content: space-between;
  }
  &--avatar {
    margin: auto;
  }
  .v-card-item__content {
    display: flex;
    justify-content: space-between;
  }
  .show-one {
    .v-field__input {
      .v-select__selection:nth-child(n+2) {
        display: none;
      }
    }
  }
}
</style>
