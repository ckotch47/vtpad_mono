<template>
  <shared-run-page />
</template>

<script setup>
import SharedRunPage from '@/components/public-run/sharedRunPage.vue'
</script>

<route>
{
  meta: {
    layout: "default",
    isPublic: true
  }
}
</route>
