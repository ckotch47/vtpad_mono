<template>
    <v-card class="mx-auto pa-12 pb-8" elevation="8" max-width="448" rounded="lg">
      <v-form @keydown.enter="loginUser">
        <div class="text-subtitle-1 text-medium-emphasis">Account</div>

        <v-text-field
          density="compact"
          placeholder="Email address"
          prepend-inner-icon="mdi-email-outline"
          variant="outlined"
          v-model="loginData.mail"
        ></v-text-field>

        <div class="text-subtitle-1 text-medium-emphasis">Password</div>

        <v-text-field
          :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
          :type="visible ? 'text' : 'password'"
          @click:append-inner="visible = !visible"
          density="compact"
          placeholder="Enter your password"
          prepend-inner-icon="mdi-lock-outline"
          variant="outlined"
          v-model="loginData.password"
        ></v-text-field>
        <v-alert class="my-2" type="error" :text="errorMessage" v-if="errorMessage">
        </v-alert>
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

<script>

import { authService } from '@/services'

export default {
  name: "authComponent",
  data(){
    return{
      visible: false,
      errorMessage: null,
      loginData: {
        mail: undefined,
        password: undefined
      }
    }
  },
  methods:{
    loginUser(){
      this.errorMessage = null;
      authService.login({
        mail: this.loginData.mail,
        password: this.loginData.password
      }).then(res => {
        if(res.status === 200){
          this.errorMessage = null;
          localStorage.setItem('auth_token', res.data.access_token)
          localStorage.setItem('refresh_token', res.data.refresh_token)
          location.href = '/space'
        }else{
          this.errorMessage = 'Not found user'
        }
      }).catch(()=>{
        this.errorMessage = 'Not found user'
      })

    }
  }
}
</script>

<style scoped>

</style>
