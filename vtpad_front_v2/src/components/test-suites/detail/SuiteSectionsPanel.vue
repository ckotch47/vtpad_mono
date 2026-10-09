<template>
  <v-card>
    <v-card-title class="d-flex align-center py-3">
      <v-icon class="mr-2">mdi-folder-open-outline</v-icon>
      Sections
      <v-spacer />
      <v-btn icon size="small" variant="text" aria-label="Add section" @click="$emit('add-section')">
        <v-icon>mdi-plus</v-icon>
      </v-btn>
    </v-card-title>
    <v-divider />
    <div class="section-filter px-3 pt-3">
      <v-text-field
        v-model="sectionQuery"
        label="Filter sections"
        prepend-inner-icon="mdi-magnify"
        density="compact"
        variant="outlined"
        hide-details
        clearable
        aria-label="Filter sections by name"
        @click:clear="sectionQuery = ''"
      />
      <div class="d-flex align-center justify-space-between mt-2 text-caption text-medium-emphasis">
        <span>{{ filteredSections.length }} of {{ localSections.length }} sections</span>
        <v-btn
          v-if="sectionQuery"
          size="small"
          variant="text"
          class="section-filter-clear"
          @click="sectionQuery = ''"
        >
          Clear filter
        </v-btn>
      </div>
    </div>
    <v-alert v-if="sortError" type="error" density="compact" class="ma-3" role="alert">
      <div class="d-flex align-center justify-space-between ga-2">
        <span>{{ sortError }}</span>
        <v-btn size="small" variant="text" :disabled="sorting" @click="retrySort">Retry</v-btn>
      </div>
    </v-alert>
    <v-alert
      v-if="selectedSectionHidden"
      type="info"
      density="compact"
      class="ma-3"
      role="status"
    >
      <div class="d-flex align-center justify-space-between ga-2">
        <span>The selected section is hidden by this filter.</span>
        <v-btn size="small" variant="text" @click="sectionQuery = ''">Show selection</v-btn>
      </div>
    </v-alert>
    <v-card-text class="pa-0">
      <v-list density="compact" class="section-list" aria-label="Suite sections">
        <v-list-item
          v-for="item in filteredSections"
          :key="item.id"
          :active="selectedSection?.id === item.id"
          :aria-label="`${item.name}, ${item.test_case_count || 0} test cases${selectedSection?.id === item.id ? ', selected' : ''}`"
          rounded="sm"
          class="section-list-item"
          @click="selectSection(item.id)"
          @dragover="onDragOver($event, item)"
          @drop="onDrop($event, item)"
          @dragend="draggedId = null"
        >
          <template #prepend>
            <div class="d-flex align-center">
              <div :style="{ width: `${item.level * 14}px` }" />
              <v-btn
                class="section-drag-handle"
                icon="mdi-drag"
                size="x-small"
                variant="text"
                :draggable="!sorting"
                :aria-label="`Drag ${item.name} to reorder within its parent`"
                :disabled="sorting"
                @click.stop
                @dragstart="onDragStart($event, item)"
              />
              <v-icon size="small" color="primary">mdi-folder-outline</v-icon>
            </div>
          </template>
          <v-list-item-title class="text-body-2" :title="item.name">
            {{ item.name }}
            <v-chip size="x-small" color="primary" variant="outlined" class="ml-2">
              {{ item.test_case_count || 0 }}
            </v-chip>
          </v-list-item-title>
          <template #append>
            <div class="d-flex align-center">
              <v-btn
                icon="mdi-chevron-up"
                size="x-small"
                variant="text"
                :aria-label="`Move ${item.name} up`"
                :disabled="sorting || !hasSiblingAt(item, -1)"
                @click.stop="moveByKeyboard(item, -1)"
              />
              <v-btn
                icon="mdi-chevron-down"
                size="x-small"
                variant="text"
                :aria-label="`Move ${item.name} down`"
                :disabled="sorting || !hasSiblingAt(item, 1)"
                @click.stop="moveByKeyboard(item, 1)"
              />
              <v-menu location="end" :close-on-content-click="true">
                <template #activator="{ props: menuProps }">
                  <v-btn
                    icon="mdi-dots-vertical"
                    size="x-small"
                    variant="text"
                    :aria-label="`More actions for ${item.name}`"
                    :title="`More actions for ${item.name}`"
                    v-bind="menuProps"
                    @click.stop
                  />
                </template>
                <v-list density="compact">
                  <v-list-item @click="$emit('add-sub-section', item.id)">
                    <template #prepend><v-icon>mdi-plus</v-icon></template>
                    <v-list-item-title>Add sub-section</v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="$emit('rename-section', item)">
                    <template #prepend><v-icon>mdi-pencil</v-icon></template>
                    <v-list-item-title>Rename</v-list-item-title>
                  </v-list-item>
                  <v-list-item class="text-error" @click="$emit('delete-section', item.id)">
                    <template #prepend><v-icon color="error">mdi-delete</v-icon></template>
                    <v-list-item-title>Delete</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </div>
          </template>
        </v-list-item>
        <div v-if="sectionQuery && filteredSections.length === 0" class="pa-4 text-body-2 text-medium-emphasis" role="status">
          <div>No sections match “{{ sectionQuery }}”.</div>
          <v-btn class="mt-2" size="small" variant="text" @click="sectionQuery = ''">Clear filter</v-btn>
        </div>
        <div v-else-if="!sectionQuery && localSections.length === 0" class="pa-4 text-body-2 text-medium-emphasis" role="status">
          No sections yet. Add a section to organize this suite.
        </div>
      </v-list>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { sectionService } from '@/services'

const props = defineProps({
  flatSections: { type: Array, default: () => [] },
  selectedSection: { type: Object, default: null }
})

const emit = defineEmits(['select-section', 'add-section', 'add-sub-section', 'rename-section', 'delete-section', 'reorder'])
const localSections = ref([...props.flatSections])
const sectionQuery = ref('')
const filteredSections = computed(() => {
  const query = sectionQuery.value.trim().toLocaleLowerCase()
  if (!query) return localSections.value

  const byId = new Map(localSections.value.map(section => [String(section.id), section]))
  const visibleIds = new Set()
  for (const section of localSections.value) {
    if (!section.name.toLocaleLowerCase().includes(query)) continue
    let current = section
    const visited = new Set()
    while (current && !visited.has(String(current.id))) {
      const id = String(current.id)
      visited.add(id)
      visibleIds.add(id)
      current = current.parentId == null ? null : byId.get(String(current.parentId))
    }
  }
  return localSections.value.filter(section => visibleIds.has(String(section.id)))
})
const selectedSectionHidden = computed(() => Boolean(
  sectionQuery.value && props.selectedSection &&
  !filteredSections.value.some(section => String(section.id) === String(props.selectedSection.id))
))
const sorting = ref(false)
const sortError = ref('')
const draggedId = ref(null)
let lastAction = null
let suppressNextClick = false

watch(() => props.flatSections, sections => {
  if (!sorting.value) localSections.value = [...sections]
}, { deep: true })

function siblingsOf(item) {
  return localSections.value.filter(section => section.parentId === item.parentId)
}

function siblingPosition(item) {
  return siblingsOf(item).findIndex(section => section.id === item.id)
}

function hasSiblingAt(item, offset) {
  const siblings = siblingsOf(item)
  const position = siblingPosition(item) + offset
  return position >= 0 && position < siblings.length
}

function subtreeEndIndex(sections, startIndex) {
  const level = sections[startIndex].level
  let index = startIndex + 1
  while (index < sections.length && sections[index].level > level) index += 1
  return index
}

function applyLocalMove(sectionId, neighborId, placement) {
  const sections = [...localSections.value]
  const sourceStart = sections.findIndex(section => section.id === sectionId)
  const sourceEnd = subtreeEndIndex(sections, sourceStart)
  const moving = sections.splice(sourceStart, sourceEnd - sourceStart)
  const neighborStart = sections.findIndex(section => section.id === neighborId)
  const insertAt = placement === 'before' ? neighborStart : subtreeEndIndex(sections, neighborStart)
  sections.splice(insertAt, 0, ...moving)
  return sections
}

async function runSort(action) {
  if (sorting.value) return
  const previousSections = [...localSections.value]
  const optimisticSections = applyLocalMove(action.sectionId, action.neighborId, action.placement)
  if (optimisticSections.every((section, index) => section.id === previousSections[index]?.id)) return

  sorting.value = true
  sortError.value = ''
  lastAction = action
  localSections.value = optimisticSections
  try {
    await sectionService.sort(action.sectionId, {
      [action.placement === 'before' ? 'sort_before_id' : 'sort_after_id']: action.neighborId
    })
    emit('reorder', optimisticSections)
    lastAction = null
  } catch (error) {
    localSections.value = previousSections
    sortError.value = error?.response?.data?.detail || 'Could not reorder sections. Your previous order was restored.'
  } finally {
    sorting.value = false
  }
}

function retrySort() {
  if (lastAction) runSort(lastAction)
}

function selectSection(id) {
  if (suppressNextClick) {
    suppressNextClick = false
    return
  }
  emit('select-section', id)
}

function moveByKeyboard(item, offset) {
  const siblings = siblingsOf(item)
  const index = siblingPosition(item)
  const neighbor = siblings[index + offset]
  if (!neighbor) return
  runSort({
    sectionId: item.id,
    neighborId: neighbor.id,
    placement: offset < 0 ? 'before' : 'after'
  })
}

function onDragStart(event, item) {
  if (!event.target.closest('.section-drag-handle')) {
    event.preventDefault()
    return
  }
  draggedId.value = item.id
  event.dataTransfer?.setData('text/plain', String(item.id))
  if (event.dataTransfer) event.dataTransfer.effectAllowed = 'move'
}

function onDragOver(event, item) {
  const dragged = localSections.value.find(section => section.id === draggedId.value)
  if (!dragged || dragged.parentId !== item.parentId || dragged.id === item.id) return
  event.preventDefault()
  if (event.dataTransfer) event.dataTransfer.dropEffect = 'move'
}

function onDrop(event, item) {
  const dragged = localSections.value.find(section => section.id === draggedId.value)
  if (!dragged || dragged.parentId !== item.parentId || dragged.id === item.id) return
  event.preventDefault()
  const bounds = event.currentTarget.getBoundingClientRect()
  const placement = event.clientY < bounds.top + bounds.height / 2 ? 'before' : 'after'
  draggedId.value = null
  suppressNextClick = true
  setTimeout(() => { suppressNextClick = false }, 300)
  runSort({ sectionId: dragged.id, neighborId: item.id, placement })
}
</script>

<style scoped>
.section-list-item {
  cursor: pointer;
}

.section-drag-handle {
  cursor: grab;
  touch-action: none;
  user-select: none;
}
</style>
