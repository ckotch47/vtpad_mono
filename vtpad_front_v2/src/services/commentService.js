import api from '@/plugins/axios'

export const commentService = {
  list: (bugId) => api.get(`/api/v1/comment/${bugId}`),
  create: (bugId, data) => api.post(`/api/v1/comment/${bugId}`, data),
  update: (commentId, data) => api.put(`/api/v1/comment/${commentId}`, data),
  delete: (commentId) => api.delete(`/api/v1/comment/${commentId}`),
}
