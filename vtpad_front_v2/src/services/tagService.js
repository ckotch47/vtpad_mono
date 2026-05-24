import api from '@/plugins/axios'

export const tagService = {
  list: (spaceId) => api.get(`/api/v1/tag/${spaceId}`),
  create: (spaceId, data) => api.post(`/api/v1/tag/${spaceId}`, data),
  update: (tagId, data) => api.put(`/api/v1/tag/${tagId}`, data),
  delete: (tagId) => api.delete(`/api/v1/tag/${tagId}`),
}
