<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-600 via-primary-500 to-accent-500 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="inline-block bg-white rounded-full p-4 mb-4">
          <span class="text-3xl">✨</span>
        </div>
        <h1 class="text-3xl font-bold text-white mb-2">S'inscrire</h1>
        <p class="text-blue-100">Créez votre compte pour commencer</p>
      </div>

      <!-- Card -->
      <div class="bg-white rounded-xl shadow-2xl p-8">
        <!-- Form -->
        <form @submit.prevent="handleRegister" class="space-y-4">
          <!-- Username -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Nom d'utilisateur</label>
            <input
              v-model="formData.username"
              type="text"
              placeholder="Choisissez un nom d'utilisateur"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
              required
            />
          </div>

          <!-- Email -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input
              v-model="formData.email"
              type="email"
              placeholder="Votre adresse email"
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
              placeholder="Créez un mot de passe sécurisé"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
              required
            />
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            {{ error }}
          </div>

          <!-- Success Message -->
          <div v-if="success" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">
            {{ success }}
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-primary-500 hover:bg-primary-600 text-white font-semibold py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="!loading">Créer mon compte</span>
            <span v-else class="flex items-center justify-center gap-2">
              <span class="animate-spin">⏳</span>
              Création...
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

        <!-- Login Link -->
        <RouterLink
          to="/login"
          class="block w-full text-center text-primary-500 hover:text-primary-600 font-semibold py-2 border border-primary-200 rounded-lg hover:bg-primary-50 transition-colors"
        >
          Déjà inscrit ? Se connecter
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
import { authService } from '../services/api.js'
import { RouterLink } from 'vue-router'

const router = useRouter()

const formData = ref({ username: '', email: '', password: '' })
const loading = ref(false)
const error = ref('')
const success = ref('')

const handleRegister = async () => {
  if (!formData.value.username || !formData.value.email || !formData.value.password) {
    error.value = 'Veuillez remplir tous les champs'
    return
  }

  if (formData.value.password.length < 6) {
    error.value = 'Le mot de passe doit contenir au moins 6 caractères'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    await authService.register(
      formData.value.username,
      formData.value.email,
      formData.value.password
    )
    
    success.value = '✅ Compte créé avec succès! Redirection vers la connexion...'
    
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erreur lors de l\'inscription'
  } finally {
    loading.value = false
  }
}
</script>
