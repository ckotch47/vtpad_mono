import api from '@/plugins/axios'

export const analyticsService = {
  getSpaceStats: (spaceId) => api.get(`/api/v2/analytics/space/${spaceId}`),
  getTopFailed: (spaceId, limit = 10) => api.get(`/api/v2/analytics/space/${spaceId}/top-failed`, { params: { limit } }),
  getTrend: (spaceId, days = 30) => api.get(`/api/v2/analytics/space/${spaceId}/trend`, { params: { days } }),
  getCoverage: (suiteId) => api.get(`/api/v2/analytics/suite/${suiteId}/coverage`),
}
