import api from '@/plugins/axios'

export const companyUserService = {
  list: () => api.get('/api/v2/company-user/list'),
  create: (data) => api.post('/api/v2/company-user', data),
  update: (userId, data) => api.put(`/api/v2/company-user/${userId}`, data),
  resetPassword: (userId) => api.put(`/api/v2/company-user/${userId}/reset-password`),
  delete: (userId) => api.delete(`/api/v2/company-user/${userId}`),
}
