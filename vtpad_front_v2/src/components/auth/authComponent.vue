<template>
  <v-card class="mx-auto pa-12 pb-8" elevation="8" max-width="448" rounded="lg">
    <v-form @keydown.enter="loginUser">
      <div class="text-subtitle-1 text-medium-emphasis">Account</div>

      <v-text-field
        v-model="loginData.mail"
        density="compact"
        placeholder="Email address"
        prepend-inner-icon="mdi-email-outline"
        variant="outlined"
      />

      <div class="text-subtitle-1 text-medium-emphasis">Password</div>

      <v-text-field
        v-model="loginData.password"
        :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
        :type="visible ? 'text' : 'password'"
        density="compact"
        placeholder="Enter your password"
        prepend-inner-icon="mdi-lock-outline"
        variant="outlined"
        @click:append-inner="visible = !visible"
      />

      <v-alert
        v-if="errorMessage"
        class="my-2"
        color="error"
        :text="errorMessage"
      />

      <v-btn
        class="mb-8"
        size="large"
        variant="tonal"
        block
        @click="loginUser"
      >
        Log In
      </v-btn>
    </v-form>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'
import { authService } from '@/services'

const visible = ref(false)
const errorMessage = ref(null)
const loginData = ref({
  mail: '',
  password: ''
})

function loginUser() {
  errorMessage.value = null
  authService.login({
    mail: loginData.value.mail,
    password: loginData.value.password
  }).then(res => {
    if (res.status === 200) {
      errorMessage.value = null
      localStorage.setItem('auth_token', res.data.access_token)
      localStorage.setItem('refresh_token', res.data.refresh_token)
      location.href = '/space'
    } else {
      errorMessage.value = 'Not found user'
    }
  }).catch(() => {
    errorMessage.value = 'Not found user'
  })
}
</script>
