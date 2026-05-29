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
        />
      </v-toolbar>

      <div class="w-100">
        <v-text-field
          v-model="user.user.username"
          class="ma-4"
          variant="underlined"
          label="username"
        />
        <v-text-field
          v-model="user.user.mail"
          class="ma-4"
          variant="underlined"
          label="mail"
        />
        <v-checkbox
          v-model="status"
          label="Active"
          color="primary"
        />
        <div class="ma-4">
          {{ password }}
        </div>
      </div>

      <div class="d-flex justify-space-between ma-4">
        <v-btn
          text="Reset password"
          color="orange"
          @click="restPasswordUser"
        />
        <v-btn
          text="Save"
          color="primary"
          @click="saveUser"
        />
      </div>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { companyUserService } from '@/services'

const props = defineProps({
  user: Object,
  isActive: Boolean
})

const emit = defineEmits(['closeUserModalEmit'])

const status = ref(false)
const password = ref(undefined)

onMounted(() => {
  status.value = props.user.status === 'active'
})

function restPasswordUser() {
  companyUserService.resetPassword(props.user.user.id).then(res => {
    password.value = res.data.password
  })
}

function saveUser() {
  companyUserService.update(props.user.user.id, {
    username: props.user.user.username,
    mail: props.user.user.mail,
    status: status.value ? 'active' : 'deactivate'
  }).then(() => {
    props.user.status = status.value ? 'active' : 'deactivate'
    password.value = undefined
    emit('closeUserModalEmit', props.isActive)
  })
}
</script>

<style scoped>
</style>
