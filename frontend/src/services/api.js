import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_PREFIX = import.meta.env.VITE_API_PREFIX || '/api/v1'

const apiClient = axios.create({
  baseURL: `${API_URL}${API_PREFIX}`,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Admin API Client (routes sans /api/v1)
const adminClient = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add token to requests (apiClient)
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Add token to requests (adminClient)
adminClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authService = {
  register(username, email, password) {
    return apiClient.post('/auth/register', { username, email, password })
  },
  
  login(username, password) {
    return apiClient.post('/auth/login', { username, password })
  }
}

export const chatService = {
  createConversation(title) {
    return apiClient.post('/chat/conversations', { title })
  },
  
  listConversations() {
    return apiClient.get('/chat/conversations')
  },
  
  sendMessage(conversationId, message) {
    return apiClient.post('/chat/message', {
      conversation_id: conversationId,
      message: message
    })
  },
  
  getConversationMessages(conversationId) {
    return apiClient.get(`/chat/conversations/${conversationId}/messages`)
  }
}

// Admin Services
export const adminService = {
  getUsers() {
    return adminClient.get('/admin/users')
      .then(res => res.data)
      .catch(error => {
        console.error('Error in getUsers:', error.response?.data || error.message)
        throw error
      })
  },
  
  createUser(username, email, password) {
    return adminClient.post('/admin/users', { username, email, password })
      .then(res => res.data)
      .catch(error => {
        console.error('Error in createUser:', error.response?.data || error.message)
        throw error
      })
  },
  
  updateUser(userId, data) {
    return adminClient.put(`/admin/users/${userId}`, data)
      .then(res => res.data)
      .catch(error => {
        console.error('Error in updateUser:', error.response?.data || error.message)
        throw error
      })
  },
  
  deleteUser(userId) {
    return adminClient.delete(`/admin/users/${userId}`)
      .then(res => res.data)
      .catch(error => {
        console.error('Error in deleteUser:', error.response?.data || error.message)
        throw error
      })
  },
  
  getStats() {
    console.log('Fetching stats from:', `${adminClient.defaults.baseURL}/admin/stats`)
    return adminClient.get('/admin/stats')
      .then(res => {
        console.log('Stats response received:', res.data)
        return res.data
      })
      .catch(error => {
        console.error('Error in getStats:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status,
          config: error.config
        })
        throw error
      })
  }
}

export default apiClient
