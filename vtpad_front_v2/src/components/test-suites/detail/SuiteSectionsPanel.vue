<template>
  <v-card>
    <v-card-title class="d-flex align-center py-3">
      <v-icon class="mr-2">mdi-folder-open-outline</v-icon>
      Sections
      <v-spacer />
      <v-btn icon size="small" variant="text" @click="$emit('add-section')">
        <v-icon>mdi-plus</v-icon>
      </v-btn>
    </v-card-title>
    <v-divider />
    <v-card-text class="pa-0">
      <v-list density="compact" class="section-list">
        <v-list-item
          v-for="item in flatSections"
          :key="item.id"
          :active="selectedSection?.id === item.id"
          rounded="sm"
          class="section-list-item"
          @click="$emit('select-section', item.id)"
        >
          <template #prepend>
            <div class="d-flex align-center">
              <div :style="{ width: `${item.level * 14}px` }" />
              <v-icon size="small" color="primary">mdi-folder-outline</v-icon>
            </div>
          </template>
          <v-list-item-title class="text-body-2">
            {{ item.name }}
            <v-chip size="x-small" color="primary" variant="outlined" class="ml-2">
              {{ item.test_case_count || 0 }}
            </v-chip>
          </v-list-item-title>
          <template #append>
            <v-menu location="end" :close-on-content-click="true">
              <template #activator="{ props: menuProps }">
                <v-btn icon="mdi-dots-vertical" size="x-small" variant="text" v-bind="menuProps" @click.stop />
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
          </template>
        </v-list-item>
      </v-list>
    </v-card-text>
  </v-card>
</template>

<script setup>
defineProps({
  flatSections: { type: Array, default: () => [] },
  selectedSection: { type: Object, default: null }
})

defineEmits(['select-section', 'add-section', 'add-sub-section', 'rename-section', 'delete-section'])
</script>

<style scoped>
.section-list-item {
  cursor: pointer;
}
</style>
