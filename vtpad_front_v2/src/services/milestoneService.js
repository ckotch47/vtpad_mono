import api from '@/plugins/axios'

export const milestoneService = {
  list: (spaceId) => api.get(`/api/v2/milestone/space/${spaceId}`),
  getById: (id) => api.get(`/api/v2/milestone/${id}`),
  create: (data) => api.post('/api/v2/milestone', data),
  update: (id, data) => api.patch(`/api/v2/milestone/${id}`, data),
  delete: (id) => api.delete(`/api/v2/milestone/${id}`),
  close: (id) => api.post(`/api/v2/milestone/${id}/close`),
}
