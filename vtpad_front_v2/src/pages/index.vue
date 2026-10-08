<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

defineOptions({ name: 'HomeRedirectPage' })

const router = useRouter()
onMounted(() => {
  router.replace('/company/spaces')
})
</script>
