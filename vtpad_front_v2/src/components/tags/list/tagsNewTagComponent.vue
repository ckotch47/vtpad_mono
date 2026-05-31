<template>
  <div class="d-flex">
    <v-text-field
      v-model="titleValue"
      label="Tags"
      variant="underlined"
      class="text-field my-4 w-75"
    />
    <div class="color-picker w-25">
      <div class="overlay-picker-wrap">
        <custom-chip-component :color="colorValue" :text="titleValue ?? 'Color'" />
        <input v-model="colorValue" type="color" class="overlay-picker-input">
      </div>

      <v-btn text="Save" variant="outlined" color="primary" @click="createTag" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import CustomChipComponent from '@/components/common/chips/customChipComponent.vue'
import { tagService } from '@/services'

const props = defineProps({
  spaceId: String
})

const emit = defineEmits(['createNewTagEmit'])

const colorValue = ref('#ff0000')
const titleValue = ref(undefined)

function createTag() {
  tagService.create(props.spaceId, {
    title: titleValue.value,
    color: colorValue.value
  }).then(res => {
    emit('createNewTagEmit', res.data)
  })
}
</script>

<style scoped lang="scss">
.overlay-picker-wrap {
  position: relative;
  display: inline-block;
  cursor: pointer;
}

.overlay-picker-input {
  opacity: 0;
  position: absolute;
  inset: 0;
  width: 100%;
}
</style>
