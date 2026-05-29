<template>
  <div class="d-flex justify-space-between suites-card_top pa-4">
    <div class="d-flex flex-column justify-space-between suites-card_top--info">
      <div class="suites-card_top--info__header">
        <div class="header-title text-h6">{{ suiteItem.name }}</div>
        <div class="header-date text-caption">{{ suiteItem.create_at.split('T')[0] }}</div>
      </div>
    </div>

    <div class="suites-card_top--info__status">
      <span v-for="(item, i) in Object.keys(suiteItem.statistic)" :key="i" class="ma-2">
        {{ item.toUpperCase() }}: <span :class="`aqa-color--${item.toUpperCase()}`">{{ suiteItem.statistic[item] }}</span>
      </span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  suiteItem: Object
})
</script>

<style scoped lang="scss">
.suites-card {
  &_top {
    &--info {
      &__header {
        .header-title {
          line-height: 110%;
        }
        .header-date {
          color: rgba(var(--v-theme-surface-variant), var(--v-theme-surface-variant-overlay-multiplier));
        }
      }
      &__status {}
    }
  }
}
</style>
