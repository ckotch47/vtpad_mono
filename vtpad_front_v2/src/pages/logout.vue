<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  localStorage.removeItem('auth_token')
  localStorage.removeItem('refresh_token')
  location.href = '/auth'
})
</script>
