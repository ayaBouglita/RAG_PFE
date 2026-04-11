<template>
  <div class="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
    <!-- Left Side - Title -->
    <div>
      <h2 v-if="currentConversation" class="text-xl font-bold text-primary-600">
        {{ currentConversation.title }}
      </h2>
      <h2 v-else class="text-xl font-bold text-gray-600">
        Assistant IA - RAG Intelligence
      </h2>
    </div>

    <!-- Right Side - User Info & Menu -->
    <div v-if="authStore.user" class="flex items-center gap-6">
      <!-- Admin Links -->
      <div v-if="authStore.isAdmin" class="flex items-center gap-4">
        <router-link
          to="/admin/users"
          class="text-sm font-medium text-gray-700 hover:text-blue-600 transition"
        >
          👨‍💼 Utilisateurs
        </router-link>
        <router-link
          to="/admin/stats"
          class="text-sm font-medium text-gray-700 hover:text-blue-600 transition"
        >
          📊 Statistiques
        </router-link>
      </div>

      <!-- User Menu -->
      <div class="relative">
        <button
          @click="showMenu = !showMenu"
          class="flex items-center gap-3 hover:bg-gray-100 px-3 py-2 rounded-lg transition"
        >
          <div class="text-right">
            <p class="font-semibold text-gray-900 text-sm">{{ authStore.user.username }}</p>
            <p class="text-xs text-gray-500">
              {{ authStore.isAdmin ? '👨‍💼 Admin' : '👤 Utilisateur' }}
            </p>
          </div>
          <div class="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
            {{ authStore.user.username.charAt(0).toUpperCase() }}
          </div>
        </button>

        <!-- Dropdown Menu -->
        <div
          v-if="showMenu"
          class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10"
        >
          <router-link
            to="/chat"
            class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
            @click="showMenu = false"
          >
            💬 Chat
          </router-link>
          <div v-if="authStore.isAdmin" class="border-t border-gray-200">
            <router-link
              to="/admin/users"
              class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              @click="showMenu = false"
            >
              👨‍💼 Gestion Utilisateurs
            </router-link>
            <router-link
              to="/admin/stats"
              class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              @click="showMenu = false"
            >
              📊 Statistiques
            </router-link>
          </div>
          <button
            @click="logout"
            class="w-full text-left block px-4 py-2 text-sm text-red-600 hover:bg-red-50 border-t border-gray-200"
          >
            🚪 Déconnexion
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import { useChatStore } from '../stores/chat.js'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const chatStore = useChatStore()
const router = useRouter()
const showMenu = ref(false)

const currentConversation = computed(() => chatStore.currentConversation)

const logout = () => {
  authStore.logout()
  showMenu.value = false
  router.push('/login')
}
</script>
