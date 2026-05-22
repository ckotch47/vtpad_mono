<template>
  <v-app>
    <v-tabs
      fixed-tabs
      align-tabs="start"
      color="primary"
      v-model="tab"
      class="rounded-0_custom"
    >
<!--      <v-tab :to="`/company`" value="info">Info</v-tab>-->
      <v-tab :to="`/company/users`" value="users">Users</v-tab>
      <v-tab :to="`/company/spaces`" value="spaces">Spaces</v-tab>

    </v-tabs>

        <router-view></router-view>
  </v-app>
</template>

<script>
import {useRouter} from "vue-router";

export default {
  name: "company",
  data: () => ({
    drawer: null,
    routerMeta: {},
    spaceId: undefined,
    tab: undefined
  }),
  mounted() {
    this.routerMeta = useRouter().currentRoute.value.meta;
    this.spaceId = useRouter().currentRoute.value.params.id;
    this.tab = this.routerMeta.tabValue;
  },
  updated() {
    this.routerMeta = useRouter().currentRoute.value.meta;
    this.spaceId = useRouter().currentRoute.value.params.id;
    this.tab = this.routerMeta.tabValue;
  }
}
</script>

<style scoped>

</style>
