import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token'))

  const isAuthenticated = computed(() => !!token.value)

  const setAuth = (userData, accessToken) => {
    user.value = userData
    token.value = accessToken
    localStorage.setItem('access_token', accessToken)
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
  }

  return {
    user,
    token,
    isAuthenticated,
    setAuth,
    logout
  }
})
