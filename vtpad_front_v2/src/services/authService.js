import api from '@/plugins/axios'

export const authService = {
  login: (data) => api.post('/api/v1/auth', data),
  refresh: (refreshToken) => api.post('/api/v1/auth/refresh', { refresh_token: refreshToken }),
}
