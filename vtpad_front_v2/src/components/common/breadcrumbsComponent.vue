<template>
  <v-breadcrumbs :items="items" class="pa-0 mb-2">
    <template v-slot:prepend>
      <v-icon size="small" icon="mdi-home" />
    </template>
    <template v-slot:divider>
      <v-icon icon="mdi-chevron-right" size="small" />
    </template>
  </v-breadcrumbs>
</template>

<script>
export default {
  name: "breadcrumbsComponent",
  props: {
    items: {
      type: Array,
      default: () => []
    }
  }
}
</script>
