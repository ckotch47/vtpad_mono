import api from '@/plugins/axios'

export const reportService = {
  listTests: (spaceId) => api.get(`/api/v2/report/${spaceId}/test/list`),
  getTestDetail: (spaceId, testId) => api.get(`/api/v2/report/${spaceId}/test/${testId}/detail`),
  getTestSuites: (spaceId, testId) => api.get(`/api/v2/report/${spaceId}/test/${testId}/suite/list`),
  getSuiteDetail: (spaceId, suiteId) => api.get(`/api/v2/report/${spaceId}/test/suite/${suiteId}/detail`),
}
