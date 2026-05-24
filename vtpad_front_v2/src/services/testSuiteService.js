import api from '@/plugins/axios'

export const testSuiteService = {
  listBySpace: (spaceId, params) => api.get(`/api/v2/test-suite/space/${spaceId}`, { params }),
  getById: (id) => api.get(`/api/v2/test-suite/${id}`),
  create: (data) => api.post('/api/v2/test-suite/', data),
  update: (id, data) => api.patch(`/api/v2/test-suite/${id}`, data),
  delete: (id) => api.delete(`/api/v2/test-suite/${id}`),
  sort: (id) => api.patch(`/api/v2/test-suite/sort/${id}`),
}
