import { computed } from 'vue'
import { useRoute } from 'vue-router'

/**
 * Reactive helper for the current spaceId from route params.
 */
export function useSpace() {
  const route = useRoute()
  const spaceId = computed(() => route.params.spaceId)
  return { spaceId }
}
