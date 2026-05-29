<template>
  <v-card>
    <v-card-item>
      <v-autocomplete
        :items="testList"
        item-title="name"
        item-value="id"
        label="Report"
        variant="underlined"
        @update:modelValue="$emit('selectTestLstEmit', $event)"
      />
    </v-card-item>
  </v-card>
</template>

<script setup>
defineProps({
  testList: Array
})
defineEmits(['selectTestLstEmit'])
</script>
