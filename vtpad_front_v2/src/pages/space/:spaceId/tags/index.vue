<route lang="json">
{
  "meta": {
    "layout": "spaces",
    "tabValue": "tags"
  }
}
</route>

<template>
  <v-container class="mx-auto custom-container max-width-1500">
    <tags-list-component />
  </v-container>
</template>

<script setup>
import TagsListComponent from '@/components/tags/tagsListComponent.vue'
</script>

<style lang="scss">
.tag-list{
  .text-field{
    min-width: 200px;
    min-height: 32px !important;
  }

  .color-picker{
    margin: 0 20px 20px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    input{
      height: 40px;
    }
    button{
      margin-left: 20px;
    }
  }
}
</style>
