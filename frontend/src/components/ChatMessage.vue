<template>
  <div class="flex-col">
    <!-- User Message -->
    <div v-if="isUser" class="flex justify-end mb-4">
      <div class="bg-primary-500 text-white rounded-lg rounded-br-none p-4 max-w-xs lg:max-w-md break-words">
        {{ message.content }}
      </div>
    </div>

    <!-- Assistant Message -->
    <div v-else class="flex justify-start mb-4">
      <div class="bg-gray-200 text-gray-900 rounded-lg rounded-bl-none p-4 max-w-xs lg:max-w-md break-words">
        {{ message.content }}
        <div v-if="message.sql_query" class="mt-3 pt-3 border-t border-gray-400">
          <details class="cursor-pointer">
            <summary class="text-xs font-mono text-gray-600 hover:text-gray-800">
              📊 SQL Query
            </summary>
            <div class="mt-2 bg-gray-300 p-2 rounded text-xs font-mono overflow-auto max-h-32">
              {{ message.sql_query }}
            </div>
          </details>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  message: Object,
  isUser: Boolean
})
</script>
