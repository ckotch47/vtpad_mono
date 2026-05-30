<template>
  <v-text-field
    label="Link"
    variant="outlined"
    :model-value="bug.external_link"
    @change="updateBug('external_link', $event)"
  />

  <v-select
    v-model="bug.assigner_user.id"
    class="select-custom"
    label="Assigner"
    :items="filter.user"
    item-value="id"
    item-title="username"
    variant="outlined"
    @update:modelValue="updateBug('assigner_id', $event)"
  />

  <v-select
    v-model="bug.state"
    class="select-custom"
    label="State"
    :items="filter.state"
    variant="outlined"
    @update:modelValue="updateBug('state', $event)"
  />

  <div class="select-custom">
    <v-text-field
      :model-value="dateVModel"
      type="date"
      class="select-custom"
      label="Estimate date"
      variant="outlined"
      @update:modelValue="onEstimateDateUpdate"
    />
  </div>

  <v-select
    v-model="bug.tag"
    class="select-custom"
    label="Tags"
    multiple
    :items="filter.tag"
    item-value="id"
    item-title="title"
    variant="outlined"
    @update:modelValue="updateBug('tags', $event)"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { bugService } from '@/services'

const props = defineProps({
  bug: Object,
  filter: Object
})

const emit = defineEmits(['updateBug'])

const dateVModel = ref(undefined)

onMounted(() => {
  dateVModel.value = props.bug.estimate_date ? String(props.bug.estimate_date).slice(0, 10) : undefined
})

function onEstimateDateUpdate(value) {
  dateVModel.value = value
  updateBug('estimate_date', value ? new Date(value).toISOString() : null)
}

function updateBug(name, event) {
  let value = undefined
  switch (name) {
    case 'external_link':
      value = event.target.value
      break
    case 'estimateDate':
      value = new Date(event).toISOString()
      break
    case 'tags':
      value = event
      break
    default:
      value = event
      break
  }
  bugService.update(props.bug.id, {
    [name]: value
  }).then(res => {
    emit('updateBug', res.data)
  })
}
</script>

<style lang="scss">
.select-custom {
  input {
    border: none;
  }
  .v-input__prepend {
    display: none !important;
  }
}
</style>
