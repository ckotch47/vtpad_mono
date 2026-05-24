<template>
  <div v-if="loader">
    <v-progress-linear
      color="primary"
      indeterminate
    ></v-progress-linear>
  </div>
  <div class="mx-auto my-2" v-if="!loader">
    <h2>Settings</h2>
    <v-text-field
      label="Space name"
      v-model="space.name"
      :append-inner-icon="'mdi-content-save'"
      @click:append-inner="saveName"
      clearable
    />
    <v-text-field
      label="Short name"
      v-model="space.short_name"
      :append-inner-icon="'mdi-content-save'"
      @click:append-inner="saveName"
      clearable
    />

  </div>
  <div class="mx-auto my-2" v-if="!loader">
    <h2>Delete</h2>
    <p>Enter DELETE for delete space</p>
    <v-text-field
      label="Delete"
      v-model="deleteSpace"
      :append-inner-icon="'mdi-delete-forever'"
      @click:append-inner="delSpace"
      clearable
    />
  </div>
</template>

<script>
import { spaceService } from '@/services'

export default {
  name: "settingsMainComponent",
  watch:{
    $route: {
      handler() {
        this.spaceId= this.$route.params.spaceId;
        this.getSpaceSetting()
      },
      deep: false
    },
  },
  data(){
    return {
      loader: true,
      spaceId: this.$route.params.spaceId,
      deleteSpace: null,
      space: {
        "short_name": null,
        "sort": 2000,
        "name": "",
        "id": ""
      }
    }
  },
  mounted() {
    this.getSpaceSetting()
  },
  updated() {

  },
  methods:{
    getSpaceSetting(){
      spaceService.getById(this.spaceId).then(res => {
        this.space = res.data
        this.loader = false;
      })
    },
    saveName(){
      spaceService.update(this.spaceId,{
        name: this.space.name,
        short_name: this.space.short_name
      }).then(res => {
        if(res.status === 200) this.getSpaceSetting()
      })
    },
    delSpace(){
      if(this.deleteSpace !== 'DELETE'){
        this.deleteSpace = null
        return false
      }else{
        spaceService.delete(this.spaceId).then(()=>{
          location.href = '/space'
        })
      }
    },
  }
}
</script>

<style >
input{
  border: none;
  background: none;
}
</style>
