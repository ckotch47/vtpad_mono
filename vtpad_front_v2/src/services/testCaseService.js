import api from '@/plugins/axios'

export const testCaseService = {
  listBySpace: (spaceId, params) => api.get(`/api/v2/test-case/space/${spaceId}`, { params }),
  listBySuite: (suiteId) => api.get(`/api/v2/test-case/suite/${suiteId}`),
  listBySection: (sectionId) => api.get(`/api/v2/test-case/section/${sectionId}`),
  getById: (id) => api.get(`/api/v2/test-case/${id}`),
  create: (data) => api.post('/api/v2/test-case/', data),
  update: (id, data) => api.patch(`/api/v2/test-case/${id}`, data),
  delete: (id) => api.delete(`/api/v2/test-case/${id}`),
  sort: (id) => api.patch(`/api/v2/test-case/sort/${id}`),
  getRuns: (id, params) => api.get(`/api/v2/test-case/${id}/runs`, { params }),
  duplicate: (id) => api.post(`/api/v2/test-case/${id}/duplicate`),
}
