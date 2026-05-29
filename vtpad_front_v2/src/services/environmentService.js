import api from '@/plugins/axios'

export const environmentService = {
  list: (spaceId) => api.get(`/api/v2/environment/space/${spaceId}`),
  getById: (id) => api.get(`/api/v2/environment/${id}`),
  create: (data) => api.post('/api/v2/environment', data),
  update: (id, data) => api.patch(`/api/v2/environment/${id}`, data),
  delete: (id) => api.delete(`/api/v2/environment/${id}`),
}
