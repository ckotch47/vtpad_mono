<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>
  <v-card v-if="!loader">
    <v-card-item class="tag-list py-4">
      <div class="d-flex flex-column">
        <tags-new-tag-component :space-id="spaceId" @create-new-tag-emit="getTagForSpace" />
        <tag-item-list-component
          v-for="item in tagItems"
          :key="item.id"
          :tag="item"
          @delete-tag-emit="getTagForSpace"
          @update-tag-emit="getTagForSpace"
        />
      </div>
    </v-card-item>
  </v-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { tagService } from '@/services'
import TagsNewTagComponent from '@/components/tags/list/tagsNewTagComponent.vue'
import TagItemListComponent from '@/components/tags/list/tagItemListComponent.vue'

const route = useRoute()
const spaceId = computed(() => route.params.spaceId)

const loader = ref(true)
const tagItems = ref([])

function getTagForSpace() {
  loader.value = true
  tagService.list(spaceId.value).then(res => {
    tagItems.value = res.data
    loader.value = false
  })
}

onMounted(() => getTagForSpace())
</script>
