<template>
  <v-dialog
    transition="dialog-top-transition"
    width="auto"
    :model-value="isActive"
    min-width="600"
    min-height="600"
    @update:modelValue="$emit('closeNewUserModalEmit', isActive)"
  >

    <v-card>
      <v-toolbar :title="'Nwe user'" />

      <div class="w-100" >
        <v-text-field
          class="ma-4"
          variant="underlined"
          label="username"
          v-model="user.username"
        />
        <v-text-field
          class="ma-4"
          variant="underlined"
          label="mail"
          v-model="user.mail"
        />
        <v-text-field
          :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
          :type="visible ? 'text' : 'password'"
          @click:append-inner="visible = !visible"
          class="ma-4"
          variant="underlined"
          label="password"
          v-model="user.password"

        />

      </div>

      <div class="d-flex justify-end ma-4">
        <v-btn
          text="Save"
          color="primary"
          @click="saveNewUser"
        ></v-btn>
      </div>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: "companyUserNewModal",
  emits: ['closeNewUserModalEmit', 'saveNewUserModalEmit'],
  props:{
    isActive: Boolean
  },
  data(){
    return{
      visible: false,
      user:{
        username: '',
        password: '',
        mail: ''
      }
    }
  },
  methods:{
    saveNewUser(){
      this.$emit('saveNewUserModalEmit', this.user)
    }
  }
}
</script>

<style scoped>

</style>
