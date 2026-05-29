<template>
  <div v-if="loader">
    <v-progress-linear color="primary" indeterminate />
  </div>
  <div v-if="!loader" class="mx-auto my-2">
    <div class="d-flex justify-space-between align-center mb-4">
      <h2>API Tokens</h2>
      <v-btn color="primary" @click="showCreateDialog = true">Create Token</v-btn>
    </div>

    <v-alert v-if="newTokenRaw" type="success" class="mb-4" closable @click:close="newTokenRaw = null">
      <div>Token created successfully. Copy it now — it won't be shown again!</div>
      <code class="d-block mt-2">{{ newTokenRaw }}</code>
    </v-alert>

    <v-card v-if="tokens.length">
      <v-list>
        <v-list-item v-for="token in tokens" :key="token.id">
          <template #prepend>
            <v-icon>mdi-key</v-icon>
          </template>
          <v-list-item-title>{{ token.name }}</v-list-item-title>
          <v-list-item-subtitle>
            Created: {{ formatDate(token.created_at) }}
            <span v-if="token.expires_at">| Expires: {{ formatDate(token.expires_at) }}</span>
            <span v-if="token.last_used_at">| Last used: {{ formatDate(token.last_used_at) }}</span>
          </v-list-item-subtitle>
          <template #append>
            <v-btn icon variant="text" color="red" @click="revokeToken(token.id)">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </v-list>
    </v-card>
    <v-card v-else class="pa-4">
      <p>No API tokens yet.</p>
    </v-card>
  </div>

  <v-dialog v-model="showCreateDialog" max-width="500">
    <v-card>
      <v-card-title>Create API Token</v-card-title>
      <v-card-text>
        <v-form ref="tokenForm" v-model="formValid">
          <v-text-field v-model="createForm.name" label="Name" :rules="[v => !!v || 'Name is required']" required />
          <v-text-field v-model="createForm.expires_at" label="Expires at (ISO date, optional)" placeholder="2026-12-31T23:59:59" />
          <v-textarea v-model="scopesText" label="Scopes (one per line, optional)" rows="3" />
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="closeDialog">Cancel</v-btn>
        <v-btn color="primary" :disabled="!formValid" @click="createToken">Create</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { apiTokenService } from '@/services'

const loader = ref(true)
const tokens = ref([])
const showCreateDialog = ref(false)
const newTokenRaw = ref(null)
const formValid = ref(false)
const createForm = ref({
  name: '',
  expires_at: '',
  scopes: []
})
const tokenForm = ref(null)

const scopesText = computed({
  get() {
    return createForm.value.scopes.join('\n')
  },
  set(val) {
    createForm.value.scopes = val.split('\n').map(s => s.trim()).filter(Boolean)
  }
})

function loadTokens() {
  loader.value = true
  apiTokenService.list().then(res => {
    tokens.value = res.data
    loader.value = false
  }).catch(() => {
    loader.value = false
  })
}

function closeDialog() {
  showCreateDialog.value = false
  createForm.value = { name: '', expires_at: '', scopes: [] }
  formValid.value = false
  nextTick(() => tokenForm.value?.resetValidation())
}

function createToken() {
  const payload = {
    name: createForm.value.name,
    scopes: createForm.value.scopes.length ? createForm.value.scopes : null,
    expires_at: createForm.value.expires_at || null
  }
  apiTokenService.create(payload).then(res => {
    newTokenRaw.value = res.data.raw_token
    closeDialog()
    loadTokens()
  })
}

function revokeToken(id) {
  if (!confirm('Revoke this API token?')) return
  apiTokenService.revoke(id).then(() => {
    loadTokens()
  })
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString()
}

onMounted(loadTokens)
</script>
