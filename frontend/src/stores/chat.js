import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '../services/api'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref([])
  const currentConversation = ref(null)
  const messages = ref([])
  const loading = ref(false)

  const setConversations = (convs) => {
    conversations.value = convs
  }

  const addConversation = (conv) => {
    conversations.value.push(conv)
  }

  const selectConversation = (conv) => {
    currentConversation.value = conv
  }

  const setMessages = (msgs) => {
    messages.value = msgs
  }

  const addMessage = (message) => {
    messages.value.push(message)
  }

  const setLoading = (value) => {
    loading.value = value
  }

  const loadConversationMessages = async (conversationId) => {
    try {
      setLoading(true)
      const response = await apiClient.get(
        `/chat/conversations/${conversationId}/messages`
      )
      setMessages(response.data.messages || [])
    } catch (error) {
      console.error('Erreur lors du chargement des messages:', error)
      setMessages([])
    } finally {
      setLoading(false)
    }
  }

  return {
    conversations,
    currentConversation,
    messages,
    loading,
    setConversations,
    addConversation,
    selectConversation,
    setMessages,
    addMessage,
    setLoading,
    loadConversationMessages
  }
})
