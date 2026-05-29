import api from '@/plugins/axios'

export const attachmentService = {
  listByEntity: (entityType, entityId) => api.get(`/api/v2/attachment/${entityType}/${entityId}`),
  create: (data) => api.post('/api/v2/attachment/', data),
  delete: (id) => api.delete(`/api/v2/attachment/${id}`),
}
