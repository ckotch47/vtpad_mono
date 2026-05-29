<template>
  <v-autocomplete
    v-model="inputValue"
    label="Find user"
    :items="searchUserItem"
    item-title="mail"
    item-value="mail"
    @update:modelValue="selectUser"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { userService } from '@/services'

const emit = defineEmits(['addUserIntoSpaceEmit'])

const searchUserItem = ref([])
const inputValue = ref('')

function searchUser(event) {
  userService.searchByMail(event).then(res => {
    searchUserItem.value = res.data
  })
}

function selectUser() {
  emit('addUserIntoSpaceEmit', inputValue.value)
}

onMounted(() => searchUser(''))
</script>
