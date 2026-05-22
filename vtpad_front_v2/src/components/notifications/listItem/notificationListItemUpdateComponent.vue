<template>
  Update {{elem.data.changes.name}} into <a :href="`/issue/${elem.data.short_name}`" target="_blank">{{elem.data.short_name}}</a>
</template>

<script>
export default {
  name: "notificationListItemUpdateComponent",
  props:{
    elem: Object
  }
}
</script>

<style scoped>

</style>
