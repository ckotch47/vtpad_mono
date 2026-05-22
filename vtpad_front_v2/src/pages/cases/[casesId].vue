<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <cases-detail-component :short-name="shortName"/>
  </v-container>
</template>

<script>
import CasesDetailComponent from "@/components/cases/detail/casesDetailComponent.vue";

export default {
  name: "TestCaseDetailPage",
  components: {CasesDetailComponent},
  data(){
    return{
      shortName: this.$route.params.casesId,
    }
  }
}
</script>

<style scoped>

</style>
