import api from '@/plugins/axios'

export const customFieldService = {
  list: (spaceId, entityType) => {
    const params = entityType ? `?entity_type=${entityType}` : ''
    return api.get(`/api/v2/custom-field/space/${spaceId}${params}`)
  },
  getById: (id) => api.get(`/api/v2/custom-field/${id}`),
  create: (data) => api.post('/api/v2/custom-field', data),
  update: (id, data) => api.patch(`/api/v2/custom-field/${id}`, data),
  delete: (id) => api.delete(`/api/v2/custom-field/${id}`),
  setValue: (data) => api.post('/api/v2/custom-field/value', data),
  getValues: (entityId) => api.get(`/api/v2/custom-field/value/${entityId}`),
}
