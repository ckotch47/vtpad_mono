// Utilities
import { defineStore } from 'pinia'
import { spaceService } from '@/services'

export const useAppStore = defineStore('app', {

  state: () => ({
    openBug: undefined,
    openSpaceId: undefined,
    shortName: undefined,
    openItem: undefined,
    openRunItem: undefined
  }),
  set(name, value){
    this[name] = value
  },
  getters: {
    getOpenItem(){
      return this.openItem;
    },
    getOpenRunItem(){
      return this.openRunItem;
    },
    async getSpaceId() {
      if (this.openSpaceId) {
        return this.openSpaceId
      } else {
        if(!this.shortName) return;

        if (this.shortName.match(/^[0-9A-F]{8}-[0-9A-F]{4}-[4][0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i)) {
          this.openSpaceId = this.shortName;
          return this.openSpaceId;
        }
        const tmp = await spaceService.getByShort(this.shortName)
        this.openSpaceId = tmp.data.short_name
        return this.openSpaceId;
      }
    }
  }
})
