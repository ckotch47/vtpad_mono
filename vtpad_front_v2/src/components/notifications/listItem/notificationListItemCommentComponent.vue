<template>
  New comment in <a :href="`/issue/${elem.data.short_name}`" target="_blank">{{ elem.data.short_name }}</a>
</template>

<script setup>
defineProps({
  elem: Object
})
</script>
