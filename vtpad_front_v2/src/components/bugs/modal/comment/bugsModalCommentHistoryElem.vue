<template>
  <v-expansion-panels class="expansion-custom">
    <v-expansion-panel>
      <v-expansion-panel-title>
        <div class="d-flex justify-space-between flex-grow-1">
          {{ comment.create_user.username }} change {{ textJson.name }}
          <div class="flex-shrink-0">
            {{ comment.create_date ? comment.create_date.split('T')[0] : '' }}
          </div>
        </div>
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <s v-html="sanitizedFrom" /> <span v-html="sanitizedTo" />
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { sanitizeHtml } from '@/utils/sanitize'

const props = defineProps({
  username: String,
  text: String,
  date: String,
  comment: Object
})

const textJson = ref({
  name: undefined,
  from: undefined,
  to: undefined
})

const sanitizedFrom = computed(() => sanitizeHtml(textJson.value?.from))
const sanitizedTo = computed(() => sanitizeHtml(textJson.value?.to))

onMounted(() => {
  try {
    textJson.value = JSON.parse(props.comment.text)
  } catch (e) {
    textJson.value = {
      name: undefined,
      from: undefined,
      to: undefined
    }
  }
})
</script>

<style lang="scss">
.expansion-custom {
  .v-expansion-panel {
    &__shadow {
      box-shadow: none;
    }
    &-title {
      padding: 0;
      min-height: unset;
      border: none;
      &--active {
        min-height: unset !important;
      }
      &:hover {
        background-color: unset;
      }
      &__icon {
        display: none;
      }
    }
  }
}
</style>
