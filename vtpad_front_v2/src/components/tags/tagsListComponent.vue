<template>
  <div v-if="loader">
    <v-progress-linear
      color="primary"
      indeterminate
    ></v-progress-linear>
  </div>
  <v-card v-if="!loader">
    <v-card-item class="tag-list py-4">
      <div class="d-flex flex-column" v-if="!loader">
        <tags-new-tag-component @createNewTagEmit="getTagForSpace" :space-id="spaceId"/>
        <tag-item-list-component
          v-for="item in tagItems"
          :key="item.id"
          :tag="item"
          @deleteTagEmit="getTagForSpace"
          @updateTagEmit="getTagForSpace"
        />
      </div>
    </v-card-item>
  </v-card>

</template>

<script>
import { tagService } from '@/services'
import TagsNewTagComponent from "@/components/tags/list/tagsNewTagComponent.vue";
import TagItemListComponent from "@/components/tags/list/tagItemListComponent.vue";

export default {
  name: "tagsListComponent",
  components: {TagItemListComponent, TagsNewTagComponent},
  data(){
    return{
      loader: true,
      tagItems: [],
      spaceId: this.$route.params.spaceId,
    }
  },
  mounted() {
    this.getTagForSpace()
  },
  methods:{
    getTagForSpace(){
      this.loader = true
      tagService.list(this.spaceId).then(res => {
        this.tagItems = res.data;
        this.loader = false
      })
    }
  }
}
</script>

<style scoped>

</style>
