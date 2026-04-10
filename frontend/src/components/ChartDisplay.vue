<template>
  <div v-if="chartConfig" class="w-full bg-white rounded-lg shadow-md p-6 mb-4">
    <!-- Header -->
    <div class="mb-4">
      <h3 class="text-lg font-semibold text-primary-600">📊 {{ chartConfig.title }}</h3>
      <p class="text-sm text-primary-500">Unité: {{ chartConfig.unit || "N/A" }}</p>
    </div>

    <!-- Chart -->
    <div class="mb-6 relative bg-gray-50 p-4 rounded-lg" style="height: 400px;">
      <canvas 
        ref="chartCanvas"
        style="display: block; width: 100% !important; height: 100% !important;"
      ></canvas>
    </div>

    <!-- Statistiques -->
    <div v-if="chartConfig.statistics && Object.keys(chartConfig.statistics).length > 0" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div v-for="(stats, metric) in chartConfig.statistics" :key="metric" class="bg-primary-50 p-4 rounded-lg border-l-4 border-accent-500">
        <h4 class="text-xs font-semibold text-primary-600 uppercase">{{ translateMetric(metric) }}</h4>
        <p class="text-lg font-bold text-accent-500">{{ formatNumber(stats.total) }}</p>
        <p class="text-xs text-primary-500">Moy: {{ formatNumber(stats.moyenne) }}</p>
        <p class="text-xs text-primary-400 mt-1">Min: {{ formatNumber(stats.min) }} / Max: {{ formatNumber(stats.max) }}</p>
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
import { ref, onMounted, watch, nextTick } from 'vue'
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
  if (!chartCanvas.value || !props.chartConfig) {
    console.error('❌ Canvas ou config manquant')
    return
  }

  // Attendre que le DOM soit rendu
  nextTick(() => {
    try {
      const canvas = chartCanvas.value
      if (!canvas) return

      // Vérifier les dimensions
      const rect = canvas.parentElement.getBoundingClientRect()
      console.log('📏 Canvas parent dimensions:', { width: rect.width, height: rect.height })

      const ctx = canvas.getContext('2d')
      if (!ctx) {
        console.error('❌ Impossible d\'obtenir le contexte 2D')
        return
      }

      const config = props.chartConfig
      console.log('📊 Chart config reçu:', {
        type: config.type,
        dataLabels: config.data?.labels?.length,
        datasets: config.data?.datasets?.length
      })

      const mergedPlugins = {
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
        },
        ...(config.options?.plugins || {})
      }

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
          plugins: mergedPlugins,
          ...(config.options ? Object.fromEntries(
            Object.entries(config.options).filter(([key]) => key !== 'plugins')
          ) : {})
        }
      }

      console.log('✅ Création du graphique avec type:', config.type)
      if (chartInstance) {
        chartInstance.destroy()
      }
      chartInstance = new Chart(ctx, chartOptions)
      console.log('✅ Graphique créé avec succès!')
    } catch (error) {
      console.error('❌ Erreur lors de la création du graphique:', error)
    }
  })
}

const formatNumber = (num) => {
  if (typeof num !== 'number') return num
  return new Intl.NumberFormat('fr-FR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(num)
}

const translateMetric = (metric) => {
  const translations = {
    'total': 'Total',
    'moyenne': 'Moyenne',
    'min': 'Minimum',
    'max': 'Maximum',
    'average': 'Moyenne',
    'items': 'Éléments',
    'consommation': 'Consommation',
    'sum': 'Somme'
  }
  return translations[metric.toLowerCase()] || metric
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
