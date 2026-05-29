<template>
  <v-table>
    <thead>
      <tr>
        <th class="text-left" width="700">Name</th>
        <th class="text-left" width="200">Status</th>
        <th class="text-left" width="100">Time</th>
        <th class="text-left" width="100">Message</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="item in suiteItems" :key="item.id">
        <td>{{ item.name }}</td>
        <td><span :class="`aqa-color--${item.status.toUpperCase()}`">{{ item.status }}</span></td>
        <td>{{ item.duration }}</td>
        <td>
          <v-btn
            v-if="item.message"
            color="grey-lighten-1"
            icon="mdi-eye"
            variant="plain"
            @click="$emit('showModalMessageSuiteEmit', item.message)"
          />
        </td>
      </tr>
    </tbody>
  </v-table>
</template>

<script setup>
defineProps({
  suiteItems: Array
})
defineEmits(['showModalMessageSuiteEmit'])
</script>
