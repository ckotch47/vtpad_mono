import api from '@/plugins/axios'

export const qaReportService = {
  getUsers: (spaceId) => api.get(`/api/v1/qa-report/users?space_id=${spaceId}`),
  getBugList: (params) => api.get('/api/v1/qa-report/bug-list', { params }),
}
