<template>
  <v-container class="mx-auto custom-container max-width-1500">
      <bugs-list-component :spase-id-from="this.spaceId"/>
  </v-container>
</template>

<script>
import BugsListComponent from "@/components/bugs/bugsListComponent.vue";

export default {
  name: "spaceBugsPage",
  components: {BugsListComponent},
  data(){
    return{
      spaceId: undefined
    }
  },
  mounted() {
    this.spaceId = this.$route.params.spaceId
  },
  updated() {
    this.spaceId = this.$route.params.spaceId
  }
}
</script>
<route lang="json">
  {
    "meta": {
      "layout": "spaces",
      "tabValue": "bugs"
    }
  }
</route>

<style lang="scss">

</style>
