import api from '@/plugins/axios'

/**
 * Shared API composable — thin wrapper around the configured axios instance.
 * Use this instead of importing axios directly in components.
 */
export function useApi() {
  const get = (url, config = {}) => api.get(url, config)
  const post = (url, data, config = {}) => api.post(url, data, config)
  const put = (url, data, config = {}) => api.put(url, data, config)
  const patch = (url, data, config = {}) => api.patch(url, data, config)
  const del = (url, config = {}) => api.delete(url, config)

  return {
    get,
    post,
    put,
    patch,
    delete: del,
    // expose raw instance for edge cases
    instance: api,
  }
}
