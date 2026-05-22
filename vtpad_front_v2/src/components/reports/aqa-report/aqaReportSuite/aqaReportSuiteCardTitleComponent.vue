<template>
  <div class="d-flex justify-space-between suites-card_top pa-4">
    <div class="d-flex flex-column justify-space-between suites-card_top--info">
      <div class="suites-card_top--info__header">
        <div class="header-title">{{suiteItem.name}}</div>
        <div class="header-date">{{suiteItem.create_at.split('T')[0]}}</div>
      </div>
    </div>

    <div class="suites-card_top--info__status">
      <span class="ma-2 "  v-for="(item, i) in Object.keys(suiteItem.statistic)" :key="i">
        {{item.toUpperCase()}}: <span :class="`aqa-color--${item.toUpperCase()}`">{{suiteItem.statistic[item]}}</span>
      </span>
    </div>
  </div>
</template>

<script>

export default {
  name: "aqaReportSuiteCardTitleComponent",
  props:{
    suiteItem: Object
  },
  data(){
    return{
    }
  },
  mounted() {
  }
}
</script>

<style scoped lang="scss">
.suites-card{
  &_top{
    &--info{
      &__header{
        .header-title{
          font-size: 1.5rem;
          line-height: 110%;
        }
        .header-date{
          color: rgba(var(--v-theme-surface-variant),var(--v-theme-surface-variant-overlay-multiplier));
          font-size: .8rem;
        }
      }
      &__status{

      }
    }
  }
}
</style>
