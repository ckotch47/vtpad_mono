<template>
  <v-expansion-panels class="my-4">
    <v-expansion-panel>
      <v-expansion-panel-title>{{ title }}</v-expansion-panel-title>
      <v-expansion-panel-text>
        <v-table class="my-4">
          <thead>
            <tr>
              <th class="text-left" width="120">Id</th>
              <th class="text-left" width="370">Title</th>
              <th class="text-left" width="100">State</th>
              <th class="text-left" width="150">Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in dataList" :key="item.id">
              <td>
                <a :href="`/issue/${item.short_name}`" target="_blank" class="text-decoration-none href--unset">{{ item.short_name }}</a>
              </td>
              <td>
                <a :href="`/issue/${item.short_name}`" target="_blank" class="text-decoration-none href--unset">{{ item.title }}</a>
              </td>
              <td :class="`color-state--${item.state}`">
                <span :class="`color-state--${item.state}`">{{ item.state }}</span>
              </td>
              <td>{{ item.create_date.split('T')[0] }}</td>
            </tr>
          </tbody>
        </v-table>
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script setup>
defineProps({
  title: String,
  dataList: Array
})
</script>

<style scoped>
.href--unset {
  color: unset;
}
</style>
