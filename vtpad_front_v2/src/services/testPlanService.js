import api from '@/plugins/axios'

export const testPlanService = {
  listBySpace: (spaceId, params) => api.get(`/api/v2/test-plan/space/${spaceId}`, { params }),
  getById: (id) => api.get(`/api/v2/test-plan/${id}`),
  getCases: (id) => api.get(`/api/v2/test-plan/${id}/cases`),
  create: (data) => api.post('/api/v2/test-plan/', data),
  update: (id, data) => api.patch(`/api/v2/test-plan/${id}`, data),
  delete: (id) => api.delete(`/api/v2/test-plan/${id}`),
}
