<template>
  <div v-if="compact" class="profile-header-control">
    <notification-rings-component :count="0" />
    <v-menu location="bottom end">
      <template #activator="{ props: menuProps }">
        <v-btn
          v-bind="menuProps"
          class="profile-header-trigger"
          variant="text"
          aria-label="Open profile menu"
          title="Profile"
        >
          <v-avatar color="grey" size="34">
            <v-img
              v-if="profile.avatar.filepath"
              :src="profile.avatar.filepath"
              :alt="profile.username || 'User avatar'"
              cover
            />
            <span v-else>{{ profile.username ? profile.username[0].toLowerCase() : '@' }}</span>
          </v-avatar>
          <v-icon class="ml-1" size="18">mdi-chevron-down</v-icon>
        </v-btn>
      </template>
      <v-list density="compact" min-width="220">
        <v-list-item
          :title="profile.username || 'Profile'"
          :subtitle="profile.mail"
          prepend-icon="mdi-account-circle-outline"
          to="/profile"
        />
        <v-list-item
          title="Notifications"
          prepend-icon="mdi-bell-outline"
          to="/profile/notification"
        />
        <v-list-item
          v-if="profile.role === 'company_admin'"
          title="Company users"
          prepend-icon="mdi-domain"
          to="/company/users"
        />
      </v-list>
    </v-menu>
  </div>

  <v-card
    v-else
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
defineProps({
  compact: Boolean
})

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

.profile-header-control {
  display: flex;
  align-items: center;
  gap: 4px;
}

.profile-header-trigger {
  min-width: 44px;
  padding-inline: 4px;
}
</style>
