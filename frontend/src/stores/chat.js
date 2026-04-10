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

  const addMessage = (userMessage, assistantResponse, sqlQuery, chartConfig) => {
    // Ajouter le message utilisateur si fourni
    if (userMessage && userMessage.trim()) {
      const userMsg = {
        id: Date.now() + Math.random(),
        role: "user",
        content: userMessage.trim()
      }
      messages.value.push(userMsg)
    }
    
    // Ajouter la réponse assistant si fournie (et non vide)
    if (assistantResponse && assistantResponse.trim()) {
      const assistantMsg = {
        id: Date.now() + Math.random() + 1,
        role: "assistant",
        content: assistantResponse.trim(),
        sql_query: sqlQuery || null,
        chart_config: chartConfig || null
      }
      messages.value.push(assistantMsg)
    }
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
