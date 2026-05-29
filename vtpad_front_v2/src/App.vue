<template>
  <v-app>
    <v-fab
      v-if="authToken"
      class="me-4 menu-show--main"
      icon="mdi-arrow-collapse-right"
      absolute
      offset
      @click="drawer = !drawer"
    />

    <v-navigation-drawer v-if="authToken" v-model="drawer" width="300">
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
    const activeOverlays = document.querySelectorAll('.v-overlay__scrim')
    if (activeOverlays.length > 0) {
      activeOverlays[activeOverlays.length - 1].click()
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
  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
})

watch(route, updateRouteMeta, { deep: true })
</script>

<style lang="scss">
.menu-show--main {
  z-index: 99;

  &.v-fab--absolute {
    position: fixed;
    top: 200px;
    left: 30px;
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
*:focus-visible {
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
