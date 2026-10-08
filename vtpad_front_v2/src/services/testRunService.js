import api from '@/plugins/axios'

export const testRunService = {
  listBySpace: (spaceId, params) => api.get(`/api/v2/test-run/space/${spaceId}`, { params }),
  getById: (id) => api.get(`/api/v2/test-run/${id}`),
  getDetail: (id) => api.get(`/api/v2/test-run/${id}/detail`),
  // Preview is deliberately separate from create: a user can verify the exact
  // case set before a draft run is persisted. Older deployments do not expose
  // this route yet, therefore callers must fall back to the local count.
  preview: (data) => api.post('/api/v2/test-run/preview', data),
  create: (data) => api.post('/api/v2/test-run/', data),
  update: (id, data) => api.patch(`/api/v2/test-run/${id}`, data),
  start: (id) => api.post(`/api/v2/test-run/${id}/start`),
  pause: (id) => api.post(`/api/v2/test-run/${id}/pause`),
  resume: (id) => api.post(`/api/v2/test-run/${id}/resume`),
  complete: (id) => api.post(`/api/v2/test-run/${id}/complete`),
  delete: (id) => api.delete(`/api/v2/test-run/${id}`),

  updateResult: (resultId, data) => api.patch(`/api/v2/test-run/result/${resultId}`, data),
  bulkUpdateResults: (data) => api.patch('/api/v2/test-run/result/bulk', data),
}
