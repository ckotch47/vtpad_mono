import api from '@/plugins/axios'

export const uploadService = {
  upload: (postId, formData) => api.post(`/api/uploads?post_id=${postId}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
}
