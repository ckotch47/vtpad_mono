<template>
  <div style="position:relative; display:inline-block; cursor: pointer">
    <v-btn class="user-right--btn" text="Right" color="amber" />
    <v-select
      v-model="selectRight"
      class="show-one"
      :items="right"
      item-value="name"
      item-title="title"
      variant="underlined"
      multiple
      style="opacity:0; position:absolute; left:0;top:0;width:100%"
      @update:modelValue="updateRight"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { spaceService } from '@/services'

const props = defineProps({
  userRight: { type: Object, default: () => ({}) },
  userId: { type: String, required: true },
  spaceId: { type: String, required: true }
})

const emit = defineEmits(['updateUserRightEmit'])

const right = ref([
  { title: 'edit pads', value: false, name: 'editPads' },
  { title: 'edit items', value: false, name: 'editItems' },
  { title: 'edit runs', value: false, name: 'editRuns' },
  { title: 'edit notes', value: false, name: 'editNotes' },
  { title: 'close bugs', value: false, name: 'closeBugs' },
  { title: 'edit tags', value: false, name: 'editTags' }
])

const rightObj = ref({
  editPads: false,
  editItems: false,
  editRuns: false,
  editNotes: false,
  closeBugs: false,
  editTags: false
})

const selectRight = ref([])

watch(() => props.userRight, (val) => {
  if (!val) return
  selectRight.value = []
  for (const elem of right.value) {
    elem.value = val[elem.name] ?? false
    if (elem.value) {
      selectRight.value.push(elem.name)
    }
  }
}, { immediate: true })

function updateRight() {
  for (const elem of selectRight.value) {
    const rightElem = right.value.find(r => r.name === elem)
    if (rightElem) {
      rightElem.value = true
      rightObj.value[rightElem.name] = rightElem.value
    }
  }
  spaceService.updateUser(props.spaceId, props.userId, rightObj.value).then(() => {
    emit('updateUserRightEmit')
  })
}
</script>

<style scoped>
</style>
