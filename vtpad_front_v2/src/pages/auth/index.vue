<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <auth-component />
  </v-container>
</template>

<script>
import AuthComponent from "@/components/auth/authComponent.vue";

export default {
  name: "authPage",
  components: {AuthComponent},
  data(){
    return{
      visible: false
    }
  },
  methods:{
    loginUser(){
      location.href = '/space'
    }
  }
}
</script>

<style scoped>

</style>
