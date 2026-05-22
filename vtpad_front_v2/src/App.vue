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
  </v-app>
</template>


<script setup>
import { ref } from 'vue'
import ProfileLeftComponent from "@/components/leftAsideMain/ProfileLeftComponent.vue";
import SpacesListComponent from "@/components/leftAsideMain/SpacesListComponent.vue";
import 'vue3-toastify/dist/index.css';

const drawer = ref(null)
</script>

<script>
import axios from "axios";


axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL;

axios.defaults.headers = {
  Accept: "application/json",
  "Content-Type": "application/json",
  responseType: "json",
}
axios.interceptors.request.use((config) => {
  const tokens = localStorage.getItem('auth_token');

  if (!tokens) {
    return config;
  }
  config.headers.Authorization = `Bearer ${tokens}`;
  return config;
});

axios.interceptors.response.use(function (response) {
  if(response.config.method === 'put' ||
    response.config.method === 'post' ||
    response.config.method === 'patch' ||
    response.config.method === 'delete'  &&
    response.status === 200 ||
    response.status === 201){
    toast.success('Success', {
      theme: vuetify.theme.name.value,
      transition: "flip",
      autoClose: 200
    })
  }

  return response
}, function (error) {
  if(error.response.status === 401 && location.pathname !== '/auth'){
    const refreshToken = localStorage.getItem('refresh_token')
    if(!refreshToken)
      location.href = '/auth'
    axios.post('/api/v1/auth/refresh', {
      refresh_token: refreshToken
    }).then((res)=>{
      if(!res) location.href = '/auth'
      if(res.status === 200) {
        localStorage.setItem('auth_token', res.data.access_token)
        localStorage.setItem('refresh_token', res.data.refresh_token)
        // eslint-disable-next-line no-self-assign
        // location.href = location.href
      }
    }).catch(()=>{
      localStorage.removeItem('auth_token')
      localStorage.removeItem('refresh_token')
      location.href = '/auth'
    })
  }
    toast.error(`${error.response.status} ${error.response.data}`, {
      theme: vuetify.theme.name.value,
      transition: "flip",
      autoClose: 200
    })
})
import {useRouter} from "vue-router";
import {toast} from "vue3-toastify";
import vuetify from "@/plugins/vuetify";


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
