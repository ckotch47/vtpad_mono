import api from '@/plugins/axios'

export const sectionService = {
  getTree: (suiteId) => api.get(`/api/v2/section/suite/${suiteId}/tree`),
  create: (data) => api.post('/api/v2/section/', data),
  update: (id, data) => api.patch(`/api/v2/section/${id}`, data),
  delete: (id) => api.delete(`/api/v2/section/${id}`),
  sort: (id) => api.patch(`/api/v2/section/sort/${id}`),
}
