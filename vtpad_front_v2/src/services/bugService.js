import api from '@/plugins/axios'

export const bugService = {
  list: (params) => api.get('/api/v1/bugs', { params }),
  getById: (id) => api.get(`/api/v1/bugs/detail/${id}`),
  getByShort: (shortName) => api.get(`/api/v2/bugs/short/${shortName}`),
  getFilters: (spaceId) => api.get(`/api/v1/bugs/filters?space_id=${spaceId}`),
  create: (data) => api.post('/api/v1/bugs', data),
  update: (id, data) => api.patch(`/api/v2/bugs/${id}`, data),
}
