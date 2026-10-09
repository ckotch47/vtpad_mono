import api from '@/plugins/axios'

export const qaReportService = {
  getUsers: (spaceId) => api.get(`/api/qa-report/users?space_id=${spaceId}`),
  getBugList: (params) => api.get('/api/qa-report/bug-list', { params }),
  getEmailRecipients: (spaceId) => api.get(`/api/qa-report/email/recipients/${spaceId}`),
  previewEmailReport: (payload) => api.post('/api/qa-report/email/preview', payload),
  sendEmailReport: (payload) => api.post('/api/qa-report/email/send', payload),
}
