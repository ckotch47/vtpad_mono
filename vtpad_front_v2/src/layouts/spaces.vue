<template>
  <v-app>
      <v-tabs
        fixed-tabs
        align-tabs="start"
        color="primary"
        v-model="tab"
        class="rounded-0_custom"
      >
        <v-tab :to="`/space/${spaceId}/bugs`"  value="bugs">Bugs</v-tab>
        <v-tab :to="`/space/${spaceId}/test-suites`"  value="test-suites" >Test Suites</v-tab>
        <v-tab :to="`/space/${spaceId}/test-runs`"  value="test-runs">Test Runs</v-tab>
      </v-tabs>


      <router-view></router-view>

  </v-app>
</template>

<script>
import {useRouter} from "vue-router";

export default {
  name: "spacesLayouts",
  data: () => ({
    drawer: null,
    routerMeta: {},
    spaceId: undefined,
    tab: undefined
  }),
  mounted() {
    this.routerMeta = useRouter().currentRoute.value.meta;
    this.spaceId = useRouter().currentRoute.value.params.spaceId;
    this.tab = this.routerMeta.tabValue;
  },
  updated() {
    this.routerMeta = useRouter().currentRoute.value.meta;
    this.spaceId = useRouter().currentRoute.value.params.spaceId;
    this.tab = this.routerMeta.tabValue;
  }
}
</script>

<style scoped>

</style>
