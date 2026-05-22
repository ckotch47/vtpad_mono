<template>
  <div style="position:relative; display:inline-block; cursor: pointer">
    <v-btn class="user-right--btn" text="Right" color="wheat" />
    <v-select
      class="show-one"
      :items="right"
      item-value="name"
      item-title="title"
      variant="underlined"
      :multiple="true"
      v-model="selectRight"
      style="opacity:0; position:absolute; left:0;top:0;width:100%"
      @update:modelValue="updateRight"

    ></v-select>
  </div>

</template>

<script>
import axios from "axios";

export default {
  name: "settingsUserRightMenuComponent",
  emits: ['updateUserRightEmit'],
  props:{
    userRight: Object,
    userId: String,
    spaceId: String
  },
  data(){
    return{
      selectRight: [],
      right: [
        {title: 'edit pads', value: false, name: 'editPads'},
        {title: 'edit items', value: false, name: 'editItems'},
        {title: 'edit runs', value: false, name: 'editRuns'},
        {title: 'edit notes', value: false, name: 'editNotes'},
        {title: 'close bugs', value: false, name: 'closeBugs'},
        {title: 'edit tags', value: false, name: 'editTags'}
      ],
      rightObj: {
        "editPads": false,
        "editItems": false,
        "editRuns": false,
        "editNotes": false,
        "closeBugs": false,
        "editTags": false
      }
    }
  },
  mounted() {
    for(const elem of this.right){
      elem.value = this.userRight[elem.name] ?? false
      if(elem.value)
        this.selectRight.push(elem.name)
    }
  },
  methods:{
    updateRight(){
      for(const elem of this.selectRight){
        let rightElem = this.right.find(value => value.name === elem);
        rightElem.value = true;
        this.rightObj[rightElem.name] = rightElem.value
      }

      axios.patch(`/api/v1/space/${this.spaceId}/user/${this.userId}`, this.rightObj).then(res => {
        this.$emit('updateUserRightEmit')
      })
    }
  }
}
</script>

<style scoped>

</style>
