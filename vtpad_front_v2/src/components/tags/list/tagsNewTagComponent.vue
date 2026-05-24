<template>
  <div class="d-flex">
    <v-text-field
      label="Tags"
      variant="underlined"
      class="text-field my-4 w-75"
      v-model="titleValue"
    />
    <div class="color-picker w-25">
      <div style="position:relative; display:inline-block; cursor: pointer">
<!--        <v-chip-->
<!--          :color="colorValue"-->
<!--          :text="'Color'"-->
<!--        />-->
        <custom-chip-component :color="colorValue" :text="titleValue ?? 'Color'" />
        <input type="color" v-model="colorValue"  style="opacity:0; position:absolute; left:0;top:0;width:100%"/>
      </div>

      <v-btn :text="'Save'" variant="outlined" color="primary" @click="createTag"/>

    </div>
  </div>
</template>

<script>

import CustomChipComponent from "@/components/common/chips/customChipComponent.vue";
import { tagService } from '@/services'

export default {
  name: "tagsNewTagComponent",
  components: {CustomChipComponent},
  emits: ['createNewTagEmit'],
  props:{
    spaceId: String
  },
  data(){
    return{
      colorValue: '#ff0000',
      titleValue: undefined
    }
  },
  methods:{
    createTag(){
      tagService.create(this.spaceId,{
        title: this.titleValue,
        color: this.colorValue
      }).then(res => {
        this.$emit('createNewTagEmit', res.data)
      })
    }
  }

}
</script>

<style lang="scss">
.btn-tag--color{

}
</style>
