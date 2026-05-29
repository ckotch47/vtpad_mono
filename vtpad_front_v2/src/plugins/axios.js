import axios from 'axios'
import { toast } from 'vue3-toastify'
import vuetify from './vuetify'

// Configure default axios for backward compatibility with legacy components
axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL
axios.defaults.headers = {
  Accept: 'application/json',
  'Content-Type': 'application/json',
  responseType: 'json',
}

// Shared helper to attach auth token
function authInterceptor(config) {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}

// Shared response handler
function successHandler(response) {
  const methods = ['put', 'post', 'patch', 'delete']
  if (
    methods.includes(response.config.method) &&
    (response.status === 200 || response.status === 201)
  ) {
    toast.success('Success', {
      theme: vuetify.theme.name.value,
      transition: 'flip',
      autoClose: 1500,
    })
  }
  return response
}

function errorHandler(error) {
  if (error.response?.status === 401 && location.pathname !== '/auth') {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      location.href = '/auth'
      return Promise.reject(error)
    }
    axios
      .post('/api/v1/auth/refresh', { refresh_token: refreshToken })
      .then((res) => {
        if (!res || res.status !== 200) {
          location.href = '/auth'
          return
        }
        localStorage.setItem('auth_token', res.data.access_token)
        localStorage.setItem('refresh_token', res.data.refresh_token)
      })
      .catch(() => {
        localStorage.removeItem('auth_token')
        localStorage.removeItem('refresh_token')
        location.href = '/auth'
      })
  }
  const status = error.response?.status || ''
  let msg = error.message
  const data = error.response?.data
  if (typeof data === 'string') msg = data
  else if (data?.detail) {
    if (Array.isArray(data.detail)) msg = data.detail.map(d => d.msg || d).join(', ')
    else msg = data.detail
  } else if (data?.msg) msg = data.msg
  else if (data && typeof data === 'object') msg = JSON.stringify(data)
  toast.error(`${status ? status + ' ' : ''}${msg}`, {
    theme: vuetify.theme.name.value,
    transition: 'flip',
    autoClose: 3000,
  })
  return Promise.reject(error)
}

// Apply to default axios (legacy components)
axios.interceptors.request.use(authInterceptor)
axios.interceptors.response.use(successHandler, errorHandler)

// Named instance for useApi() — same config + interceptors
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
    responseType: 'json',
  },
})
api.interceptors.request.use(authInterceptor)
api.interceptors.response.use(successHandler, errorHandler)

export default api
