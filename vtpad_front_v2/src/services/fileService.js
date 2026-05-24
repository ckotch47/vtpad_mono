import api from '@/plugins/axios'

export const fileService = {
  upload: (formData) => api.post('/api/v1/file', formData),
}
