import api from '@/plugins/axios'

export const apiTokenService = {
  list: () => api.get('/api/v2/api-token/'),
  create: (data) => api.post('/api/v2/api-token/', data),
  revoke: (tokenId) => api.delete(`/api/v2/api-token/${tokenId}`),
}
