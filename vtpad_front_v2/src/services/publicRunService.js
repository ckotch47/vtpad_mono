import api from '@/plugins/axios'

const managementPath = (runId) => `/api/v2/test-run/${encodeURIComponent(runId)}/public-link`

export const publicRunService = {
  createLink(runId) {
    return api.post(managementPath(runId))
  },
  getLinkStatus(runId) {
    return api.get(managementPath(runId))
  },
  revokeLink(runId) {
    return api.delete(managementPath(runId))
  }
}

// Do not use the shared Axios instance here: its interceptors read the logged-in
// user's token from localStorage and may redirect or toast on a 401 response.
export async function redeemSharedRun(shareToken) {
  const baseUrl = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '')
  const response = await fetch(`${baseUrl}/api/v2/test-run/public/shared`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${shareToken}`
    },
    cache: 'no-store',
    credentials: 'omit',
    referrerPolicy: 'no-referrer'
  })

  if (!response.ok) {
    const error = new Error('Shared run unavailable')
    error.status = response.status
    throw error
  }

  return response.json()
}
