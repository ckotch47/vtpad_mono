<template>

  <v-app>
      <router-view></router-view>
  </v-app>
</template>


<script setup>

</script>

<script>
import {useRouter} from "vue-router";

export default {
  name: "LayoutsDefaultComponent",
  data: () => ({
    drawer: null,
    routerMeta: {},
    spaceId: undefined
  }),
  mounted() {
    this.routerMeta = useRouter().currentRoute.value.meta;
    this.spaceId = useRouter().currentRoute.value.params.id;
  },
  updated() {
    this.routerMeta = useRouter().currentRoute.value.meta
    this.spaceId = useRouter().currentRoute.value.params.id
  }
}
</script>
<style lang="scss">
.v-navigation-drawer{
  //display: none !important;
}
</style>
