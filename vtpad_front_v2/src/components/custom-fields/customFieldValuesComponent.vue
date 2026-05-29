<template>
  <div v-if="fields.length">
    <div class="text-subtitle-1 mt-4 mb-2">Custom Fields</div>
    <v-row>
      <v-col v-for="field in fields" :key="field.id" cols="12" md="6">
        <v-text-field
          v-if="field.field_type === 'text' || field.field_type === 'number'"
          v-model="values[field.id]"
          :label="field.name"
          :type="field.field_type === 'number' ? 'number' : 'text'"
          @blur="saveValue(field.id)"
        />
        <v-select
          v-else-if="field.field_type === 'select'"
          v-model="values[field.id]"
          :items="field.options || []"
          :label="field.name"
          @update:model-value="saveValue(field.id)"
        />
        <v-select
          v-else-if="field.field_type === 'multiselect'"
          v-model="values[field.id]"
          :items="field.options || []"
          :label="field.name"
          multiple
          chips
          @update:model-value="saveValue(field.id)"
        />
        <v-checkbox
          v-else-if="field.field_type === 'checkbox'"
          v-model="values[field.id]"
          :label="field.name"
          @update:model-value="saveValue(field.id)"
        />
        <v-text-field
          v-else-if="field.field_type === 'date'"
          v-model="values[field.id]"
          :label="field.name"
          type="date"
          @blur="saveValue(field.id)"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { customFieldService } from '@/services'

const props = defineProps({
  spaceId: { type: String, required: true },
  entityType: { type: String, required: true },
  entityId: { type: String, default: null }
})

const fields = ref([])
const values = ref({})

function loadFields() {
  customFieldService.list(props.spaceId, props.entityType).then(res => {
    fields.value = res.data || []
    if (props.entityId) {
      loadValues()
    }
  }).catch(() => {
    fields.value = []
  })
}

function loadValues() {
  if (!props.entityId) return
  customFieldService.getValues(props.entityId).then(res => {
    const data = res.data || []
    const map = {}
    for (const item of data) {
      const fieldId = item.field?.id || item.field_id
      if (fieldId) {
        map[fieldId] = item.value
      }
    }
    values.value = map
  }).catch(() => {
    values.value = {}
  })
}

function saveValue(fieldId) {
  if (!props.entityId) return
  let value = values.value[fieldId]
  if (value === undefined || value === null || value === '') {
    value = null
  }
  customFieldService.setValue({
    field_id: fieldId,
    entity_id: props.entityId,
    value: value
  }).catch(() => {})
}

function getValues() {
  const result = []
  for (const field of fields.value) {
    const val = values.value[field.id]
    if (val !== undefined && val !== null && val !== '') {
      result.push({ field_id: field.id, value: val })
    }
  }
  return result
}

function saveAllValues(entityId) {
  if (!entityId) return Promise.resolve()
  const promises = []
  for (const field of fields.value) {
    const val = values.value[field.id]
    promises.push(
      customFieldService.setValue({
        field_id: field.id,
        entity_id: entityId,
        value: (val !== undefined && val !== null && val !== '') ? val : null
      })
    )
  }
  return Promise.all(promises)
}

watch(() => props.entityId, (newVal) => {
  if (newVal) {
    loadValues()
  }
})

onMounted(loadFields)

defineExpose({ getValues, saveAllValues })
</script>
