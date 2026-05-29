<template>
  <div class="mt-4">
    <div class="d-flex align-center mb-2">
      <span class="text-subtitle-1">Attachments</span>
      <v-spacer />
      <v-btn size="small" variant="text" prepend-icon="mdi-paperclip" @click="fileInput.click()">
        Attach File
      </v-btn>
      <input
        ref="fileInput"
        type="file"
        class="d-none"
        @change="uploadFile"
      />
    </div>

    <v-list v-if="attachments.length" density="compact">
      <v-list-item v-for="att in attachments" :key="att.id">
        <template #prepend>
          <v-icon>mdi-file</v-icon>
        </template>
        <v-list-item-title>
          <a :href="att.file?.filepath" target="_blank">{{ att.file?.filepath?.split('/').pop() || 'File' }}</a>
        </v-list-item-title>
        <template #append>
          <v-btn icon size="x-small" variant="text" color="error" @click="deleteAttachment(att.id)">
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-list-item>
    </v-list>
    <p v-else class="text-body-2 text-medium-emphasis">No attachments</p>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { attachmentService, fileService } from '@/services'

const props = defineProps({
  entityType: { type: String, required: true },
  entityId: { type: String, required: true }
})

const attachments = ref([])
const fileInput = ref(null)

function loadAttachments() {
  attachmentService.listByEntity(props.entityType, props.entityId).then(res => {
    attachments.value = res.data || []
  }).catch(() => {
    attachments.value = []
  })
}

function uploadFile(event) {
  const file = event.target.files[0]
  if (!file) return
  const form = new FormData()
  form.append('file', file)
  fileService.upload(form).then(res => {
    const fileData = res.data
    const fileId = fileData.id || fileData.file_id || fileData
    return attachmentService.create({
      entity_type: props.entityType,
      entity_id: props.entityId,
      file_id: fileId
    })
  }).then(() => {
    loadAttachments()
    event.target.value = ''
  }).catch(() => {
    event.target.value = ''
  })
}

function deleteAttachment(id) {
  if (!confirm('Delete attachment?')) return
  attachmentService.delete(id).then(() => {
    loadAttachments()
  })
}

watch(() => props.entityId, loadAttachments)
onMounted(loadAttachments)
</script>
