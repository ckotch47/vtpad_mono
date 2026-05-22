<template>
  <div class="d-flex">
    <div class="w-66">
      <pads-detail-list-item-component :items="items" :pad-id="padId"/>
    </div>

  </div>
</template>

<script>
import PadsDetailListItemComponent from "@/components/pads/detail/padsDetailListItemComponent.vue";
// import PadsDetailHalfRightComponent from "@/components/pads/detail/v2/padsDetailHalfRightComponent.vue";

export default {
  components: {PadsDetailListItemComponent},
  props:{
    items: Array,
    padId: String
  },
  name: "padsDetailHalfComponent"
}
</script>

<style scoped>

</style>
