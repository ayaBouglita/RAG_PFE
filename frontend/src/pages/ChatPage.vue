<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Sidebar -->
    <Sidebar />

    <!-- Main Chat Area -->
    <div class="flex-1 flex flex-col">
      <!-- Header -->
      <Header />

      <!-- Messages Container -->
      <div class="flex-1 overflow-y-auto p-6 space-y-4" ref="messagesContainer">
        <!-- Empty State -->
        <div v-if="!currentConversation" class="flex items-center justify-center h-full">
          <div class="text-center">
            <svg class="w-24 h-24 mx-auto mb-4 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <h2 class="text-2xl font-bold text-gray-700 mb-2">Aucune conversation</h2>
            <p class="text-gray-500">Créez une nouvelle conversation pour commencer</p>
          </div>
        </div>

        <!-- Messages -->
        <div v-else class="space-y-4">
          <ChatMessage
            v-for="msg in messages"
            :key="msg.id"
            :message="msg"
            :is-user="msg.role === 'user'"
          />

          <!-- Loading Indicator -->
          <div v-if="loading" class="flex justify-start">
            <div class="bg-gray-300 rounded-lg rounded-bl-none p-4 max-w-xs animated-pulse">
              <div class="flex gap-2">
                <div class="w-2 h-2 bg-gray-600 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-gray-600 rounded-full animate-bounce" style="animation-delay: 0.2s;"></div>
                <div class="w-2 h-2 bg-gray-600 rounded-full animate-bounce" style="animation-delay: 0.4s;"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div v-if="currentConversation" class="bg-white border-t border-gray-200 p-6">
        <form @submit.prevent="sendMessage" class="flex gap-3">
          <input
            v-model="newMessage"
            type="text"
            placeholder="Posez votre question à l'assistant IA..."
            :disabled="loading"
            class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            :disabled="!newMessage.trim() || loading"
            class="bg-primary-500 hover:bg-primary-600 text-white px-6 py-3 rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <span>Envoyer</span>
            <span v-if="!loading">➤</span>
            <span v-else class="animate-spin">⏳</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import { useChatStore } from '../stores/chat.js'
import { chatService } from '../services/api.js'
import Sidebar from '../components/Sidebar.vue'
import Header from '../components/Header.vue'
import ChatMessage from '../components/ChatMessage.vue'

const authStore = useAuthStore()
const chatStore = useChatStore()

const newMessage = ref('')
const messagesContainer = ref(null)
const loading = computed(() => chatStore.loading)
const currentConversation = computed(() => chatStore.currentConversation)
const messages = computed(() => chatStore.messages)

// Auto-scroll to bottom
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

watch(() => messages.value.length, scrollToBottom)

onMounted(async () => {
  try {
    const response = await chatService.listConversations()
    chatStore.setConversations(response.data.conversations || [])
  } catch (err) {
    console.error('Erreur lors du chargement des conversations:', err)
  }
})

const sendMessage = async () => {
  if (!newMessage.value.trim() || !currentConversation.value || loading.value) return

  const messageText = newMessage.value
  newMessage.value = ''

  // Ajouter immédiatement le message utilisateur (avant l'appel API)
  chatStore.addMessage(messageText, null, null, null)

  chatStore.setLoading(true)

  try {
    const response = await chatService.sendMessage(currentConversation.value.id, messageText)
    
    // Ajouter la réponse de l'assistant
    chatStore.addMessage(
      null, // pas de message utilisateur (déjà ajouté)
      response.data.assistant_response,
      response.data.sql_query,
      response.data.chart_config || null
    )
  } catch (err) {
    console.error('Erreur lors de l\'envoi du message:', err)
    const errorText = err.response?.data?.detail || 'Une erreur est survenue'
    // Remplacer le dernier message par l'erreur
    chatStore.addMessage(
      null,
      '❌ Erreur: ' + errorText,
      null,
      null
    )
  } finally {
    chatStore.setLoading(false)
  }
}
</script>
