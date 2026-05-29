<template>
  <v-card
    class="mx-auto"
    min-height="150"
    rounded="0"
  >
    <div class="d-flex">
      <div class="w-75">
        <router-link to="/profile">
          <v-avatar
            class="left-avatar_top"
            color="grey"
            size="60"
          >
            <span v-if="!profile.avatar.filepath" class="text-h5">{{ profile.username ? profile.username[0].toLowerCase() : '@' }}</span>
            <v-img v-else :src="profile.avatar.filepath" :alt="profile.username || 'User avatar'" cover />
          </v-avatar>
        </router-link>
        <v-list-item
          :title="profile.username"
          :subtitle="profile.mail"
        />
      </div>

      <div class="w-25 d-flex flex-column icon-profile">
        <notification-rings-component :count="0" />

        <v-btn
          v-if="profile.role === 'company_admin'"
          color="grey-lighten-1"
          icon="mdi-domain"
          variant="plain"
          aria-label="Company users"
          to="/company/users"
        />
        <v-btn
          color="grey-lighten-1"
          icon="mdi-arrow-collapse-left"
          variant="plain"
          aria-label="Hide menu"
          @click="$emit('hideLeftMenu')"
        />
      </div>
    </div>
  </v-card>
</template>

<script setup>
import { ref, onBeforeMount } from 'vue'
import { userService } from '@/services'
import NotificationRingsComponent from '@/components/notifications/notificationRingsComponent.vue'

const emit = defineEmits(['hideLeftMenu'])

const profile = ref({
  id: 'string',
  username: 'string',
  mail: 'string',
  status: 'string',
  role: 'string',
  avatar: {
    avatar: 'string',
    filepath: 'string'
  },
  company: {
    id: 'string',
    name: 'string',
    status: 'string'
  }
})

function getUserProfile() {
  userService.getCurrent().then(res => {
    profile.value = res.data
  })
}

onBeforeMount(getUserProfile)
</script>

<style lang="scss">
.left-avatar_top {
  margin: 8px 0 0 16px;
  cursor: pointer;
}
.menu-show {
  .v-fab__container {
    right: -15px !important;
    bottom: 15px !important;
  }
}
.icon-profile {
  align-items: flex-end;
  justify-content: space-between;
}
</style>
