<template>
  <v-card>
    <v-row no-gutters>
      <v-col cols="12" md="6" class="pa-4">
        <v-date-picker
          v-model="dates"
          class="data-picker--compact"
          multiple="range"
          title=""
          @update:modelValue="getBugsList"
        />
      </v-col>

      <v-col cols="12" md="6" class="pa-4">
        <v-select
          class="py-2"
          label="Create user"
          variant="outlined"
          :items="userList"
          item-title="username"
          item-value="id"
          @update:modelValue="setUserId"
        />

        <reports-pie-chart-component v-if="dataChar" :data-chart="dataChar" />
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ReportsPieChartComponent from '@/components/reports/reportsPieChartComponent.vue'
import { qaReportService } from '@/services'
import { color } from '@/components/common/collorList'

const route = useRoute()
const spaceId = ref('')

const emit = defineEmits(['selectFilterEmit'])

const props = defineProps({
  statistic: Object
})

const userList = ref([])
const dates = ref([])
const userId = ref(undefined)
const dataChar = ref({
  labelList: [],
  colorList: [],
  dataList: []
})

watch(() => props.statistic, (val) => {
  dataChar.value = {
    labelList: [],
    colorList: [],
    dataList: []
  }
  for (const i of Object.keys(val)) {
    dataChar.value.labelList.push(i)
    dataChar.value.colorList.push(color[i])
    dataChar.value.dataList.push(val[i])
  }
}, { deep: false, immediate: true })

function getUserForFilter() {
  qaReportService.getUsers(spaceId.value).then(res => {
    userList.value = res.data
  })
}

function setUserId(id) {
  userId.value = id
  getBugsList()
}

function getBugsList() {
  if (dates.value.length < 2 || !userId.value) return
  emit('selectFilterEmit', {
    date_start: dates.value[0].toISOString(),
    date_end: dates.value[dates.value.length - 1].toISOString(),
    create_user: userId.value,
    space_id: spaceId.value
  })
}

onMounted(() => {
  spaceId.value = route.params.spaceId
  getUserForFilter()
})
</script>

<style scoped>
</style>
