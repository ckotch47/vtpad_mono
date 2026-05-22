<template>

  <settings-main-component />
<!--    <v-tabs-window v-model="tab">-->
<!--      <v-tabs-window-item value="main">-->
<!--        <settings-main-component />-->
<!--      </v-tabs-window-item>-->

<!--      <v-tabs-window-item value="users">-->
<!--        <settings-user-component />-->
<!--      </v-tabs-window-item>-->

<!--    </v-tabs-window>-->

</template>

<script>
import SettingsMainComponent from "@/components/settings/settingsMainComponent.vue";
import SettingsUserComponent from "@/components/settings/settingsUserComponent.vue";

export default {
  name: "settingsComponent",
  components: { SettingsMainComponent},
  data: () => ({
    tab: null,
  }),
}
</script>

<style scoped>

</style>
