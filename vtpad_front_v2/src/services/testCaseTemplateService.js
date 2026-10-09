import api from '@/plugins/axios'

export const testCaseTemplateService = {
  listBySpace: (spaceId, params = {}) => api.get(`/api/v2/test-case-template/space/${spaceId}`, { params }),
  getById: (spaceId, templateId) => api.get(`/api/v2/test-case-template/space/${spaceId}/${templateId}`),
  create: (spaceId, data) => api.post(`/api/v2/test-case-template/space/${spaceId}`, data),
  update: (spaceId, templateId, data) => api.put(`/api/v2/test-case-template/space/${spaceId}/${templateId}`, data)
}
