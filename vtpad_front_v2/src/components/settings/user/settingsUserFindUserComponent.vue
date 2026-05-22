<template>
  <v-autocomplete
    label="Find user"
    :items="searchUserItem"
    :item-title="'mail'"
    item-value="mail"
    v-model="inputValue"
    @update:modelValue="selectUser"
  ></v-autocomplete>
</template>

<script>
import axios from "axios";

export default {
  name: "settingsUserFindUserComponent",
  emits: ['addUserIntoSpaceEmit'],
  data(){
    return {
      searchUserItem: [],
      inputValue: ''
    }
  },
  mounted() {
    this.searchUser('')
  },
  methods:{
    searchUser(event){
      axios.get(`/api/v1/user/search/by-mail?mail=`+event).then(res => {
        this.searchUserItem = res.data
      })
    },
    selectUser(){
      this.$emit('addUserIntoSpaceEmit', this.inputValue)
    }
  }
}
</script>

<style scoped>

</style>
