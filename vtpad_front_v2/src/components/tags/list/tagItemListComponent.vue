<template>
  <div class="d-flex w-100">
    <v-text-field
      :label="tag.title"
      variant="underlined"
      class="text-field my-4 w-75"
      v-model="tag.title"
    />

    <div class="color-picker w-25">
      <div style="position:relative; display:inline-block; cursor: pointer">
<!--        <v-btn class="btn-tag&#45;&#45;color" :text="'Color'" :color="tag.color"/>-->

        <custom-chip-component :color="tag.color" :text="tag.title ?? 'Color'" />
        <input type="color" v-model="tag.color" style="opacity:0; position:absolute; left:0;top:0;width:100%"/>
      </div>

      <v-btn :text="'Save'" variant="outlined" color="primary" @click="updateTag"/>
      <v-btn :text="'Delete'" variant="outlined" color="red" @click="deleteTag"/>
    </div>

  </div>
</template>

<script>
import CustomChipComponent from "@/components/common/chips/customChipComponent.vue";
import { tagService } from '@/services'

export default {
  name: "tagItemListComponent",
  components: {CustomChipComponent},
  emits: ['deleteTagEmit', 'updateTagEmit'],
  props:{
    tag: Object
  },
  methods:{
    deleteTag(){
      tagService.delete(this.tag.id).then(res => {
        this.$emit('deleteTagEmit')
      })
    },
    updateTag(){
      tagService.update(this.tag.id, {
        title: this.tag.title,
        color: this.tag.color
      }).then(res => {
        this.$emit('updateTagEmit')
      })
    }
  }
}
</script>

<style scoped>

</style>
