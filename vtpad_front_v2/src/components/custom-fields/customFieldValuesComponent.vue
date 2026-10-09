<template>
  <section v-if="loading || error || fields.length" class="custom-fields">
    <div class="text-subtitle-1 mt-4 mb-2">Custom Fields</div>
    <v-progress-linear v-if="loading" indeterminate color="primary" aria-label="Loading custom fields" />
    <v-alert v-else-if="error" type="error" variant="tonal" density="compact" role="alert">
      Custom fields could not be loaded.
      <v-btn size="small" variant="text" @click="loadFields">Retry</v-btn>
    </v-alert>
    <v-form v-else ref="fieldForm">
      <v-row>
        <v-col v-for="field in fields" :key="field.id" cols="12" md="6">
          <template v-if="readonly">
            <div class="text-caption text-medium-emphasis">{{ field.name }}<span v-if="field.required"> · Required</span></div>
            <div class="custom-fields__value">{{ displayValue(fieldValue(field.id), field.field_type) }}</div>
          </template>
          <v-text-field
            v-else-if="field.field_type === 'text'"
            :model-value="fieldValue(field.id)"
            :label="label(field)"
            :rules="field.required ? [requiredRule] : []"
            :aria-required="field.required ? 'true' : 'false'"
            @update:model-value="setValue(field.id, $event)"
          />
          <v-text-field
            v-else-if="field.field_type === 'number'"
            :model-value="fieldValue(field.id)"
            :label="label(field)"
            type="number"
            :rules="field.required ? [requiredRule] : []"
            :aria-required="field.required ? 'true' : 'false'"
            @update:model-value="setValue(field.id, $event === '' || $event === null ? null : Number($event))"
          />
          <v-text-field
            v-else-if="field.field_type === 'date'"
            :model-value="fieldValue(field.id)"
            :label="label(field)"
            type="date"
            :rules="field.required ? [requiredRule] : []"
            :aria-required="field.required ? 'true' : 'false'"
            @update:model-value="setValue(field.id, $event)"
          />
          <v-select
            v-else-if="field.field_type === 'select'"
            :model-value="fieldValue(field.id)"
            :items="field.options || []"
            :label="label(field)"
            :rules="field.required ? [requiredRule] : []"
            :aria-required="field.required ? 'true' : 'false'"
            @update:model-value="setValue(field.id, $event)"
          />
          <v-select
            v-else-if="field.field_type === 'multiselect'"
            :model-value="fieldValue(field.id) || []"
            :items="field.options || []"
            :label="label(field)"
            multiple
            chips
            closable-chips
            :rules="field.required ? [requiredRule] : []"
            :aria-required="field.required ? 'true' : 'false'"
            @update:model-value="setValue(field.id, $event)"
          />
          <v-checkbox
            v-else-if="field.field_type === 'checkbox'"
            :model-value="fieldValue(field.id)"
            :label="label(field)"
            :rules="field.required ? [requiredRule] : []"
            :aria-required="field.required ? 'true' : 'false'"
            @update:model-value="setValue(field.id, $event)"
          />
        </v-col>
      </v-row>
    </v-form>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { customFieldService } from '@/services'

const props = defineProps({
  spaceId: { type: String, required: true },
  entityType: { type: String, default: 'testcase' },
  modelValue: { type: Array, default: () => [] },
  readonly: { type: Boolean, default: false }
})
const emit = defineEmits(['update:modelValue'])

const fields = ref([])
const loading = ref(false)
const error = ref(false)
const fieldForm = ref(null)
const valueMap = computed(() => new Map(
  (Array.isArray(props.modelValue) ? props.modelValue : []).map(item => [String(item.field_id), item.value])
))

const requiredRule = value => {
  if (value === null || value === undefined || value === '') return 'This field is required'
  if (typeof value === 'string' && !value.trim()) return 'This field is required'
  if (Array.isArray(value) && !value.length) return 'Select at least one option'
  return true
}

function label(field) {
  return field.required ? `${field.name} *` : field.name
}

function fieldValue(fieldId) {
  return valueMap.value.get(String(fieldId))
}

function setValue(fieldId, value) {
  const values = new Map(valueMap.value)
  values.set(String(fieldId), value)
  emit('update:modelValue', fields.value.map(field => ({
    field_id: String(field.id),
    value: values.get(String(field.id)) ?? null
  })))
}

function displayValue(value, type) {
  if (value === null || value === undefined || value === '') return '—'
  if (type === 'checkbox') return value ? 'Yes' : 'No'
  if (Array.isArray(value)) return value.join(', ')
  return String(value)
}

async function loadFields() {
  if (!props.spaceId) return
  loading.value = true
  error.value = false
  try {
    const response = await customFieldService.list(props.spaceId, props.entityType)
    fields.value = Array.isArray(response.data) ? response.data : []
    const current = new Map(valueMap.value)
    for (const field of fields.value) {
      const snapshot = (props.modelValue || []).find(item => String(item.field_id) === String(field.id))
      if (snapshot && !current.has(String(field.id))) current.set(String(field.id), snapshot.value)
    }
  } catch (_) {
    error.value = true
    fields.value = []
  } finally {
    loading.value = false
  }
}

async function validate() {
  if (props.readonly || !fieldForm.value) return { valid: true }
  return fieldForm.value.validate()
}

watch(() => [props.spaceId, props.entityType], loadFields)
onMounted(loadFields)
defineExpose({ validate, fields, loading })
</script>

<style scoped>
.custom-fields__value {
  min-height: 2.5rem;
  padding: 0.35rem 0;
  overflow-wrap: anywhere;
}
</style>
