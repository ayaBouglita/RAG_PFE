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

    <!-- Right Side - User Info -->
    <div v-if="authStore.user" class="flex items-center gap-4">
      <div class="text-right">
        <p class="font-semibold text-gray-900">{{ authStore.user.username }}</p>
        <p class="text-xs text-gray-500">{{ authStore.user.email }}</p>
      </div>
      <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-accent-500 rounded-full flex items-center justify-center text-white font-bold">
        {{ authStore.user.username.charAt(0).toUpperCase() }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import { useChatStore } from '../stores/chat.js'

const authStore = useAuthStore()
const chatStore = useChatStore()

const currentConversation = computed(() => chatStore.currentConversation)
</script>
