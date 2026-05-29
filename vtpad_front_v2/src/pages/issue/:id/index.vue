<template>
  <div>
    <v-container v-if="issue" fluid>
      <breadcrumbs-component :items="breadcrumbItems" />
      <v-row align="center">
        <v-col>
          <h1 class="text-h4 font-weight-bold">{{ issue.title }}</h1>
          <p class="text-body-1 text-medium-emphasis mt-1">
            {{ issue.description || 'No description' }}
          </p>
        </v-col>
        <v-col cols="auto">
          <v-chip :color="issue.state === 'open' ? 'success' : 'grey'">{{ issue.state }}</v-chip>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { bugService } from '@/services'
import BreadcrumbsComponent from '@/components/common/breadcrumbsComponent.vue'

const route = useRoute()
const issueId = route.params.id

const issue = ref(null)
const breadcrumbItems = ref([])

function loadIssue() {
  bugService.getById(issueId).then(res => {
    issue.value = res.data
    breadcrumbItems.value = [
      { title: 'Issues', to: '/issues' },
      { title: `#${issue.value.id}` }
    ]
  })
}

onMounted(() => {
  loadIssue()
})
</script>
