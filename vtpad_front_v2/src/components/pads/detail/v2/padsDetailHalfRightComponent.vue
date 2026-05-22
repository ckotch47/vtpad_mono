<template>

  <div v-if="!isShowTabs">
    <div class="d-none">
      <v-text-field placeholder="Title" style="margin-top: 20px;"/>
    </div>



<!--    <pads-right-description-component-->

<!--      v-on:SaveDescriptionPadEmit="{}"-->
<!--      :text="openItem?.description"-->
<!--      :edit="canEdit"-->
<!--    />-->

    <pads-right-check-list-component
      :edit="canEdit"
      :item-id="openItem?.id"
    />

    <pads-right-test-cse-list-component
      :edit="canEdit"
      :item-id="openItem?.id"
      />

    <pads-right-bugs-component
      v-if="isShowBugs"
      :edit="canEdit"

    />

  </div>


</template>

<script>
import PadsRightBugsComponent from "@/components/pads/detail/right/padsRightBugsComponent.vue";
import PadsRightCheckListComponent from "@/components/pads/detail/right/padsRightCheckListComponent.vue";

import PadsRightTestCseListComponent from "@/components/pads/detail/right/padsRightTestCseListComponent.vue";
// import RightRunDetailStateComponent from "@/components/runs/detail/right/rightRunDetailStateComponent.vue";
import {useAppStore} from "@/stores/app";
export default {
  name: "padsDetailHalfRightComponent",
  components: {
    // RightRunDetailStateComponent,
    PadsRightTestCseListComponent,

     PadsRightCheckListComponent, PadsRightBugsComponent},
  props: {
    isShowBugs: Boolean,
    isShowTabs: Boolean,
    canEdit: Boolean,

  },
  data: () => ({
    tab: null,
    store: useAppStore(),
    openItem: undefined
  }),
  mounted() {
    this.openItem = this.store.getOpenItem
  },
  watch:{
    "store.getOpenItem"(newValue) {
      this.openItem = newValue
    }
  }
}
</script>

<style lang="scss">
.v-expansion-panel-text__wrapper{
  .editor-custom{
    margin: 2px !important;
  }
}
.v-timeline-item__body{
  width: 100%;
}
</style>
