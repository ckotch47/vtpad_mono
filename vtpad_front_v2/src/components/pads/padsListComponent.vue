<template>
  <div v-if="loader">
    <v-progress-linear
      color="primary"
      indeterminate
    ></v-progress-linear>
  </div>

  <v-list v-if="!loader">
    <pads-list-create-folder-component :space-id="spaceId" @createFolderEmit="createFolder"/>

    <v-divider :thickness="2"></v-divider>


    <v-list-group
      v-for="item in folders"
      :key="item.id"
      :value="item.id"
    >
      <template v-slot:activator="{ props }">
        <pads-list-folder-component
          v-if="item.id"
          :props="props"
          :title="item.name"
          :id="item.id"
          :space-id="spaceId"
          @open-folder-modal="openFolderModal(item)"
          @openFolderEmit="openFolder"
          />
      </template>


      <div v-if="!item.pads" >
        <v-progress-linear
          color="primary"
          indeterminate
        ></v-progress-linear>
      </div>

      <div v-if="item.pads">
        <pads-list-item-component
          v-for="elem in item.pads"
          :key="elem.id"
          :value="elem.id"
          :name="elem.name"
          :id="elem.id"
          :folder-id="item.id"
          @open-item-modal="openItemModalFolder(item.id, elem.id)"
        />
      </div>
      <pads-list-create-item-component
        :space-id="spaceId"
        :folder-id="item.id"
        @createPadEmit="createPad"
      />
    </v-list-group>


    <pads-list-item-component
      v-for="item in pads"
      :key="item.id"
      :value="item.id"
      :name="item.name"
      :id="item.id"
      @open-item-modal="openItemModal"
    />


    <pads-list-create-item-component
      :space-id="spaceId"
      @createPadEmit="createPad"
    />
  </v-list>
  <pads-list-modal-item-component
    v-if="openItem_modal && openItem_item"
    :is-active="openItem_modal"
    :pad="openItem_item"
    :folder="folders"
    @close-item-modal="closeItemModal"
    @saveItemModalEmit="saveItemPad"
    @deleteItemModalEmit="deleteItemPad"
  />

  <pads-list-modal-folder-component
    v-if="openFolder_modal && openFolder_item"
    :is-active="openFolder_modal"
    :folder="openFolder_item"
    @close-folder-modal="closeFolderModal"
    @updateFolderEmit="updateFolder"
    @deleteFolderEmit="deleteFolder"
  />
</template>

<script>
import PadsListItemComponent from "@/components/pads/list/padsListItemComponent.vue";
import PadsListFolderComponent from "@/components/pads/list/padsListFolderComponent.vue";
import PadsListCreateItemComponent from "@/components/pads/list/padsListCreateItemComponent.vue";
import PadsListCreateFolderComponent from "@/components/pads/list/padsListCreateFolderComponent.vue";
import PadsListModalItemComponent from "@/components/pads/list/modal/padsListModalItemComponent.vue";
import PadsListModalFolderComponent from "@/components/pads/list/modal/padsListModalFolderComponent.vue";
import axios from "axios";

export default {
  name: "padsListComponent",
  components: {
    PadsListModalFolderComponent,
    PadsListModalItemComponent,
    PadsListCreateFolderComponent,
    PadsListCreateItemComponent, PadsListFolderComponent, PadsListItemComponent},
  data: () => ({
    folders: [],
    pads: [],
    openItem_modal: false,
    openItem_item: undefined,
    openFolder_modal: false,
    openFolder_item: undefined,
    spaceId: undefined,
    loader: true,

  }),
  mounted() {
    this.spaceId = this.$route.params.spaceId;
    this.getFolders();
    this.getPads();
  },
  updated() {
    this.spaceId = this.$route.params.spaceId
  },
  methods:{
    getFolders(){
      this.folders = []
      axios.get(`/api/v1/pad-folder/${this.spaceId}`).then(res=>{
        this.folders = res.data
      })
    },
    createFolder(folderItem){
      this.folders.push(folderItem)
    },
    deleteFolder(folderItem){
      this.closeFolderModal()
      const tmp = this.folders.findIndex(value => value.id === folderItem.id)
      this.folders.splice(tmp, tmp+1)
    },
    getPads(){
      axios.get(`/api/v1/pad/${this.spaceId}`).then(res => {
        this.pads  = res.data
        this.loader = false
      })
    },
    createPad(padItem){
      if(!padItem.folder_id)
        this.pads.push(padItem)
      else
        this.folders.find(value => value.id === padItem.folder_id).pads.push(padItem)
    },
    saveItemPad(oldFolderId, newFolderId){
      if(oldFolderId !== newFolderId){
        if(oldFolderId) this.getFolderDetailList(oldFolderId)
        if(newFolderId && newFolderId != 'none') this.getFolderDetailList(newFolderId)
        else this.getPads()
      }
      if(!oldFolderId) this.getPads()

      this.getFolderDetailList(oldFolderId)
      this.closeItemModal()
    },
    deleteItemPad(padId, folderId){
      if(folderId){
        const tmp = this.folders.find(value => value.id === folderId).pads.findIndex(value => value.id === padId)
        this.folders.find(value => value.id === folderId).pads.splice(tmp, 1)
      }else{
        const tmp = this.pads.findIndex(value => value.id === padId)
        this.pads.splice(tmp, 1)
      }
      this.closeItemModal()
    },
    getFolderDetailList(folderId){
      axios.get(`/api/v1/pad/${this.spaceId}?folderId=${folderId}`).then(res => {
        this.folders.find(value => value.id === folderId).pads = res.data;
      })
    },
    openFolder(folderId){
      if(this.folders.find(value => value.id === folderId).pads)
        return
      axios.get(`/api/v1/pad/${this.spaceId}?folderId=${folderId}`).then(res => {
        this.folders.find(value => value.id === folderId).pads = res.data
      })
    },
    openItemModalFolder(folderId, padId){

      this.openItem_modal = !this.openItem_modal;
      const folder = this.folders.find(value => value.id === folderId)
      this.openItem_item = folder.pads.find(value => value.id  === padId)
    },
    openItemModal(padId){
      this.openItem_modal = !this.openItem_modal;
      this.openItem_item = this.pads.find(value => value.id  === padId)
    },
    closeItemModal(){
      this.openItem_modal = false;
      this.openItem_item = undefined;
    },
    openFolderModal(folderItem){
      this.openFolder(folderItem.id)
      this.openFolder_item = folderItem
      this.openFolder_modal = !this.openFolder_modal;
    },
    closeFolderModal(){
      this.openFolder_item = undefined
      this.openFolder_modal = false
    },
    updateFolder(folderItem){
      let tmp = this.folders.findIndex(value => value.id === folderItem.id)
      this.folders[tmp] = folderItem
      this.closeFolderModal()
    }
  }
}
</script>

<style lang="scss">
.no-white-space{
  white-space: nowrap;
    div{
      display: none !important;
    }
}
div.is-empty:first-child::before {
  color: rgba(var(--v-theme-secondary-darken-1));
  content: attr(data-placeholder);
}
.w-97{
  width: 97%;
}

.list-item--icon{
  opacity: var(--v-medium-emphasis-opacity);
}
</style>
