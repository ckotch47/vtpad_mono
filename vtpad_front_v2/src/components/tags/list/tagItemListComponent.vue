<template>
  <div class="d-flex w-100">
    <v-text-field
      v-model="tag.title"
      :label="tag.title"
      variant="underlined"
      class="text-field my-4 w-75"
    />

    <div class="color-picker w-25">
      <div class="overlay-picker-wrap">
        <custom-chip-component :color="tag.color" :text="tag.title ?? 'Color'" />
        <input v-model="tag.color" type="color" class="overlay-picker-input">
      </div>

      <v-btn text="Save" variant="outlined" color="primary" @click="updateTag" />
      <v-btn text="Delete" variant="outlined" color="red" @click="deleteTag" />
    </div>
  </div>
</template>

<script setup>
import CustomChipComponent from '@/components/common/chips/customChipComponent.vue'
import { tagService } from '@/services'

const props = defineProps({
  tag: Object
})

const emit = defineEmits(['deleteTagEmit', 'updateTagEmit'])

function deleteTag() {
  tagService.delete(props.tag.id).then(() => {
    emit('deleteTagEmit')
  })
}

function updateTag() {
  tagService.update(props.tag.id, {
    title: props.tag.title,
    color: props.tag.color
  }).then(() => {
    emit('updateTagEmit')
  })
}
</script>

<style scoped>
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
