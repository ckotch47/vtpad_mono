<template>
  <v-app>
    <v-fab
      v-if="authToken && !drawer"
      id="spaces-navigation-toggle"
      class="me-4 menu-show--main"
      icon="mdi-menu"
      aria-label="Open spaces navigation"
      aria-controls="spaces-navigation"
      title="Open spaces navigation"
      @click="drawer = !drawer"
    />

    <v-navigation-drawer
      id="spaces-navigation"
      v-if="authToken"
      v-model="drawer"
      width="300"
    >
      <profile-left-component @hide-left-menu="drawer = !drawer" />
      <spaces-list-component />
    </v-navigation-drawer>

    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>

    <command-palette-component ref="commandPalette" />

    <!-- Keyboard shortcuts help -->
    <v-dialog v-model="showShortcuts" max-width="400">
      <v-card>
        <v-card-title>Keyboard Shortcuts</v-card-title>
        <v-divider />
        <v-card-text>
          <v-list density="compact">
            <v-list-item title="Esc" subtitle="Close overlay / dialog" />
            <v-list-item title="?" subtitle="Show this help" />
            <v-list-item title="Cmd / Ctrl + K" subtitle="Open command palette" />
            <v-list-item title="Cmd / Ctrl + S" subtitle="Save the active form" />
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showShortcuts = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-app>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ProfileLeftComponent from '@/components/leftAsideMain/ProfileLeftComponent.vue'
import SpacesListComponent from '@/components/leftAsideMain/SpacesListComponent.vue'
import CommandPaletteComponent from '@/components/common/commandPaletteComponent.vue'
import 'vue3-toastify/dist/index.css'

const route = useRoute()
const router = useRouter()

const drawer = ref(null)
const spaceId = ref(null)
const routerMeta = ref({})
const authToken = ref(undefined)
const showShortcuts = ref(false)
const commandPalette = ref(null)

function checkAuth() {
  authToken.value = localStorage.getItem('auth_token')
  if (!authToken.value && location.pathname !== '/auth' && location.pathname !== '/404') {
    location.href = '/auth'
  }
}

function updateRouteMeta() {
  routerMeta.value = router.currentRoute.value
  if (route.params?.id) {
    spaceId.value = route.params.id
  }
}

function onKeydown(e) {
  if (e.key === 'Escape') {
    const overlays = document.querySelectorAll('.v-overlay--active')
    const topOverlay = overlays[overlays.length - 1]
    if (topOverlay) {
      const savingForm = topOverlay.querySelector('[data-keyboard-escape-saving="true"]')
      if (savingForm) {
        e.preventDefault()
        e.stopImmediatePropagation()
        return
      }

      const guardedForm = topOverlay.querySelector('[data-keyboard-escape-confirm]')
      if (guardedForm && !window.confirm(guardedForm.dataset.keyboardEscapeConfirm)) {
        e.preventDefault()
        e.stopImmediatePropagation()
        return
      }
    }
  }
  if ((e.metaKey || e.ctrlKey) && !e.altKey && e.key.toLowerCase() === 's') {
    const activeElement = document.activeElement
    const scope = activeElement?.closest('[data-keyboard-save-scope]')
    const saveAction = scope?.querySelector('[data-keyboard-save-action]')
    if (saveAction) {
      e.preventDefault()
      if (!saveAction.disabled && saveAction.getAttribute('aria-disabled') !== 'true') {
        saveAction.click()
      }
    }
  }
  if (e.key === '?' && !e.ctrlKey && !e.metaKey && !e.altKey) {
    const tag = document.activeElement?.tagName
    if (tag !== 'INPUT' && tag !== 'TEXTAREA') {
      showShortcuts.value = !showShortcuts.value
    }
  }
}

onMounted(() => {
  checkAuth()
  updateRouteMeta()
  document.addEventListener('keydown', onKeydown, true)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown, true)
})

watch(route, updateRouteMeta, { deep: true })
</script>

<style lang="scss">
.menu-show--main {
  position: fixed !important;
  top: 200px;
  left: 12px;
  z-index: 1200 !important;
}

body::-webkit-scrollbar,
*::-webkit-scrollbar {
  width: .3em;
  height: .3em;
  cursor: default !important;
}

*::-webkit-scrollbar-track {
  cursor: default !important;
}

body::-webkit-scrollbar-thumb,
*::-webkit-scrollbar-thumb {
  background-color: rgb(var(--v-theme-primary)) !important;
  cursor: default !important;
}

input:not(.v-field__input):not(.v-text-field__input) {
  border: none;
}

.custom-container {
  margin: 0;
  max-width: unset;
}

.max-width-1500 {
  max-width: 1500px !important;
}

.router--link {
  color: unset;
  background-color: unset;
  text-decoration: unset;
}

select:not(.v-field__input),
input:not(.v-field__input):not(.v-text-field__input) {
  background: none;
}

.color-state {
  &--READY {
    color: rgb(var(--v-theme-warning));
  }

  &--OPEN {
    color: rgb(var(--v-theme-success));
  }

  &--CLOSED {
    color: rgb(var(--v-theme-info));
  }

  &--REOPEN {
    color: rgb(var(--v-theme-error));
  }

  &--FIXED {
    color: rgb(var(--v-theme-warning));
  }
}

.w-90 {
  width: 90% !important;
}

.fab_btn {
  z-index: 9;
}

@media (width <= 720px) {
  .v-container {
    padding: 4px !important;
  }
}

/* Keyboard focus indicators */
*:focus-visible:not(input):not(textarea):not(select) {
  outline: 2px solid rgb(var(--v-theme-primary));
  outline-offset: 2px;
}

.rounded-0_custom {
  .rounded-xl {
    border-radius: 2px !important;
  }
}

.no-padding-important {
  .v-expansion-panel-text__wrapper {
    padding: 0 !important;
  }
}
</style>
