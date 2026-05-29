<template>
  <v-btn class="custom-chip" :text="text" :color="color" />
</template>

<script setup>
defineProps({
  text: String,
  color: String
})
</script>

<style scoped lang="scss">
.custom-chip {
  height: 24px;
  font-size: 0.7rem;
  margin-right: 5px;
  align-items: center;
  display: inline-flex;
  font-weight: 400;
  max-width: 100%;
  min-width: 0;
  overflow: hidden;
  position: relative;
  text-decoration: none;
  white-space: nowrap;
  vertical-align: middle;
  border-color: rgba(var(--v-border-color), var(--v-border-opacity));
  border-style: solid;
  border-width: 0;
  border-radius: 9999px;
  padding: 0 12px;
  opacity: 0.8;

  &.v-btn--variant-elevated {
    box-shadow: unset !important;
  }
}
</style>
