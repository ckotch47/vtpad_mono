<template>
  <v-app>
    <v-fab
      class="me-4 menu-show--main"
      icon="mdi-arrow-collapse-right"

      absolute
      offset
      @click="drawer = !drawer"
      v-if="auth_token"

    ></v-fab>

    <v-navigation-drawer v-model="drawer" width="300" v-if="auth_token">
      <profile-left-component @hide-left-menu="drawer = !drawer"/>
      <spaces-list-component />
    </v-navigation-drawer>

    <v-main>
      <v-container fluid>
        <router-view></router-view>
      </v-container>
    </v-main>

    <command-palette-component ref="commandPalette" />
  </v-app>
</template>


<script setup>
import { ref } from 'vue'
import ProfileLeftComponent from "@/components/leftAsideMain/ProfileLeftComponent.vue";
import SpacesListComponent from "@/components/leftAsideMain/SpacesListComponent.vue";
import CommandPaletteComponent from "@/components/common/commandPaletteComponent.vue";
import 'vue3-toastify/dist/index.css';

const drawer = ref(null)
</script>

<script>
import {useRouter} from "vue-router";


export default {
  data: () => ({
    drawer: null,
    spaceId: null,
    routerMeta: {},
    auth_token: undefined,
  }),
  mounted() {
    this.auth_token = localStorage.getItem('auth_token')
    if(!this.auth_token && location.pathname !== '/auth' && location.pathname !== '/404') location.href = '/auth'
    this.routerMeta = useRouter().currentRoute.value;
    if(this.$route?.params.id)
      this.spaceId = this.$route?.params.id

    // Global Esc handler — close topmost overlay (dialog, menu, etc.)
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        const activeOverlays = document.querySelectorAll('.v-overlay__scrim');
        if (activeOverlays.length > 0) {
          activeOverlays[activeOverlays.length - 1].click();
        }
      }
    });
  },
  updated() {
    this.routerMeta = useRouter().currentRoute.value;
    if(this.$route?.params.id)
      this.spaceId = this.$route?.params.id
  },
  methods:{
    hideMenu(){
      this.drawer = !this.drawer
    }
  }
}
</script>
<style lang="scss">

.menu-show--main{
  z-index: 99;
  //.v-fab__container{
  //  //left: -30px;
  //  //top: 300px;
  //  top: 0;
  //  left: 0;
  //}

  &.v-fab--absolute{
    position: fixed;
    top: 200px;
    left: 30px;
  }
}

body::-webkit-scrollbar, *::-webkit-scrollbar, *::-webkit-scrollbar  {
  width: .3em;
  height: .3em;
  cursor: default !important;
}

*::-webkit-scrollbar-track {
  cursor: default !important;
}

body::-webkit-scrollbar-thumb, *::-webkit-scrollbar-thumb {
  background-color: rgb(var(--v-theme-primary))  !important;
  cursor: default !important;
}
input{
  border: none !important;
}
.custom-container{
  margin: 0;
  max-width: unset;
}
.max-width-1500{
  max-width: 1500px !important;
}
.router--link{
  color: unset;
  background-color: unset;
  text-decoration: unset;
}
select, input{
  background: none !important;
}
.v-application__wrap{
  //min-height: 90vh;
}
.color-state{
  &--READY{
    color: #e6bb00;
  }
  &--OPEN{
    color: #07d401;
  }
  &--CLOSED{
    color: #15d1d1;
  }
  &--REOPEN{
    color: #e6003a;
  }
  &--FIXED{
    color: #ffea5f;
  }
}
.w-90{
  width: 90% !important;
}
.fab_btn{
  z-index: 9;
}
@media (width <= 720px) {
  .v-container{
    padding: 4px !important;
  }
}
.rounded-0_custom{
  .rounded-xl{
    border-radius: 2px !important;
  }
}
.no-padding-important{
  .v-expansion-panel-text__wrapper{
    padding: 0 !important;
  }
}
</style>
