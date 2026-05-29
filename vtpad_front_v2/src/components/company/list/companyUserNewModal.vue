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
      <v-toolbar title="New user" />
      <div class="w-100">
        <v-text-field
          v-model="user.username"
          class="ma-4"
          variant="underlined"
          label="username"
        />
        <v-text-field
          v-model="user.mail"
          class="ma-4"
          variant="underlined"
          label="mail"
        />
        <v-text-field
          v-model="user.password"
          :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
          :type="visible ? 'text' : 'password'"
          class="ma-4"
          variant="underlined"
          label="password"
          @click:append-inner="visible = !visible"
        />
      </div>
      <div class="d-flex justify-end ma-4">
        <v-btn
          text="Save"
          color="primary"
          @click="saveNewUser"
        />
      </div>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  isActive: Boolean
})

const emit = defineEmits(['closeNewUserModalEmit', 'saveNewUserModalEmit'])

const visible = ref(false)
const user = ref({
  username: '',
  password: '',
  mail: ''
})

function saveNewUser() {
  emit('saveNewUserModalEmit', user.value)
}
</script>

<style scoped>
</style>
