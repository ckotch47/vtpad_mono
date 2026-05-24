import api from '@/plugins/axios'

export const spaceService = {
  list: () => api.get('/api/v1/space'),
  listCompany: () => api.get('/api/v1/company/spaces'),
  create: (data) => api.post('/api/v1/space', data),
  getById: (id) => api.get(`/api/v1/space/${id}`),
  getByShort: (shortName) => api.get(`/api/v1/space/by-short/${shortName}`),
  update: (id, data) => api.put(`/api/v1/space/${id}`, data),
  delete: (id) => api.delete(`/api/v1/space/${id}`),

  getUsers: (id) => api.get(`/api/v1/space/${id}/users`),
  addUser: (id, data) => api.put(`/api/v1/space/${id}/user`, data),
  removeUser: (spaceId, userId) => api.delete(`/api/v1/space/${spaceId}/user/${userId}`),
  updateUser: (spaceId, userId, data) => api.patch(`/api/v1/space/${spaceId}/user/${userId}`, data),
  makeOwner: (spaceId, userId) => api.put(`/api/v1/space/${spaceId}/user-make-owner/${userId}`),

  getStatistic: (id) => api.get(`/api/v1/space/${id}/statistic`),
  getAllRuns: (id) => api.get(`/api/v1/space/${id}/all_runs`),
}
