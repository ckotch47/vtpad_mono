<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <settings-user-component />
  </v-container>
</template>

<script>
import SettingsUserComponent from "@/components/settings/settingsUserComponent.vue";

export default {
  name: "usersSettingPage",
  components: {SettingsUserComponent}
}
</script>
<route>
{
meta: {
layout: "spacesSettings",
tabValue: "users"
}
}
</route>
<style scoped>

</style>
