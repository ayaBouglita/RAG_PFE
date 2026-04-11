<template>
  <div class="min-h-screen bg-gray-100">
    <Header />
    
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Title -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Statistiques Système</h1>
        <p class="text-gray-600 mt-2">Vue d'ensemble des utilisateurs et de l'activité du système</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-flex items-center space-x-2">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span class="text-gray-600">Chargement des statistiques...</span>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
        <p class="text-red-700">{{ errorMessage }}</p>
      </div>

      <!-- Stats Grid -->
      <div v-if="!loading && stats" class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <!-- Total Users Card -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-500 text-sm font-medium">Total d'utilisateurs</p>
              <p class="text-3xl font-bold text-gray-900 mt-2">{{ stats.total_users }}</p>
            </div>
            <div class="bg-blue-100 rounded-lg p-3">
              <svg class="h-8 w-8 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 9a3 3 0 100-6 3 3 0 000 6m0 0a7 7 0 1 1 0 14 7 7 0 0 1 0-14z" />
              </svg>
            </div>
          </div>
        </div>

        <!-- Admins Card -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-500 text-sm font-medium">Administrateurs</p>
              <p class="text-3xl font-bold text-purple-600 mt-2">{{ stats.admin_count }}</p>
            </div>
            <div class="bg-purple-100 rounded-lg p-3">
              <svg class="h-8 w-8 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
              </svg>
            </div>
          </div>
        </div>

        <!-- Regular Users Card -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-500 text-sm font-medium">Utilisateurs Normaux</p>
              <p class="text-3xl font-bold text-green-600 mt-2">{{ stats.user_count }}</p>
            </div>
            <div class="bg-green-100 rounded-lg p-3">
              <svg class="h-8 w-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10.5 1.5H9.5V9H1.5v1h7.5v7.5h1V10h7.5V9h-7.5V1.5z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Role Distribution -->
      <div v-if="!loading && stats" class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <!-- Role Distribution Card -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-6">Répartition des Rôles</h2>
          <div class="space-y-4">
            <!-- Admin Bar -->
            <div>
              <div class="flex justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">👨‍💼 Administrateurs</span>
                <span class="text-sm font-medium text-gray-700">{{ adminPercentage }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-purple-600 h-2 rounded-full transition-all duration-300"
                  :style="{ width: adminPercentage + '%' }"
                ></div>
              </div>
              <p class="text-xs text-gray-500 mt-1">{{ stats.admin_count }} / {{ stats.total_users }}</p>
            </div>

            <!-- User Bar -->
            <div>
              <div class="flex justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">👤 Utilisateurs</span>
                <span class="text-sm font-medium text-gray-700">{{ userPercentage }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-green-600 h-2 rounded-full transition-all duration-300"
                  :style="{ width: userPercentage + '%' }"
                ></div>
              </div>
              <p class="text-xs text-gray-500 mt-1">{{ stats.user_count }} / {{ stats.total_users }}</p>
            </div>
          </div>
        </div>

        <!-- Statistics Summary -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-6">Résumé</h2>
          <div class="space-y-3">
            <div class="flex justify-between items-center pb-3 border-b">
              <span class="text-gray-600">Total d'utilisateurs:</span>
              <span class="font-semibold text-gray-900">{{ stats.total_users }}</span>
            </div>
            <div class="flex justify-between items-center pb-3 border-b">
              <span class="text-gray-600">Administrateurs:</span>
              <span class="font-semibold text-purple-600">{{ stats.admin_count }}</span>
            </div>
            <div class="flex justify-between items-center pb-3 border-b">
              <span class="text-gray-600">Utilisateurs normaux:</span>
              <span class="font-semibold text-green-600">{{ stats.user_count }}</span>
            </div>
            <div class="flex justify-between items-center pt-3">
              <span class="text-gray-600">Ratio Admin/Utilisateur:</span>
              <span class="font-semibold text-gray-900">1:{{ ratioAdminUser }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Registrations Over Time -->
      <div v-if="!loading && stats && stats.registrations_by_date.length > 0" class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-6">Évolution des Inscriptions</h2>
        
        <!-- Chart -->
        <div class="space-y-4">
          <div v-for="(item, index) in stats.registrations_by_date" :key="index" class="flex items-center">
            <div class="w-24 text-sm text-gray-600">{{ formatDate(item.date) }}</div>
            <div class="flex-1">
              <div class="bg-gray-200 rounded-full h-6 relative">
                <div
                  class="bg-blue-600 h-6 rounded-full flex items-center justify-end pr-3 transition-all duration-300"
                  :style="{ width: getChartWidth(item.count) + '%' }"
                >
                  <span v-if="getChartWidth(item.count) > 15" class="text-xs font-semibold text-white">
                    {{ item.count }}
                  </span>
                </div>
              </div>
              <span v-if="getChartWidth(item.count) <= 15" class="text-xs font-semibold text-blue-600 ml-2">
                {{ item.count }}
              </span>
            </div>
          </div>
        </div>

        <!-- Summary -->
        <div class="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p class="text-sm text-blue-900">
            <strong>Total des inscriptions:</strong> {{ totalRegistrations }} utilisateurs
          </p>
        </div>
      </div>

      <!-- No Data Message -->
      <div v-if="!loading && (!stats || stats.registrations_by_date.length === 0)" class="bg-white rounded-lg shadow p-6 text-center">
        <p class="text-gray-500">Aucune donnée d'inscription disponible</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import { adminService } from '../services/api.js'
import Header from '../components/Header.vue'

const authStore = useAuthStore()
const stats = ref(null)
const loading = ref(false)
const errorMessage = ref('')

onMounted(() => {
  console.log('AdminStats mounted')
  authStore.loadUser()
  console.log('Current user:', authStore.user)
  console.log('Token:', localStorage.getItem('access_token')?.substring(0, 20) + '...')
  fetchStats()
})

const adminPercentage = computed(() => {
  if (!stats.value || stats.value.total_users === 0) return 0
  return Math.round((stats.value.admin_count / stats.value.total_users) * 100)
})

const userPercentage = computed(() => {
  if (!stats.value || stats.value.total_users === 0) return 0
  return Math.round((stats.value.user_count / stats.value.total_users) * 100)
})

const ratioAdminUser = computed(() => {
  if (!stats.value || stats.value.admin_count === 0) return '∞'
  return Math.round(stats.value.user_count / stats.value.admin_count)
})

const totalRegistrations = computed(() => {
  if (!stats.value) return 0
  return stats.value.registrations_by_date.reduce((sum, item) => sum + item.count, 0)
})

const fetchStats = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const data = await adminService.getStats()
    stats.value = data
    console.log('Stats loaded successfully:', stats.value)
  } catch (error) {
    console.error('Fetch error:', error)
    errorMessage.value = error.response?.data?.detail || error.message || 'Erreur lors du chargement des statistiques'
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    month: 'short',
    day: 'numeric'
  })
}

const getChartWidth = (count) => {
  if (!stats.value || stats.value.registrations_by_date.length === 0) return 0
  const maxCount = Math.max(...stats.value.registrations_by_date.map(item => item.count))
  return (count / maxCount) * 100
}
</script>
