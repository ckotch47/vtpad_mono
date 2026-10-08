<template>
  <div
    class="list-loading-skeleton"
    :class="`list-loading-skeleton--${variant}`"
    role="status"
    aria-live="polite"
  >
    <span class="list-loading-skeleton__label">Loading {{ label }}…</span>
    <v-progress-linear indeterminate color="primary" height="2" aria-hidden="true" />
    <div
      v-for="row in rows"
      :key="row"
      class="list-loading-skeleton__row"
      :class="`list-loading-skeleton__row--${variant}`"
      :style="variant === 'table' ? { '--skeleton-columns': columns } : undefined"
      aria-hidden="true"
    >
      <template v-if="variant === 'table'">
        <v-skeleton-loader
          v-for="column in columns"
          :key="column"
          type="text"
          class="list-loading-skeleton__cell"
        />
      </template>
      <template v-else>
        <v-skeleton-loader type="avatar" class="list-loading-skeleton__icon" />
        <div class="list-loading-skeleton__text">
          <v-skeleton-loader type="text" />
          <v-skeleton-loader v-if="variant === 'list'" type="text" class="list-loading-skeleton__secondary" />
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
defineProps({
  variant: { type: String, default: 'table', validator: value => ['table', 'list', 'tree'].includes(value) },
  rows: { type: Number, default: 6 },
  columns: { type: Number, default: 5 },
  label: { type: String, default: 'items' }
})
</script>

<style scoped>
.list-loading-skeleton {
  overflow: hidden;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 8px;
  background: rgb(var(--v-theme-surface));
}

.list-loading-skeleton__label {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.list-loading-skeleton__row {
  min-height: 52px;
  padding: 0 16px;
  border-bottom: 1px solid rgba(var(--v-border-color), 0.55);
}

.list-loading-skeleton__row:last-child {
  border-bottom: 0;
}

.list-loading-skeleton__row--table {
  display: grid;
  grid-template-columns: repeat(var(--skeleton-columns), minmax(0, 1fr));
  align-items: center;
  gap: 20px;
}

.list-loading-skeleton__cell {
  width: 100%;
  max-width: 170px;
}

.list-loading-skeleton__row--list,
.list-loading-skeleton__row--tree {
  display: flex;
  align-items: center;
  gap: 12px;
}

.list-loading-skeleton__icon {
  width: 28px;
  flex: 0 0 28px;
}

.list-loading-skeleton__text {
  flex: 1;
  min-width: 0;
}

.list-loading-skeleton__secondary {
  max-width: 55%;
}

.list-loading-skeleton--table {
  min-height: 360px;
}

.list-loading-skeleton--list {
  min-height: 280px;
}

.list-loading-skeleton--tree {
  min-height: 320px;
  border: 0;
  border-radius: 0;
}
</style>
