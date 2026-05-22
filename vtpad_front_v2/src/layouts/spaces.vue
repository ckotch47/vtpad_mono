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
        <v-tab :to="`/space/${spaceId}/pads`"  value="pads" >Pads</v-tab>
        <v-tab :to="`/space/${spaceId}/runs`"  value="runs">Runs</v-tab>
        <v-tab :to="`/space/${spaceId}/cases`" value="cases">Test Cases</v-tab>
        <v-tab :to="`/space/${spaceId}/checklist`" value="checklist">Check list</v-tab>
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
