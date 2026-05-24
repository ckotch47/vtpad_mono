import api from '@/plugins/axios'

export const techDocService = {
  getTree: (spaceId) => api.get(`/api/v2/tech-doc/space/${spaceId}/tree`),
  listBySpace: (spaceId) => api.get(`/api/v2/tech-doc/space/${spaceId}`),
  getById: (id) => api.get(`/api/v2/tech-doc/${id}`),
  create: (data) => api.post('/api/v2/tech-doc/', data),
  update: (id, data) => api.patch(`/api/v2/tech-doc/${id}`, data),
  delete: (id) => api.delete(`/api/v2/tech-doc/${id}`),
}
