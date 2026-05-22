<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <settings-main-component />
  </v-container>
</template>

<script>

import SettingsMainComponent from "@/components/settings/settingsMainComponent.vue";

export default {
  name: "SpaceSettingsComponent",
  components: {SettingsMainComponent},

}
</script>
<route>
  {
  meta: {
    layout: "spacesSettings",
    tabValue: "index"
  }
}
</route>
<style scoped>

</style>
