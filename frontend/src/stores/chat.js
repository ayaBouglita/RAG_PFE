import { defineStore } from 'pinia'
import { ref } from 'vue'

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
    messages.value = []
  }

  const addMessage = (message) => {
    messages.value.push(message)
  }

  const setLoading = (value) => {
    loading.value = value
  }

  return {
    conversations,
    currentConversation,
    messages,
    loading,
    setConversations,
    addConversation,
    selectConversation,
    addMessage,
    setLoading
  }
})
