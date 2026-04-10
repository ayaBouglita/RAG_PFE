<template>
  <div v-if="chartConfig" class="w-full bg-white rounded-lg shadow-md p-6 mb-4">
    <!-- Header -->
    <div class="mb-4">
      <h3 class="text-lg font-semibold text-primary-600">📊 {{ chartConfig.title }}</h3>
      <p class="text-sm text-gray-600">Unité: {{ chartConfig.unit || "N/A" }}</p>
    </div>

    <!-- Chart -->
    <div class="mb-6 h-80 relative">
      <canvas ref="chartCanvas"></canvas>
    </div>

    <!-- Statistiques -->
    <div v-if="chartConfig.statistics && Object.keys(chartConfig.statistics).length > 0" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div v-for="(stats, metric) in chartConfig.statistics" :key="metric" class="bg-gray-50 p-4 rounded-lg">
        <h4 class="text-xs font-semibold text-gray-600 uppercase">{{ metric }}</h4>
        <p class="text-lg font-bold text-primary-600">{{ formatNumber(stats.total) }}</p>
        <p class="text-xs text-gray-500">Avg: {{ formatNumber(stats.moyenne) }}</p>
      </div>
    </div>

    <!-- Actions -->
    <div class="mt-4 flex gap-2">
      <button
        @click="downloadChart"
        class="px-3 py-2 text-sm bg-accent-500 hover:bg-accent-400 text-white rounded-lg transition-colors"
      >
        ⬇️ Télécharger
      </button>
      <button
        @click="copyToClipboard"
        class="px-3 py-2 text-sm bg-primary-400 hover:bg-primary-500 text-white rounded-lg transition-colors"
      >
        📋 Copier données
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  chartConfig: {
    type: Object,
    default: null
  }
})

const chartCanvas = ref(null)
let chartInstance = null

onMounted(() => {
  if (props.chartConfig) {
    createChart()
  }
})

watch(
  () => props.chartConfig,
  (newConfig) => {
    if (newConfig) {
      if (chartInstance) {
        chartInstance.destroy()
      }
      createChart()
    }
  },
  { deep: true }
)

const createChart = () => {
  if (!chartCanvas.value || !props.chartConfig) return

  const ctx = chartCanvas.value.getContext('2d')
  const config = props.chartConfig

  const chartOptions = {
    type: config.type,
    data: config.data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        title: {
          display: true,
          text: config.title,
          font: {
            size: 14,
            weight: 'bold'
          }
        }
      },
      ...config.options
    }
  }

  chartInstance = new Chart(ctx, chartOptions)
}

const formatNumber = (num) => {
  if (typeof num !== 'number') return num
  return new Intl.NumberFormat('fr-FR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(num)
}

const downloadChart = () => {
  if (chartInstance) {
    const image = chartInstance.toBase64Image()
    const link = document.createElement('a')
    link.href = image
    link.download = `chart-${Date.now()}.png`
    link.click()
  }
}

const copyToClipboard = () => {
  if (props.chartConfig) {
    const json = JSON.stringify(props.chartConfig.data)
    navigator.clipboard.writeText(json).then(() => {
      alert('Données copiées!')
    })
  }
}
</script>

<style scoped>
canvas {
  max-height: 100%;
}
</style>
