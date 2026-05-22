<template>
  New comment in <a :href="`/issue/${elem.data.short_name}`" target="_blank">{{elem.data.short_name}}</a>
</template>

<script>
export default {
  name: "notificationListItemCommentComponent",
  props:{
    elem: Object
  }
}
</script>

<style scoped>

</style>
