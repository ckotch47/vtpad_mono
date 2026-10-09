<template>
  <v-card variant="outlined" class="list-page-toolbar mb-4">
    <v-card-text class="list-page-toolbar__body">
      <div v-if="$slots.filters" class="list-page-toolbar__filters">
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

@media (min-width: 960px) {
  .list-page-toolbar__body {
    gap: 10px;
  }

  .list-page-toolbar__actions {
    order: -1;
    justify-content: flex-start;
  }

  .list-page-toolbar__filters {
    align-items: flex-start;
    width: 100%;
  }

  .list-page-toolbar__filters > :deep(.v-input) {
    min-width: 0;
  }

  .list-page-toolbar :deep(.v-btn:focus-visible),
  .list-page-toolbar :deep(.v-field:focus-within) {
    outline: 2px solid currentColor;
    outline-offset: 2px;
  }
}
</style>
