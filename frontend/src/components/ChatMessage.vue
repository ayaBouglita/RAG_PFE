<template>
  <div class="flex-col">
    <!-- User Message -->
    <div v-if="isUser" class="flex justify-end mb-4">
      <div class="bg-primary-500 text-white rounded-lg rounded-br-none p-4 max-w-xs lg:max-w-md break-words">
        {{ message.content }}
      </div>
    </div>

    <!-- Assistant Message -->
    <div v-else class="flex flex-col justify-start mb-4">
      <!-- Response Text -->
      <div class="bg-gray-100 text-gray-900 rounded-lg rounded-bl-none p-4 max-w-2xl break-words">
        {{ message.content }}
        
        <!-- SQL Query -->
        <div v-if="message.sql_query" class="mt-3 pt-3 border-t border-gray-300">
          <details class="cursor-pointer">
            <summary class="text-xs font-mono text-gray-600 hover:text-gray-800 font-semibold">
              📊 SQL Query
            </summary>
            <div class="mt-2 bg-gray-200 p-2 rounded text-xs font-mono overflow-auto max-h-32 border border-gray-300">
              {{ message.sql_query }}
            </div>
          </details>
        </div>
      </div>

      <!-- Chart (if available) -->
      <ChartDisplay v-if="message.chart_config" :chart-config="message.chart_config" class="mt-4 max-w-2xl" />
    </div>
  </div>
</template>

<script setup>
import ChartDisplay from './ChartDisplay.vue'

defineProps({
  message: Object,
  isUser: Boolean
})
</script>
