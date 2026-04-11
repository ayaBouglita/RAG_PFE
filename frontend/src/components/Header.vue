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
          class="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-blue-600 transition"
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10.5 1.5H9.5V9H1.5v1h7.5v7.5h1V10h7.5V9h-7.5V1.5z"/>
          </svg>
          Utilisateurs
        </router-link>
        <router-link
          to="/admin/stats"
          class="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-blue-600 transition"
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"/>
          </svg>
          Statistiques
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
            <p class="text-xs text-gray-500 flex items-center justify-end gap-1">
              <svg v-if="authStore.isAdmin" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z"/>
              </svg>
              <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"/>
              </svg>
              {{ authStore.isAdmin ? 'Admin' : 'Utilisateur' }}
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
            class="flex items-center gap-2 block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
            @click="showMenu = false"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 5a2 2 0 012-2h12a2 2 0 012 2v6a2 2 0 01-2 2H4l-3 3V5z"/>
            </svg>
            Chat
          </router-link>
          <div v-if="authStore.isAdmin" class="border-t border-gray-200">
            <router-link
              to="/admin/users"
              class="flex items-center gap-2 block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              @click="showMenu = false"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10.5 1.5H9.5V9H1.5v1h7.5v7.5h1V10h7.5V9h-7.5V1.5z"/>
              </svg>
              Gestion Utilisateurs
            </router-link>
            <router-link
              to="/admin/stats"
              class="flex items-center gap-2 block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              @click="showMenu = false"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"/>
              </svg>
              Statistiques
            </router-link>
          </div>
          <button
            @click="logout"
            class="flex items-center gap-2 w-full text-left block px-4 py-2 text-sm text-red-600 hover:bg-red-50 border-t border-gray-200"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clip-rule="evenodd"/>
            </svg>
            Déconnexion
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
