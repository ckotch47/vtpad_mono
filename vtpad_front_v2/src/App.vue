<template>
  <v-app v-if="routerReady">
    <template v-if="!isPublicRoute">
      <v-app-bar
        v-if="authToken"
        class="spaces-navigation-shell"
        flat
        height="56"
      >
        <v-btn
          v-if="mdAndUp || !drawer"
          id="spaces-navigation-toggle"
          class="spaces-navigation-toggle menu-show--main ms-2"
          :icon="drawer ? 'mdi-menu-open' : 'mdi-menu'"
          :aria-label="drawer ? 'Close spaces navigation' : 'Open spaces navigation'"
          aria-controls="spaces-navigation"
          :aria-expanded="String(Boolean(drawer))"
          :title="drawer ? 'Close spaces navigation' : 'Open spaces navigation'"
          @click="drawer = mdAndUp ? !drawer : true"
        />
        <v-tabs
          v-if="mdAndUp && spaces.length"
          class="spaces-navigation-tabs"
          :model-value="activeSpaceId"
          show-arrows
          align-tabs="start"
          density="compact"
        >
          <v-tab
            v-for="space in spaces"
            :key="space.id"
            :to="`/space/${space.id}/dashboard`"
            :value="String(space.id)"
            :aria-label="spaceName(space)"
          >
            {{ spaceName(space) }}
          </v-tab>
        </v-tabs>
        <v-spacer />
        <profile-left-component v-if="mdAndUp" compact class="spaces-navigation-profile" />
      </v-app-bar>

      <v-navigation-drawer
        id="spaces-navigation"
        v-if="authToken"
        v-model="drawer"
        width="300"
      >
        <profile-left-component
          v-if="!mdAndUp"
          class="spaces-navigation-mobile-profile"
          @hide-left-menu="drawer = !drawer"
        />
        <spaces-list-component />
      </v-navigation-drawer>

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
    </template>

    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDisplay } from 'vuetify'
import ProfileLeftComponent from '@/components/leftAsideMain/ProfileLeftComponent.vue'
import SpacesListComponent from '@/components/leftAsideMain/SpacesListComponent.vue'
import CommandPaletteComponent from '@/components/common/commandPaletteComponent.vue'
import { spaceService } from '@/services'
import 'vue3-toastify/dist/index.css'

const route = useRoute()
const router = useRouter()
const { mdAndUp } = useDisplay()
const isPublicRoute = computed(() => route.meta?.isPublic === true)

const routerReady = ref(false)
const drawer = ref(null)
const spaceId = ref(null)
const routerMeta = ref({})
const authToken = ref(undefined)
const showShortcuts = ref(false)
const commandPalette = ref(null)
const spaces = ref([])
const spacesLoaded = ref(false)
const spacesLoading = ref(false)
const activeSpaceId = computed(() => {
  const routeSpaceId = route.params.spaceId ?? route.params.id
  return spaces.value.some(space => String(space.id) === String(routeSpaceId)) ? String(routeSpaceId) : ''
})

function loadSpaces() {
  if (!authToken.value) {
    spaces.value = []
    spacesLoaded.value = false
    return
  }
  if (spacesLoaded.value || spacesLoading.value) return
  spacesLoading.value = true
  const requestToken = authToken.value
  spaceService.list().then(res => {
    if (authToken.value === requestToken && !isPublicRoute.value) {
      spaces.value = Array.isArray(res.data) ? res.data : []
    }
  }).catch(() => {
    if (authToken.value === requestToken && !isPublicRoute.value) spaces.value = []
  }).finally(() => {
    if (authToken.value === requestToken && !isPublicRoute.value) spacesLoaded.value = true
    spacesLoading.value = false
  })
}

function spaceName(space) {
  const name = typeof space?.name === 'string' ? space.name.trim() : ''
  return !name || ['null', 'undefined'].includes(name.toLocaleLowerCase()) ? 'Unnamed space' : name
}

function checkAuth() {
  if (isPublicRoute.value) {
    authToken.value = null
    return
  }
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

onMounted(async () => {
  // Do not mount route-aware shell components until initial metadata is known.
  await router.isReady()
  routerReady.value = true
  checkAuth()
  loadSpaces()
  updateRouteMeta()
  if (!isPublicRoute.value) document.addEventListener('keydown', onKeydown, true)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown, true)
})

watch(route, () => {
  updateRouteMeta()
  if (isPublicRoute.value) {
    authToken.value = null
    spaces.value = []
    spacesLoaded.value = false
    showShortcuts.value = false
    document.removeEventListener('keydown', onKeydown, true)
  } else {
    checkAuth()
    loadSpaces()
    document.addEventListener('keydown', onKeydown, true)
  }
}, { deep: true })
</script>

<style lang="scss">
.spaces-navigation-shell {
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  padding-inline: 12px;
}

.spaces-navigation-tabs {
  min-width: 0;
  max-width: calc(100vw - 220px);
  flex: 1 1 auto;
}

.spaces-navigation-profile {
  flex: 0 0 auto;
  margin-left: 8px;
}

.spaces-navigation-toggle {
  min-width: 48px;
  min-height: 48px;
}

@media (min-width: 960px) {
  .spaces-navigation-toggle {
    min-width: 44px;
    min-height: 44px;
  }

  .menu-show--main {
    left: -24px;
  }
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
