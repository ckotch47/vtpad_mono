<template>
  <span>
    Test run completed.
    <RouterLink v-if="runRoute" :to="runRoute" aria-label="Open completed test run">
      Open run
    </RouterLink>
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  elem: {
    type: Object,
    required: true
  }
})

const runRoute = computed(() => {
  const route = props.elem?.data?.route
  if (typeof route !== 'string') return null

  const match = route.match(/^\/space\/([0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})\/test-runs\/([0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})$/i)
  return match ? route : null
})
</script>
