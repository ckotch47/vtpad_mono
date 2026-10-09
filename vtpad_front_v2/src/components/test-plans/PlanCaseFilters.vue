<template>
  <section class="plan-case-filters">
    <div class="d-flex align-center mb-2">
      <div>
        <div class="text-subtitle-2">Case filters</div>
        <div class="text-caption text-medium-emphasis">Filters intersect; all selected tags must match.</div>
      </div>
      <v-spacer />
      <v-btn
        size="small"
        variant="text"
        prepend-icon="mdi-plus"
        :disabled="!availableFields.length"
        @click="addCustomField"
      >
        Custom field
      </v-btn>
    </div>

    <v-select
      :model-value="modelValue.priorities || []"
      :items="priorityOptions"
      label="Priorities"
      multiple
      chips
      closable-chips
      density="compact"
      variant="outlined"
      hide-details
      class="mb-3"
      @update:model-value="updateFilter('priorities', $event)"
    />

    <v-autocomplete
      :model-value="modelValue.tags || []"
      :items="tagOptions"
      label="Tags (all selected tags)"
      multiple
      chips
      closable-chips
      clearable
      density="compact"
      variant="outlined"
      hide-details
      class="mb-3"
      @update:model-value="updateFilter('tags', $event)"
    />

    <div v-if="(modelValue.custom_fields || []).length" class="d-flex flex-column ga-2">
      <div
        v-for="(filter, index) in modelValue.custom_fields"
        :key="`${filter.field_id || 'new'}-${index}`"
        class="custom-filter-row"
      >
        <v-select
          :model-value="filter.field_id"
          :items="availableFieldsFor(index)"
          item-title="name"
          item-value="id"
          label="Custom field"
          density="compact"
          variant="outlined"
          hide-details
          @update:model-value="setCustomField(index, $event)"
        />

        <div v-if="fieldFor(filter.field_id)" class="custom-filter-value">
          <v-checkbox
            :model-value="filter.value === null"
            label="Is unset"
            density="compact"
            hide-details
            @update:model-value="setUnset(index, $event, fieldFor(filter.field_id))"
          />
          <component
            :is="customValueComponent(filter.field_id)"
            v-if="filter.value !== null"
            :model-value="filter.value"
            :label="fieldFor(filter.field_id).name"
            :items="customValueItems(fieldFor(filter.field_id))"
            :type="fieldFor(filter.field_id).field_type === 'number' ? 'number' : fieldFor(filter.field_id).field_type === 'date' ? 'date' : 'text'"
            :multiple="fieldFor(filter.field_id).field_type === 'multiselect'"
            density="compact"
            variant="outlined"
            hide-details
            @update:model-value="setCustomValue(index, $event, fieldFor(filter.field_id).field_type)"
          />
        </div>

        <v-btn
          icon="mdi-close"
          size="small"
          variant="text"
          :aria-label="`Remove custom field filter ${fieldFor(filter.field_id)?.name || ''}`"
          @click="removeCustomField(index)"
        />
      </div>
    </div>
    <div v-else class="text-caption text-medium-emphasis">No custom field filters.</div>

    <v-alert v-if="loadError" type="warning" variant="tonal" density="compact" class="mt-3">
      Custom field and tag options could not be loaded.
      <v-btn size="small" variant="text" @click="loadOptions">Retry</v-btn>
    </v-alert>

    <v-alert v-if="previewResult" type="info" variant="tonal" density="compact" class="mt-3" role="status">
      {{ previewResult.total }} test case{{ previewResult.total === 1 ? '' : 's' }} selected
      <span v-if="previewResult.truncated">(showing the first {{ previewResult.case_ids.length }} IDs)</span>
    </v-alert>
    <v-alert v-if="previewError" type="error" variant="tonal" density="compact" class="mt-3" role="alert">
      {{ previewError }}
    </v-alert>
    <v-btn
      class="mt-3"
      size="small"
      variant="tonal"
      prepend-icon="mdi-eye-outline"
      :loading="previewLoading"
      :disabled="previewLoading"
      @click="$emit('preview')"
    >
      Preview selection
    </v-btn>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { customFieldService, testCaseService } from '@/services'

const props = defineProps({
  spaceId: { type: String, required: true },
  modelValue: { type: Object, default: () => ({ priorities: [], tags: [], custom_fields: [] }) },
  previewResult: { type: Object, default: null },
  previewError: { type: String, default: '' },
  previewLoading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'preview'])
const customFields = ref([])
const tagOptions = ref([])
const loadError = ref(false)
const optionsRequestId = ref(0)
const priorityOptions = ['P0', 'P1', 'P2', 'P3']

const availableFields = computed(() => customFields.value)

function cloneFilters() {
  return {
    priorities: [...(props.modelValue?.priorities || [])],
    tags: [...(props.modelValue?.tags || [])],
    custom_fields: (props.modelValue?.custom_fields || []).map(item => ({ ...item })),
  }
}

function publish(next) {
  emit('update:modelValue', next)
}

function updateFilter(key, value) {
  const next = cloneFilters()
  next[key] = value || []
  publish(next)
}

function fieldFor(fieldId) {
  return customFields.value.find(field => field.id === fieldId)
}

function availableFieldsFor(index) {
  const selected = new Set((props.modelValue.custom_fields || []).map((item, i) => i === index ? null : item.field_id).filter(Boolean))
  return availableFields.value.filter(field => !selected.has(field.id))
}

function addCustomField() {
  const next = cloneFilters()
  const selected = new Set(next.custom_fields.map(item => item.field_id))
  const field = availableFields.value.find(item => !selected.has(item.id))
  if (!field) return
  next.custom_fields.push({ field_id: field.id, value: null })
  publish(next)
}

function setCustomField(index, fieldId) {
  const next = cloneFilters()
  next.custom_fields[index] = { field_id: fieldId, value: null }
  publish(next)
}

function setUnset(index, isUnset, field) {
  const next = cloneFilters()
  const value = isUnset ? null : field.field_type === 'multiselect'
    ? []
    : field.field_type === 'checkbox'
      ? false
      : field.field_type === 'number'
        ? 0
        : field.field_type === 'select'
          ? field.options?.[0] || ''
          : ''
  next.custom_fields[index] = { ...next.custom_fields[index], value }
  publish(next)
}

function setCustomValue(index, value, fieldType) {
  const next = cloneFilters()
  const normalized = fieldType === 'number' && value !== '' && value !== null ? Number(value) : value
  next.custom_fields[index] = { ...next.custom_fields[index], value: normalized }
  publish(next)
}

function removeCustomField(index) {
  const next = cloneFilters()
  next.custom_fields.splice(index, 1)
  publish(next)
}

function customValueComponent(fieldId) {
  const type = fieldFor(fieldId)?.field_type
  if (type === 'select' || type === 'multiselect' || type === 'checkbox') return 'v-select'
  return 'v-text-field'
}

function customValueItems(field) {
  if (field.field_type === 'checkbox') return [{ title: 'True', value: true }, { title: 'False', value: false }]
  return field.options || []
}

async function loadOptions() {
  if (!props.spaceId) return
  const requestId = ++optionsRequestId.value
  const requestedSpaceId = props.spaceId
  loadError.value = false
  try {
    const [fieldsResponse, tagsResponse] = await Promise.all([
      customFieldService.list(requestedSpaceId, 'testcase'),
      testCaseService.listTagsBySpace(requestedSpaceId),
    ])
    if (requestId !== optionsRequestId.value || requestedSpaceId !== props.spaceId) return
    customFields.value = fieldsResponse.data || []
    tagOptions.value = tagsResponse.data || []
  } catch {
    if (requestId === optionsRequestId.value && requestedSpaceId === props.spaceId) loadError.value = true
  }
}

watch(() => props.spaceId, () => {
  customFields.value = []
  tagOptions.value = []
  loadOptions()
})
onMounted(loadOptions)
</script>

<style scoped>
.custom-filter-row {
  display: grid;
  grid-template-columns: minmax(120px, 0.8fr) minmax(200px, 1.5fr) auto;
  align-items: start;
  gap: 8px;
}

.custom-filter-value {
  display: grid;
  grid-template-columns: auto minmax(120px, 1fr);
  align-items: start;
  gap: 8px;
}
</style>
