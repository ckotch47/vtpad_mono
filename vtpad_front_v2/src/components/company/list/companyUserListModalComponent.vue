<template>
  <v-dialog
    transition="dialog-top-transition"
    width="auto"
    :model-value="isActive"
    min-width="300"
    min-height="600"
    @update:modelValue="$emit('closeUserModalEmit', isActive)"
  >

    <v-card>
      <v-toolbar :title="user.user.username">
        <v-btn
          text="Close"
          color="gray"
          @click="$emit('closeUserModalEmit', isActive)"
        ></v-btn>
      </v-toolbar>

      <div class="w-100" >
          <v-text-field
            class="ma-4"
            variant="underlined"
            label="username"
            v-model="user.user.username"
          />
        <v-text-field
          class="ma-4"
          variant="underlined"
          label="mail"
          v-model="user.user.mail"
        />
        <v-checkbox
          label="Active"
          v-model="status"
          color="primary"
        />
        <div class="ma-4">
        {{password}}
        </div>
      </div>

      <div class="d-flex justify-space-between ma-4">
        <v-btn
          text="Reset password"
          color="orange"
          @click="restPasswordUser"
        ></v-btn>
        <v-btn
          text="Save"
          color="primary"
          @click="saveUser"
        ></v-btn>
      </div>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from "axios";

export default {
  name: "companyUserListModalComponent",
  emits: ['closeUserModalEmit'],
  props: {
    user: Object,
    isActive: Boolean,
  },
  data(){
    return{
      status: false,
      password: undefined
    }
  },
  mounted() {
    this.status = this.user.status === 'active'
  },
  methods:{
    deleteUser(){
      axios.delete(`/api/v2/company-user/${this.user.user.id}`).then(res => {
        this.$emit('closeUserModalEmit', this.isActive)
      })
    },
    restPasswordUser(){
      axios.put(`/api/v2/company-user/${this.user.user.id}/reset-password`).then(res => {
        this.password = res.data.password
      })
    },
    saveUser(){
      axios.put(`/api/v2/company-user/${this.user.user.id}`,{
        username: this.user.user.username,
        mail: this.user.user.mail,
        status: this.status ? 'active' : 'deactivate'
      }).then(()=>{
        this.user.status = this.status ? 'active' : 'deactivate'
        this.password = undefined;
        this.$emit('closeUserModalEmit', this.isActive)
      })

    }
  }
}
</script>

<style scoped>

</style>
