<template>
  <v-dialog :model-value="modelValue" max-width="620" @update:model-value="onDialogUpdate">
    <v-card>
      <v-card-title class="text-h6">Share run</v-card-title>
      <v-card-text>
        <div v-if="statusLoading" class="d-flex align-center ga-3 py-4" role="status">
          <v-progress-circular indeterminate size="22" />
          <span>Checking share link…</span>
        </div>

        <v-alert v-else-if="statusError" type="error" variant="tonal" role="alert">
          Share link status could not be loaded.
          <v-btn variant="text" size="small" @click="loadStatus">Retry</v-btn>
        </v-alert>

        <template v-else>
          <v-alert type="info" variant="tonal" class="mb-4">
            Anyone with this link can view the run name, status, group names, case counts, result counts, and known durations for 7 days. Case content, comments, bugs, attachments, and user names are not shared.
          </v-alert>

          <template v-if="oneTimeLink">
            <p class="text-body-2 mb-2">Copy this link now. The secret is shown once and cannot be recovered after you close this dialog.</p>
            <div class="d-flex align-start ga-2">
              <v-textarea
                :model-value="oneTimeLink"
                label="One-time share link"
                rows="2"
                auto-grow
                readonly
                hide-details
                aria-label="One-time share link"
              />
              <v-btn
                class="mt-1"
                color="primary"
                variant="tonal"
                prepend-icon="mdi-content-copy"
                :aria-label="copied ? 'Share link copied' : 'Copy share link'"
                @click="copyLink"
              >{{ copied ? 'Copied' : 'Copy' }}</v-btn>
            </div>
            <v-alert v-if="actionError" type="warning" variant="tonal" density="compact" role="alert" class="mt-3">
              {{ actionError }}
            </v-alert>
          </template>

          <template v-else-if="linkStatus?.active">
            <v-list density="compact" class="pa-0">
              <v-list-item prepend-icon="mdi-link-variant">
                <v-list-item-title>Active share link</v-list-item-title>
                <v-list-item-subtitle>Created {{ formatDate(linkStatus.created_at) }} · Expires {{ formatDate(linkStatus.expires_at) }}</v-list-item-subtitle>
                <template #append>
                  <v-chip color="success" size="small">Active</v-chip>
                </template>
              </v-list-item>
            </v-list>
            <p class="text-body-2 text-medium-emphasis mt-3">The secret cannot be viewed again. Revoke this link if it should no longer work.</p>
          </template>

          <template v-else>
            <v-checkbox
              v-model="confirmed"
              density="compact"
              hide-details
              label="I understand that anyone with the link can view the limited run summary until it expires or I revoke it."
              class="mb-2"
            />
            <v-alert v-if="actionError" type="error" variant="tonal" density="compact" role="alert" class="mt-3">
              {{ actionError }}
            </v-alert>
          </template>
        </template>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="close">Close</v-btn>
        <v-btn
          v-if="!statusLoading && !statusError && linkStatus?.active && !oneTimeLink"
          color="error"
          variant="outlined"
          :loading="actionLoading"
          @click="revokeLink"
        >Revoke link</v-btn>
        <v-btn
          v-else-if="!statusLoading && !statusError && !linkStatus?.active && !oneTimeLink"
          color="primary"
          :disabled="!confirmed"
          :loading="actionLoading"
          @click="createLink"
        >Create share link</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { publicRunService } from '@/services/publicRunService'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  runId: { type: [String, Number], required: true }
})
const emit = defineEmits(['update:modelValue'])

const linkStatus = ref(null)
const statusLoading = ref(false)
const statusError = ref(false)
const actionLoading = ref(false)
const actionError = ref('')
const confirmed = ref(false)
const oneTimeLink = ref('')
const copied = ref(false)
let statusRequestVersion = 0

watch(() => [props.modelValue, props.runId], ([isOpen]) => {
  if (isOpen) loadStatus()
  else clearOneTimeSecret()
})

async function loadStatus() {
  if (!props.modelValue) return
  const requestVersion = ++statusRequestVersion
  statusLoading.value = true
  statusError.value = false
  actionError.value = ''
  try {
    const response = await publicRunService.getLinkStatus(props.runId)
    if (requestVersion !== statusRequestVersion) return
    linkStatus.value = response.data
  } catch {
    if (requestVersion !== statusRequestVersion) return
    statusError.value = true
    linkStatus.value = null
  } finally {
    if (requestVersion === statusRequestVersion) statusLoading.value = false
  }
}

async function createLink() {
  if (!confirmed.value || actionLoading.value) return
  actionLoading.value = true
  actionError.value = ''
  try {
    const response = await publicRunService.createLink(props.runId)
    const token = response.data?.token
    if (typeof token !== 'string' || !token) throw new Error('invalid response')
    oneTimeLink.value = `${window.location.origin}/shared-run#${encodeURIComponent(token)}`
    linkStatus.value = {
      active: true,
      created_at: new Date().toISOString(),
      expires_at: response.data.expires_at
    }
    confirmed.value = false
    copied.value = false
  } catch {
    actionError.value = 'The share link could not be created. Check your access and try again.'
  } finally {
    actionLoading.value = false
  }
}

async function revokeLink() {
  if (actionLoading.value) return
  actionLoading.value = true
  actionError.value = ''
  try {
    await publicRunService.revokeLink(props.runId)
    linkStatus.value = { ...linkStatus.value, active: false }
    clearOneTimeSecret()
  } catch {
    actionError.value = 'The share link could not be revoked. Check your access and try again.'
  } finally {
    actionLoading.value = false
  }
}

async function copyLink() {
  try {
    await navigator.clipboard.writeText(oneTimeLink.value)
    copied.value = true
  } catch {
    actionError.value = 'Clipboard access was unavailable. Select and copy the link manually.'
  }
}

function clearOneTimeSecret() {
  oneTimeLink.value = ''
  copied.value = false
}

function formatDate(value) {
  if (!value) return '—'
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? '—' : parsed.toLocaleString()
}

function onDialogUpdate(open) {
  if (!open) close()
}

function close() {
  clearOneTimeSecret()
  confirmed.value = false
  emit('update:modelValue', false)
}
</script>
