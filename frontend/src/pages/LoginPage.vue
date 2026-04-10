<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-600 via-primary-500 to-accent-500 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="inline-block bg-white rounded-full p-4 mb-4">
          <span class="text-3xl">🔐</span>
        </div>
        <h1 class="text-3xl font-bold text-white mb-2">Connexion</h1>
        <p class="text-blue-100">Assistant IA - Intelligence RAG</p>
      </div>

      <!-- Card -->
      <div class="bg-white rounded-xl shadow-2xl p-8">
        <!-- Form -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <!-- Username -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Nom d'utilisateur</label>
            <input
              v-model="formData.username"
              type="text"
              placeholder="Entrez votre nom d'utilisateur"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
              required
            />
          </div>

          <!-- Password -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Mot de passe</label>
            <input
              v-model="formData.password"
              type="password"
              placeholder="Entrez votre mot de passe"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
              required
            />
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            {{ error }}
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-primary-500 hover:bg-primary-600 text-white font-semibold py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="!loading">Se connecter</span>
            <span v-else class="flex items-center justify-center gap-2">
              <span class="animate-spin">⏳</span>
              Connexion en cours...
            </span>
          </button>
        </form>

        <!-- Divider -->
        <div class="relative my-6">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-300"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-white text-gray-500">ou</span>
          </div>
        </div>

        <!-- Register Link -->
        <RouterLink
          to="/register"
          class="block w-full text-center text-primary-500 hover:text-primary-600 font-semibold py-2 border border-primary-200 rounded-lg hover:bg-primary-50 transition-colors"
        >
          Créer un compte
        </RouterLink>
      </div>

      <!-- Footer -->
      <div class="text-center mt-8">
        <p class="text-blue-100 text-sm">
          © 2024 Assistant IA. Tous droits réservés.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import { authService } from '../services/api.js'
import { RouterLink } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({ username: '', password: '' })
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!formData.value.username || !formData.value.password) {
    error.value = 'Veuillez remplir tous les champs'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const response = await authService.login(formData.value.username, formData.value.password)
    const { access_token, user } = response.data

    authStore.setAuth(user, access_token)
    router.push('/chat')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erreur de connexion. Vérifiez vos identifiants.'
  } finally {
    loading.value = false
  }
}
</script>
