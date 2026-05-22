<template>
  <v-dialog
    transition="dialog-top-transition"
    width="auto"
    :model-value="isActive"
    min-width="400"
    min-height="400"
    @update:modelValue="$emit('closeProfileModal')"
  >
      <v-card>
        <v-toolbar title="Profile">
          <v-btn :text="'Logout'" color="red" :to="'/auth/logout'"/>
        </v-toolbar>

        <div class="" >
          <label for="upload_avatar">
            <v-avatar
              class="left-avatar_top"
              color="grey"
              size="60"
              image=""
            >
              <span class="text-h5" v-if="!profile.avatar.filepath">{{profile.username[0] ? profile.username[0].toLowerCase() : '@'}}</span>
              <v-img  :src="profile.avatar.filepath" cover v-else></v-img>
            </v-avatar>
            <v-file-input  @update:modelValue="uploadAvatar($event)" accept="image/*" id="upload_avatar" class="profile-upload--avatar d-none" label="File input"></v-file-input>
          </label>
          <div class="ma-4">
            <v-text-field
              variant="underlined"
              title="username"
              :model-value="profile.username"
            >

            </v-text-field>
            <span >{{profile.mail}}</span>
          </div>
          <v-list-item>
            <v-select
              class="select-custom py-4"
              label="Theme"
              :items="['light', 'dark', 'system']"
              v-model="theme"
              variant="outlined"
              @update:modelValue="updateTheme( $event)"
            ></v-select>
          </v-list-item>


        </div>

        <v-card-actions class="justify-end">
          <v-btn
            text="Close"
            @click="$emit('closeProfileModal')"
          ></v-btn>
        </v-card-actions>
      </v-card>
  </v-dialog>
</template>

<script>
import {useTheme} from "vuetify";
import axios from "axios";

export default {
  name: "profileModalComponent",
  props: {
    isActive: Boolean,
    profile: Object,
  },
  emits: ['updateUserProfileEmit'],
  setup(){
    const userTheme = useTheme();
    return{
      userTheme
    }
  },
  data(){
    return{
      theme: undefined
    }
  },
  mounted() {
    this.theme = localStorage.getItem('useTheme')
  },
  methods:{
    updateTheme(event){
      localStorage.setItem('useTheme', event);
      if(event !== 'system'){
        this.userTheme.global.name.value = event
      }else {
        this.userTheme.global.name.value = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      }
      // eslint-disable-next-line no-self-assign
      // location.href = location.href
    },
    uploadAvatar(event){
      const form = new FormData();
      form.append('file', event);
      axios.post('/api/v1/file', form,
        {headers: {"Content-Type": "multipart/form-data",}}).then(value => {
          this.$emit('updateUserProfileEmit')
      })
    }
  }
}
</script>

<style scoped>

</style>
