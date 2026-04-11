<template>
  <div class="w-64 bg-white border-r border-gray-200 flex flex-col h-screen">
    <!-- Header -->
    <div class="p-4 border-b border-gray-200">
      <div class="flex items-center gap-2 mb-4">
        <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        <h1 class="text-xl font-bold text-primary-600">Conversations</h1>
      </div>
      <button
        @click="openNewConversation"
        class="w-full bg-accent-500 hover:bg-accent-400 text-white font-semibold py-2 rounded-lg transition-colors"
      >
        + Nouvelle
      </button>
    </div>

    <!-- New Conversation Modal -->
    <div v-if="showNewConvModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
        <h2 class="text-xl font-bold mb-4">Nouvelle Conversation</h2>
        <input
          v-model="newConvTitle"
          type="text"
          placeholder="Titre de la conversation..."
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none mb-4"
          @keyup.enter="createConversation"
        />
        <div class="flex gap-2">
          <button
            @click="showNewConvModal = false"
            class="flex-1 px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Annuler
          </button>
          <button
            @click="createConversation"
            class="flex-1 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600"
          >
            Créer
          </button>
        </div>
      </div>
    </div>

    <!-- Conversations List -->
    <div class="flex-1 overflow-y-auto">
      <div
        v-for="conv in conversations"
        :key="conv.id"
        @click="selectConversation(conv)"
        :class="[
          'p-4 cursor-pointer border-l-4 transition-colors',
          currentConversation?.id === conv.id
            ? 'bg-primary-50 border-l-primary-500'
            : 'border-l-transparent hover:bg-gray-50'
        ]"
      >
        <h3 class="font-semibold text-gray-900 truncate">{{ conv.title }}</h3>
        <p class="text-xs text-gray-500">{{ formatDate(conv.created_at) }}</p>
      </div>
    </div>

    <!-- Logout Button -->
    <div class="p-4 border-t border-gray-200">
      <button
        @click="logout"
        class="w-full px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-semibold flex items-center justify-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        Déconnexion
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import { useChatStore } from '../stores/chat.js'
import { chatService } from '../services/api.js'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

const showNewConvModal = ref(false)
const newConvTitle = ref('')
const conversations = computed(() => chatStore.conversations)
const currentConversation = computed(() => chatStore.currentConversation)

const openNewConversation = () => {
  newConvTitle.value = ''
  showNewConvModal.value = true
}

const createConversation = async () => {
  if (!newConvTitle.value.trim()) return

  try {
    const response = await chatService.createConversation(newConvTitle.value)
    chatStore.addConversation(response.data)
    chatStore.selectConversation(response.data)
    showNewConvModal.value = false
  } catch (err) {
    console.error('Erreur lors de la création:', err)
  }
}

const selectConversation = async (conv) => {
  chatStore.selectConversation(conv)
  // Charger les messages historiques de cette conversation
  await chatStore.loadConversationMessages(conv.id)
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' })
}
</script>
