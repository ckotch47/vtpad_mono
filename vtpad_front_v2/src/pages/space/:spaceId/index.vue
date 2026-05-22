<template >

</template>

<script>


export default {
  name: "SpaceDetailPage",
  meta: {
    newMeta: 'asdd'
  },
  data(){
    return{
      spaceId: this.$route.params.spaceId
    }
  },
  updated() {
    this.spaceId= this.$route.params.spaceId
  },
  mounted() {

  }


}
</script>

<style scoped>

</style>
