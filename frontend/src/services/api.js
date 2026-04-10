import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_PREFIX = import.meta.env.VITE_API_PREFIX || '/api/v1'

const apiClient = axios.create({
  baseURL: `${API_URL}${API_PREFIX}`,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add token to requests
apiClient.interceptors.request.use((config) => {
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

export default apiClient
