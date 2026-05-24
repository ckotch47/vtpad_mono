<template>
  <v-card class="d-flex justify-space-between ">
    <v-card-item class="w-50 justify-center">
      <v-date-picker
        class="data-picker--compact"
        multiple="range"
        v-model="dates"
        title=""
        @update:modelValue="getBugsList"
      />
    </v-card-item>

    <v-card-item class="w-50">
      <v-select
        class="py-2"
        label="Create user"
        variant="outlined"
        :items="userList"
        :item-title="'username'"
        :item-value="'id'"
        @update:modelValue="setUserId($event)"
      />

      <reports-pie-chart-component  :data-chart="dataChar" v-if="dataChar"/>
    </v-card-item>
  </v-card>
</template>

<script>
import ReportsPieChartComponent from "@/components/reports/reportsPieChartComponent.vue";
import { qaReportService } from '@/services'
import {color} from "@/components/common/collorList";

export default {
  name: "reportQaFilterComponent",
  components: {ReportsPieChartComponent},
  emits: ['selectFilterEmit'],
  props:{
    statistic: Object
  },
  data: () => ({
    userList: [],
    dates: [],
    spaceId: '',
    userId: undefined,

    dataChar: {
      labelList: [],
      colorList: [],
      dataList: []
    }
  }),
  watch:{
    statistic: {
      handler() {
        this.dataChar = {
          labelList: [],
          colorList: [],
          dataList: []
        }
        for(const i of Object.keys(this.statistic)){
          this.dataChar.labelList.push(i);
          this.dataChar.colorList.push(color[i]);
          this.dataChar.dataList.push(this.statistic[i])
        }
        console.log(this.dataChar)
      },
      deep: false
    },
  },
  mounted() {
    // for(const i of this.statistic.keys()){
    //   console.log(i)
    // }
    this.spaceId= this.$route.params.spaceId;
    this.getUserForFilter();
  },
  methods:{
    getUserForFilter(){
      qaReportService.getUsers(this.spaceId).then(res => {
        this.userList = res.data;
      })
    },
    setUserId(userId){
      this.userId = userId;
      this.getBugsList();
    },
    getBugsList(){
      if(this.dates.length < 2 || !this.userId) return;
      this.$emit('selectFilterEmit', {
        date_start: this.dates[0].toISOString(), //[0].toISOString().split('T')[0],
        date_end: this.dates[this.dates.length - 1].toISOString(), //.toISOString().split('T')[0],
        create_user: this.userId,
        space_id: this.spaceId
      })
    }
  }
}
</script>

<style scoped>

</style>
