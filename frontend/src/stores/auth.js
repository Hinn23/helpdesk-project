import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/ticketsApi'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')
  const userId = ref(localStorage.getItem('userId') || '')
  const userRole = ref(localStorage.getItem('userRole') || '')
  const userName = ref(localStorage.getItem('userName') || '')
  const userStatus = ref(localStorage.getItem('userStatus') || 'active')

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => userRole.value === 'admin')
  const isWarned = computed(() => userStatus.value === 'warned')
  const isBanned = computed(() => userStatus.value === 'banned')

  function setAuth(data) {
    token.value = data.access_token
    if (data.refresh_token) refreshToken.value = data.refresh_token
    userId.value = String(data.user_id)
    userRole.value = data.role
    userName.value = data.name || ''
    userStatus.value = data.status || 'active'
    localStorage.setItem('token', data.access_token)
    if (data.refresh_token) localStorage.setItem('refreshToken', data.refresh_token)
    localStorage.setItem('userId', String(data.user_id))
    localStorage.setItem('userRole', data.role)
    localStorage.setItem('userName', data.name || '')
    localStorage.setItem('userStatus', data.status || 'active')
  }

  async function login(email, password) {
    const data = await authApi.login(email, password)
    setAuth(data)
  }

  async function register(name, email, password) {
    const data = await authApi.register(name, email, password)
    setAuth(data)
  }

  function logout() {
    token.value = ''
    refreshToken.value = ''
    userId.value = ''
    userRole.value = ''
    userName.value = ''
    userStatus.value = 'active'
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userId')
    localStorage.removeItem('userRole')
    localStorage.removeItem('userName')
    localStorage.removeItem('userStatus')
  }

  const userIdAsNumber = computed(() => Number(userId.value))

  let checked = false
  async function checkAuth() {
    if (!token.value || checked) return
    try {
      const data = await authApi.getMe()
      userRole.value = data.role
      userName.value = data.name || ''
      userStatus.value = data.status || 'active'
      localStorage.setItem('userRole', data.role)
      localStorage.setItem('userName', data.name || '')
      localStorage.setItem('userStatus', data.status || 'active')
    } catch {
      logout()
    }
    checked = true
  }

  return { token, refreshToken, userId, userIdAsNumber, userRole, userName, userStatus, isAuthenticated, isAdmin, isWarned, isBanned, login, register, logout, setAuth, checkAuth }
})
