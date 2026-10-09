<template>
  <v-dialog v-model="dialog" max-width="920" scrollable>
    <template #activator="{ props }">
      <v-btn v-bind="props" color="primary" prepend-icon="mdi-email-outline" aria-label="Prepare QA report email">
        Email report
      </v-btn>
    </template>

    <v-card>
      <v-card-title>Email QA report</v-card-title>
      <v-card-text>
        <v-alert v-if="errorMessage" type="error" variant="tonal" class="mb-4">{{ errorMessage }}</v-alert>
        <v-alert v-if="resultMessage" type="success" variant="tonal" class="mb-4">{{ resultMessage }}</v-alert>

        <v-autocomplete
          v-model="selectedRecipients"
          :items="recipients"
          item-title="label"
          item-value="id"
          return-object
          multiple
          chips
          closable-chips
          label="Recipients in this space"
          hint="Only active space members are available. Each person receives an individual email."
          persistent-hint
          :loading="loadingRecipients"
          :disabled="loadingRecipients || sending"
        />

        <div class="text-subtitle-2 mt-5 mb-2">Report fields</div>
        <div class="d-flex flex-wrap">
          <v-checkbox
            v-for="field in availableFields"
            :key="field.value"
            :label="field.title"
            :model-value="selectedFields.includes(field.value)"
            density="compact"
            hide-details
            class="mr-4"
            :disabled="sending"
            @update:model-value="toggleField(field.value, $event)"
          />
        </div>

        <div class="text-caption text-medium-emphasis mt-2">
          Period: {{ snapshot?.payload.date_start || filter.date_start }} — {{ snapshot?.payload.date_end || filter.date_end }}
        </div>
        <v-btn class="mt-4" variant="outlined" :loading="previewing" :disabled="!canPreview" @click="createPreview">
          Preview report
        </v-btn>

        <template v-if="snapshot">
          <v-divider class="my-5" />
          <div class="text-subtitle-1 font-weight-medium">Preview</div>
          <div class="text-caption text-medium-emphasis mb-3">
            Snapshot {{ snapshot.snapshot_id }} · expires {{ new Date(snapshot.expires_at).toLocaleString() }}
          </div>
          <v-card v-if="snapshot.payload.summary" variant="tonal" class="pa-3 mb-4">
            <span v-for="(value, key) in snapshot.payload.summary" :key="key" class="mr-4">
              {{ summaryLabels[key] }}: {{ value }}
            </span>
          </v-card>
          <v-expansion-panels>
            <v-expansion-panel title="Created bugs" :text="`${snapshot.payload.created.length} rows`">
              <v-expansion-panel-text>
                <v-table density="compact">
                  <thead><tr><th v-for="field in tableFields" :key="field">{{ fieldLabels[field] }}</th></tr></thead>
                  <tbody>
                    <tr v-for="(row, index) in snapshot.payload.created" :key="index">
                      <td v-for="field in tableFields" :key="field">{{ row[field] ?? '—' }}</td>
                    </tr>
                  </tbody>
                </v-table>
              </v-expansion-panel-text>
            </v-expansion-panel>
            <v-expansion-panel title="Updated bugs" :text="`${snapshot.payload.updated.length} rows`">
              <v-expansion-panel-text>
                <v-table density="compact">
                  <thead><tr><th v-for="field in tableFields" :key="field">{{ fieldLabels[field] }}</th></tr></thead>
                  <tbody>
                    <tr v-for="(row, index) in snapshot.payload.updated" :key="index">
                      <td v-for="field in tableFields" :key="field">{{ row[field] ?? '—' }}</td>
                    </tr>
                  </tbody>
                </v-table>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>

          <v-alert type="info" variant="tonal" class="mt-5">
            <div><strong>Recipients</strong></div>
            <div v-for="recipient in selectedRecipients" :key="recipient.id">{{ recipient.username }} — {{ recipient.email }}</div>
            <div class="mt-2"><strong>Included fields:</strong> {{ selectedFieldLabels.join(', ') }}</div>
          </v-alert>
          <v-checkbox
            v-model="confirmed"
            label="I reviewed this snapshot and confirm sending one individual email to each listed recipient."
            :disabled="sending"
            hide-details
            class="mt-2"
          />
        </template>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" :disabled="sending" @click="dialog = false">Close</v-btn>
        <v-btn color="primary" :disabled="!canSend" :loading="sending" @click="sendReport">Send report</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { qaReportService } from '@/services'

const props = defineProps({
  filter: { type: Object, required: true },
})
const route = useRoute()
const dialog = ref(false)
const recipients = ref([])
const selectedRecipients = ref([])
const selectedFields = ref(['summary', 'short_name', 'title', 'state', 'created_at', 'updated_at'])
const snapshot = ref(null)
const confirmed = ref(false)
const loadingRecipients = ref(false)
const previewing = ref(false)
const sending = ref(false)
const errorMessage = ref('')
const resultMessage = ref('')
const idempotencyKey = ref(null)

const availableFields = [
  { value: 'summary', title: 'Summary' },
  { value: 'short_name', title: 'Bug ID' },
  { value: 'title', title: 'Title' },
  { value: 'state', title: 'State' },
  { value: 'created_at', title: 'Created date' },
  { value: 'updated_at', title: 'Updated date' },
]
const fieldLabels = {
  short_name: 'Bug ID', title: 'Title', state: 'State',
  created_at: 'Created', updated_at: 'Updated',
}
const summaryLabels = {
  opened: 'Created', updated: 'Updated', open: 'Open', reopen: 'Reopened',
  closed: 'Closed', fixed: 'Fixed', hold: 'On hold', ready: 'Ready',
}
const tableFields = computed(() => selectedFields.value.filter(field => field !== 'summary'))
const selectedFieldLabels = computed(() => selectedFields.value.map(field => availableFields.find(item => item.value === field)?.title).filter(Boolean))
const canPreview = computed(() => selectedRecipients.value.length > 0 && selectedFields.value.length > 0 && !previewing.value)
const canSend = computed(() => Boolean(snapshot.value && confirmed.value && selectedRecipients.value.length && !sending.value))

watch(dialog, async open => {
  if (!open) return
  loadingRecipients.value = true
  errorMessage.value = ''
  try {
    const response = await qaReportService.getEmailRecipients(route.params.spaceId)
    const nextRecipients = response.data.map(recipient => ({
      ...recipient,
      label: `${recipient.username || 'Unnamed user'} — ${recipient.email}`,
    }))
    const nextById = new Map(nextRecipients.map(recipient => [recipient.id, recipient]))
    const selectedIds = selectedRecipients.value.map(recipient => recipient.id)
    const emailChanged = selectedRecipients.value.some(recipient => nextById.get(recipient.id)?.email !== recipient.email)
    recipients.value = nextRecipients
    if (emailChanged) {
      selectedRecipients.value = selectedIds.map(id => nextById.get(id)).filter(Boolean)
      errorMessage.value = 'A recipient email changed. Review the refreshed recipient list and create a new preview.'
    }
  } catch {
    errorMessage.value = 'Could not load active space recipients.'
  } finally {
    loadingRecipients.value = false
  }
})

watch([selectedRecipients, selectedFields], () => {
  snapshot.value = null
  confirmed.value = false
  resultMessage.value = ''
  idempotencyKey.value = null
}, { deep: true })

watch(() => [props.filter, route.params.spaceId], () => {
  snapshot.value = null
  confirmed.value = false
  resultMessage.value = ''
  idempotencyKey.value = null
}, { deep: true })

watch(snapshot, () => {
  idempotencyKey.value = null
})

function toggleField(field, checked) {
  selectedFields.value = checked
    ? [...new Set([...selectedFields.value, field])]
    : selectedFields.value.filter(value => value !== field)
}

async function createPreview() {
  errorMessage.value = ''
  resultMessage.value = ''
  previewing.value = true
  snapshot.value = null
  confirmed.value = false
  try {
    const response = await qaReportService.previewEmailReport({
      space_id: route.params.spaceId,
      date_start: props.filter.date_start.slice(0, 10),
      date_end: props.filter.date_end.slice(0, 10),
      create_user: props.filter.create_user,
      fields: selectedFields.value,
    })
    snapshot.value = response.data
  } catch {
    errorMessage.value = 'Could not prepare the report preview.'
  } finally {
    previewing.value = false
  }
}

async function sendReport() {
  if (!canSend.value) return
  if (!idempotencyKey.value) {
    if (!window.crypto?.randomUUID) {
      errorMessage.value = 'This browser cannot create a safe request identifier.'
      return
    }
    idempotencyKey.value = window.crypto.randomUUID()
  }
  errorMessage.value = ''
  resultMessage.value = ''
  sending.value = true
  try {
    const response = await qaReportService.sendEmailReport({
      snapshot_id: snapshot.value.snapshot_id,
      recipient_ids: selectedRecipients.value.map(recipient => recipient.id),
      confirmed_recipients: selectedRecipients.value.map(recipient => ({
        recipient_id: recipient.id,
        email: recipient.email,
      })),
      idempotency_key: idempotencyKey.value,
    })
    const sent = response.data.results.filter(result => result.status === 'sent').length
    const failed = response.data.results.length - sent
    resultMessage.value = failed ? `Sent ${sent}; ${failed} delivery(s) were not sent.` : `Report sent individually to ${sent} recipient(s).`
    confirmed.value = false
  } catch (error) {
    errorMessage.value = error?.response?.status === 409
      ? 'The server rejected this request because it is already in progress or recipient details changed. Retry keeps the same key; close and reopen to refresh recipients, then create a new preview if their details changed.'
      : 'The delivery result is unknown. Retry keeps the same request key; create a new preview to start a separate delivery.'
  } finally {
    sending.value = false
  }
}
</script>
