<template>

</template>

<script>
export default {
  name: "logoutPage",
  mounted() {
    localStorage.removeItem('auth_token' )
    localStorage.removeItem('refresh_token')
    location.href = '/auth'
  }
}
</script>

<style scoped>

</style>
