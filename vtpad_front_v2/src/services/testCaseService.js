import api from '@/plugins/axios'

export const testCaseService = {
  listBySpace: (spaceId, params) => api.get(`/api/v2/test-case/space/${spaceId}`, { params }),
  listBySuite: (suiteId) => api.get(`/api/v2/test-case/suite/${suiteId}`),
  listBySection: (sectionId) => api.get(`/api/v2/test-case/section/${sectionId}`),
  getById: (id) => api.get(`/api/v2/test-case/${id}`),
  create: (data) => api.post('/api/v2/test-case/', data),
  update: (id, data) => api.patch(`/api/v2/test-case/${id}`, data),
  move: (id, suiteId, sectionId) => api.post(`/api/v2/test-case/${id}/move`, {
    suite_id: suiteId,
    section_id: sectionId
  }),
  delete: (id) => api.delete(`/api/v2/test-case/${id}`),
  sort: (id) => api.patch(`/api/v2/test-case/sort/${id}`),
  getRuns: (id, params) => api.get(`/api/v2/test-case/${id}/runs`, { params }),
  duplicate: (id) => api.post(`/api/v2/test-case/${id}/duplicate`),
  getVersions: (id) => api.get(`/api/v2/test-case/${id}/versions`),
  getVersion: (id, versionId) => api.get(`/api/v2/test-case/${id}/versions/${versionId}`),
  restoreVersion: (id, versionId) => api.post(`/api/v2/test-case/${id}/versions/${versionId}/restore`),
  getTechDocs: (id) => api.get(`/api/v2/test-case/${id}/tech-docs`),
  updateTechDocs: (id, techDocIds) => api.put(`/api/v2/test-case/${id}/tech-docs`, { tech_doc_ids: techDocIds }),
}
