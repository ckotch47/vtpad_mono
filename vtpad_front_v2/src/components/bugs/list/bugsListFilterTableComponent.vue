<template>
  <div :class="!display ? 'bugs-filter--d_none' : 'bugs-filter--d'">
    <v-select
      v-model="select"
      class="bugs-filter--d_select"
      :label="title"
      :items="item"
      item-value="id"
      item-title="title"
      variant="underlined"
      :multiple="multi"
      @update:modelValue="someChange"
    />
    <span v-if="!display" class="text-primary">{{ title }}</span>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  title: String,
  item: Object,
  multi: Boolean,
  link: Boolean,
  selectArray: Array,
  display: Boolean
})

const emit = defineEmits(['changeFilter'])

const select = ref(undefined)

watch(() => props.selectArray, (val) => {
  select.value = val
}, { deep: true, immediate: true })

function someChange() {
  emit('changeFilter', select.value)
}
</script>

<style lang="scss">
.text-primary {
  color: rgb(var(--v-theme-primary));
}
.bugs-filter {
  &--d_none {
    position: relative;
    display: inline-block;
    cursor: pointer;
  }
  &--d_select {}
}
.bugs-filter--d_none {
  .bugs-filter--d_select {
    opacity: 0;
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
  }
}
</style>
