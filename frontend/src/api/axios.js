import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
    'X-Client-Name': 'Helpdesk-Lite-Frontend',
  },
})

let isRefreshing = false
let failedQueue = []

function processQueue(error, token = null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error)
    else resolve(token)
  })
  failedQueue = []
}

api.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }
  return config
})

api.interceptors.response.use(
  (resp) => resp,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest?.url?.includes('/auth/refresh') && !originalRequest?._retry) {
      const authStore = useAuthStore()
      if (!authStore.refreshToken) {
        authStore.logout()
        window.location.href = '/login'
        return Promise.reject(error)
      }
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        })
      }
      originalRequest._retry = true
      isRefreshing = true
      try {
        const resp = await axios.post('/auth/refresh', { refresh_token: authStore.refreshToken })
        authStore.setAuth(resp.data)
        processQueue(null, resp.data.access_token)
        originalRequest.headers.Authorization = `Bearer ${resp.data.access_token}`
        return api(originalRequest)
      } catch {
        processQueue(error)
        authStore.logout()
        window.location.href = '/login'
        return Promise.reject(error)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  }
)

export default api
