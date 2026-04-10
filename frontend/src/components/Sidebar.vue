<template>
  <div class="w-64 bg-white border-r border-gray-200 flex flex-col h-screen">
    <!-- Header -->
    <div class="p-4 border-b border-gray-200">
      <h1 class="text-xl font-bold text-primary-600 mb-4">💬 Conversations</h1>
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
        class="w-full px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-semibold"
      >
        🚪 Déconnexion
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

const selectConversation = (conv) => {
  chatStore.selectConversation(conv)
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
