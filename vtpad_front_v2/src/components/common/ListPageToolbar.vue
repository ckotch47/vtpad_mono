<template>
  <v-card variant="outlined" class="list-page-toolbar mb-4">
    <v-card-text class="list-page-toolbar__body">
      <div class="list-page-toolbar__filters">
        <slot name="filters" />
      </div>
      <div v-if="$slots.actions" class="list-page-toolbar__actions">
        <slot name="actions" />
      </div>
    </v-card-text>
  </v-card>
</template>

<style scoped>
.list-page-toolbar {
  border-radius: 12px;
}

.list-page-toolbar__body {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px;
}

.list-page-toolbar__filters,
.list-page-toolbar__actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  min-width: 0;
}

.list-page-toolbar__actions {
  justify-content: flex-end;
}
</style>
