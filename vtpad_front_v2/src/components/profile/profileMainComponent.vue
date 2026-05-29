<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>
  <div v-if="!loader">
    <v-card class="mx-auto my-4" max-width="600">
      <v-card-title class="d-flex align-center">
        <span>Profile</span>
        <v-spacer />
        <v-btn color="red" variant="outlined" to="/auth/logout">Logout</v-btn>
      </v-card-title>
      <v-divider />
      <v-card-text>
        <div class="d-flex align-center mb-4">
          <label for="upload_avatar" class="cursor-pointer">
            <v-avatar color="grey" size="80">
              <span v-if="!profile.avatar?.filepath" class="text-h4">
                {{ profile.username ? profile.username[0].toLowerCase() : '@' }}
              </span>
              <v-img v-else :src="profile.avatar?.filepath" :alt="profile.username || 'User avatar'" cover />
            </v-avatar>
            <v-file-input
              id="upload_avatar"
              accept="image/*"
              class="d-none"
              label="File input"
              @update:modelValue="uploadAvatar"
            />
          </label>
          <div class="ml-4">
            <div class="text-h6">{{ profile.username || '@username' }}</div>
            <div class="text-body-2 text-medium-emphasis">{{ profile.mail }}</div>
            <div class="text-caption text-medium-emphasis">{{ profile.role }}</div>
          </div>
        </div>

        <v-text-field
          v-model="editForm.username"
          label="Username"
          variant="outlined"
          class="mb-2"
        />
        <v-text-field
          :model-value="profile.mail"
          label="Email"
          variant="outlined"
          readonly
          class="mb-2"
        />
        <v-select
          v-model="theme"
          label="Theme"
          :items="['light', 'dark', 'system']"
          variant="outlined"
          class="mb-2"
          @update:modelValue="updateTheme"
        />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" @click="saveProfile">Save</v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTheme } from 'vuetify'
import { userService, fileService } from '@/services'

const userTheme = useTheme()

const loader = ref(true)
const profile = ref({
  id: null,
  username: '',
  mail: '',
  role: '',
  avatar: { filepath: null }
})
const editForm = ref({
  username: ''
})
const theme = ref('system')

function loadProfile() {
  loader.value = true
  userService.getCurrent().then(res => {
    profile.value = res.data
    editForm.value.username = res.data.username || ''
    loader.value = false
  }).catch(() => {
    loader.value = false
  })
}

function saveProfile() {
  userService.updateCurrent({ username: editForm.value.username }).then(() => {
    loadProfile()
  })
}

function uploadAvatar(event) {
  const form = new FormData()
  form.append('file', event)
  fileService.upload(form).then(() => {
    loadProfile()
  })
}

function updateTheme(event) {
  localStorage.setItem('useTheme', event)
  if (event !== 'system') {
    userTheme.global.name.value = event
  } else {
    userTheme.global.name.value = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
}

onMounted(() => {
  theme.value = localStorage.getItem('useTheme') || 'system'
  loadProfile()
})
</script>
