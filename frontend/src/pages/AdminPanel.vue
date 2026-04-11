<template>
  <div class="min-h-screen bg-gray-100">
    <Header />
    
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Title -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Gestion des Utilisateurs</h1>
        <p class="text-gray-600 mt-2">Ajoutez, modifiez ou supprimez des comptes utilisateur</p>
      </div>

      <!-- Add User Button -->
      <div class="mb-6">
        <button
          @click="showAddUserModal = true"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          <svg class="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10.5 1.5H9.5V9H1.5v1h7.5v7.5h1V10h7.5V9h-7.5V1.5z"/>
          </svg>
          Ajouter un utilisateur
        </button>
      </div>

      <!-- Check if loading data -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-flex items-center space-x-2">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span class="text-gray-600">Chargement des utilisateurs...</span>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
        <p class="text-red-700">{{ errorMessage }}</p>
      </div>

      <!-- Success Message -->
      <div v-if="successMessage" class="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
        <p class="text-green-700">{{ successMessage }}</p>
      </div>

      <!-- Users Table -->
      <div v-if="!loading" class="bg-white rounded-lg shadow overflow-hidden">
        <table class="w-full">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Utilisateur</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Email</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Rôle</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Date d'inscription</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-700 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ user.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ user.username }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{{ user.email }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full',
                  user.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-green-100 text-green-800'
                ]">
                  {{ user.role === 'admin' ? '👨‍💼 Admin' : '👤 Utilisateur' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                {{ formatDate(user.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">
                <button
                  @click="editUser(user)"
                  class="text-blue-600 hover:text-blue-900 mr-4"
                >
                  Modifier
                </button>
                <button
                  v-if="user.id !== currentUserId"
                  @click="deleteUserConfirm(user)"
                  class="text-red-600 hover:text-red-900"
                >
                  Supprimer
                </button>
                <span v-else class="text-gray-400">Supprimer</span>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="users.length === 0" class="text-center py-12">
          <p class="text-gray-500">Aucun utilisateur trouvé</p>
        </div>
      </div>
    </div>

    <!-- Add/Edit User Modal -->
    <div v-if="showAddUserModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-lg p-6 w-full max-w-md">
        <h2 class="text-2xl font-bold mb-4">
          {{ editingUser ? 'Modifier l\'utilisateur' : 'Ajouter un utilisateur' }}
        </h2>

        <form @submit.prevent="saveUser" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nom d'utilisateur</label>
            <input
              v-model="formData.username"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              v-model="formData.email"
              type="email"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div v-if="!editingUser">
            <label class="block text-sm font-medium text-gray-700 mb-1">Mot de passe</label>
            <input
              v-model="formData.password"
              type="password"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Rôle</label>
            <select
              v-model="formData.role"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="user">Utilisateur</option>
              <option value="admin">Administrateur</option>
            </select>
          </div>

          <div class="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              @click="closedModal"
              class="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Annuler
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              {{ editingUser ? 'Mettre à jour' : 'Créer' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirmModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-lg p-6 w-full max-w-md">
        <h2 class="text-2xl font-bold mb-4">Confirmer la suppression</h2>
        <p class="text-gray-600 mb-6">
          Êtes-vous sûr de vouloir supprimer l'utilisateur <strong>{{ userToDelete?.username }}</strong> ?
          Cette action est irréversible.
        </p>

        <div class="flex justify-end space-x-3">
          <button
            @click="showDeleteConfirmModal = false"
            class="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
          >
            Annuler
          </button>
          <button
            @click="deleteUser"
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
          >
            Supprimer
          </button>
        </div>
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
const users = ref([])
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const showAddUserModal = ref(false)
const showDeleteConfirmModal = ref(false)
const editingUser = ref(null)
const userToDelete = ref(null)

const currentUserId = computed(() => authStore.user?.id)

const formData = ref({
  username: '',
  email: '',
  password: '',
  role: 'user'
})

onMounted(() => {
  authStore.loadUser()
  fetchUsers()
})

const fetchUsers = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const data = await adminService.getUsers()
    console.log('Users received:', data)
    users.value = data
  } catch (error) {
    console.error('Fetch error:', error)
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

const editUser = (user) => {
  editingUser.value = user
  formData.value = {
    username: user.username,
    email: user.email,
    password: '',
    role: user.role
  }
  showAddUserModal.value = true
}

const closedModal = () => {
  showAddUserModal.value = false
  editingUser.value = null
  resetForm()
}

const resetForm = () => {
  formData.value = {
    username: '',
    email: '',
    password: '',
    role: 'user'
  }
}

const saveUser = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  try {
    if (editingUser.value) {
      // Update user
      await adminService.updateUser(editingUser.value.id, {
        username: formData.value.username,
        email: formData.value.email,
        role: formData.value.role
      })
      successMessage.value = 'Utilisateur mis à jour avec succès'
    } else {
      // Create user
      await adminService.createUser(
        formData.value.username,
        formData.value.email,
        formData.value.password
      )
      successMessage.value = 'Utilisateur créé avec succès'
    }

    closedModal()
    fetchUsers()

    // Clear success message after 3 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    errorMessage.value = error.message
  }
}

const deleteUserConfirm = (user) => {
  userToDelete.value = user
  showDeleteConfirmModal.value = true
}

const deleteUser = async () => {
  if (!userToDelete.value) return

  errorMessage.value = ''
  successMessage.value = ''

  try {
    await adminService.deleteUser(userToDelete.value.id)
    successMessage.value = 'Utilisateur supprimé avec succès'
    showDeleteConfirmModal.value = false
    userToDelete.value = null
    fetchUsers()

    // Clear success message after 3 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    errorMessage.value = error.message
  }
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>
