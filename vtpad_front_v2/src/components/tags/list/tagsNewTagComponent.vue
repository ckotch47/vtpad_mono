<template>
  <div class="d-flex">
    <v-text-field
      v-model="titleValue"
      label="Tags"
      variant="underlined"
      class="text-field my-4 w-75"
    />
    <div class="color-picker w-25">
      <div style="position:relative; display:inline-block; cursor: pointer">
        <custom-chip-component :color="colorValue" :text="titleValue ?? 'Color'" />
        <input v-model="colorValue" type="color" style="opacity:0; position:absolute; left:0;top:0;width:100%">
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

<style lang="scss">
.btn-tag--color {}
</style>
