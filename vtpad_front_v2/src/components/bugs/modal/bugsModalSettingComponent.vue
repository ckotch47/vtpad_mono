<template>
    <v-text-field
      label="Link"
      variant="outlined"
      :model-value="bug.external_link"
      @change="updateBug('external_link', $event)"
    />

    <v-select
      class="select-custom"
      label="Assigner"
      :items="filter.user"
      item-value="id"
      item-title="username"
      :model-value="bug.assigner_user.id"
      v-model="bug.assigner_user.id"
      variant="outlined"
      @update:modelValue="updateBug('assigner_id', $event)"
    ></v-select>



    <v-select
      class="select-custom"
      label="State"
      :items="filter.state"
      :model-value="bug.state"
      v-model="bug.state"
      @update:modelValue="updateBug('state', $event)"
      variant="outlined"
    ></v-select>

    <div class="select-custom">
    <v-date-input
      class="select-custom"
      label="Estimate date"
      :model="dateVModel"
      v-model="dateVModel"
      @update:modelValue="updateBug('estimate_date', $event)"
      variant="outlined" />
    </div>

    <v-select
      class="select-custom"
      label="Tags"
      multiple
      :items="filter.tag"
      item-value="id"
      item-title="title"
      :model-value="bug.tag"
      variant="outlined"
      v-model="bug.tag"
      @update:modelValue="updateBug('tags', $event)"
    ></v-select>
</template>

<script>
import { VDateInput } from 'vuetify/labs/VDateInput'
import { bugService } from '@/services'

export default {
  name: "bugsModalSettingComponent",
  components: {
    VDateInput,
  },
  emits:[
    'updateBug'
  ],
  props:{
    bug: Object,
    filter: Object,
  },
  data(){
    return{
      tags: [],
      openBugItem: {},
      exteranl_link: undefined,
      dateVModel: undefined
    }
  },
  mounted() {
    this.openBugItem = this.bug;
    this.dateVModel = this.openBugItem.estimate_date ? new Date(this.openBugItem.estimate_date) : undefined
  },
  methods:{
    updateBug(name, event){
      let value = undefined;
      switch (name) {
        case 'external_link':
          value = event.target.value;
          break;
        case 'estimateDate':
          value = new Date(event).toISOString();
          break;
        case 'tags':
          value = event;
          break;
        default:
          value = event;
          break;
      }
      bugService.update(this.bug.id,{
        [name]: value
      }).then(res => {
        this.openBugItem = res.data
        this.$emit('updateBug', res.data)
      })
    },
  }
}
</script>

<style lang="scss">
.select-custom{
  input{
    border: none;
  }
  .v-input__prepend{
    display: none !important;
  }
}
</style>
