<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>
  <div v-if="!loader" class="mx-auto my-2">
    <h2>Settings</h2>
    <v-text-field
      v-model="space.name"
      label="Space name"
      append-inner-icon="mdi-content-save"
      clearable
      @click:append-inner="saveName"
    />
    <v-text-field
      v-model="space.short_name"
      label="Short name"
      append-inner-icon="mdi-content-save"
      clearable
      @click:append-inner="saveName"
    />
  </div>
  <div v-if="!loader" class="mx-auto my-2">
    <h2>Delete</h2>
    <p>Enter DELETE for delete space</p>
    <v-text-field
      v-model="deleteSpace"
      label="Delete"
      append-inner-icon="mdi-delete-forever"
      clearable
      @click:append-inner="delSpace"
    />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { spaceService } from '@/services'

const route = useRoute()
const spaceId = ref(route.params.spaceId)

const loader = ref(true)
const deleteSpace = ref(null)
const space = ref({
  short_name: null,
  sort: 2000,
  name: '',
  id: ''
})

function getSpaceSetting() {
  spaceService.getById(spaceId.value).then(res => {
    space.value = res.data
    loader.value = false
  })
}

function saveName() {
  spaceService.update(spaceId.value, {
    name: space.value.name,
    short_name: space.value.short_name
  }).then(res => {
    if (res.status === 200) getSpaceSetting()
  })
}

function delSpace() {
  if (deleteSpace.value !== 'DELETE') {
    deleteSpace.value = null
    return false
  }
  spaceService.delete(spaceId.value).then(() => {
    location.href = '/space'
  })
}

watch(() => route.params.spaceId, (val) => {
  spaceId.value = val
  getSpaceSetting()
}, { deep: false })

onMounted(getSpaceSetting)
</script>

<style scoped>
input {
  border: none;
  background: none;
}
</style>
