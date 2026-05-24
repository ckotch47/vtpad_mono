import api from '@/plugins/axios'

export const userService = {
  getCurrent: () => api.get('/api/v2/user'),
  updateCurrent: (data) => api.patch('/api/v2/user', data),
  searchByMail: (mail) => api.get(`/api/v1/user/search/by-mail?mail=${encodeURIComponent(mail)}`),
}
