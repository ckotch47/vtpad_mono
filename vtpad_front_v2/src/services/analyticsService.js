import api from '@/plugins/axios'

export const analyticsService = {
  getSpaceStats: (spaceId) => api.get(`/api/v2/analytics/space/${spaceId}`),
  getCoverage: (suiteId) => api.get(`/api/v2/analytics/suite/${suiteId}/coverage`),
}
