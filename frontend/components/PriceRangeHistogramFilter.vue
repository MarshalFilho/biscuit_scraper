<template>
  <div class="price-histogram-filter">
    <div class="filter-header">
      <h4>Faixa de Preço (R$)</h4>
      <div class="price-display">
        R$ {{ minVal }} - R$ {{ maxVal === absoluteMax ? maxVal + '+' : maxVal }}
      </div>
    </div>
    
    <div class="histogram-container">
      <apexchart 
        v-if="isMounted && series[0].data.length > 0" 
        type="bar" 
        height="80" 
        :options="chartOptions" 
        :series="series"
      ></apexchart>
      
      <!-- Dual Range Slider Customizado -->
      <div class="range-slider-wrapper">
        <input 
          type="range" 
          :min="absoluteMin" 
          :max="absoluteMax" 
          v-model.number="minVal" 
          @input="onMinInput" 
          @change="onSliderChange"
          class="range-input min-range"
        />
        <input 
          type="range" 
          :min="absoluteMin" 
          :max="absoluteMax" 
          v-model.number="maxVal" 
          @input="onMaxInput" 
          @change="onSliderChange"
          class="range-input max-range"
        />
        <!-- Pista visual (Track) entre os thumbs -->
        <div class="range-track-highlight" :style="trackStyle"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] }
})

const emit = defineEmits(['filter'])

const isMounted = ref(false)
onMounted(() => { isMounted.value = true })

// Configuração do Range
const absoluteMin = ref(0)
const absoluteMax = ref(300)
const minVal = ref(0)
const maxVal = ref(300)

const BUCKET_SIZE = 10 // Agrupar a cada R$ 10

const histogramData = computed(() => {
  if (!props.items || props.items.length === 0) return []
  
  // Encontra o preço máximo arredondado para cima
  const maxPriceInItems = Math.max(...props.items.map(i => i.preco || 0))
  absoluteMax.value = Math.min(Math.ceil(maxPriceInItems / 50) * 50, 1000) // Limite seguro
  
  if (maxVal.value > absoluteMax.value) maxVal.value = absoluteMax.value
  
  const buckets = {}
  const totalBuckets = Math.ceil(absoluteMax.value / BUCKET_SIZE)
  
  for (let i = 0; i < totalBuckets; i++) {
    buckets[i * BUCKET_SIZE] = 0
  }
  
  for (const item of props.items) {
    if (item.preco > 0) {
      const bucketIndex = Math.floor(item.preco / BUCKET_SIZE) * BUCKET_SIZE
      if (buckets[bucketIndex] !== undefined) {
        buckets[bucketIndex] += (item.vendas_totais || 1) // Soma volume de vendas
      } else if (bucketIndex > absoluteMax.value) {
        // Agrupa tudo que passar do máximo no último bucket
        const lastBucket = (totalBuckets - 1) * BUCKET_SIZE
        if (buckets[lastBucket] !== undefined) {
          buckets[lastBucket] += (item.vendas_totais || 1)
        }
      }
    }
  }
  
  return Object.keys(buckets).sort((a,b) => Number(a) - Number(b)).map(k => buckets[k])
})

const series = computed(() => [{
  name: 'Volume de Vendas',
  data: histogramData.value
}])

const chartOptions = computed(() => {
  return {
    chart: {
      type: 'bar',
      toolbar: { show: false },
      sparkline: { enabled: true },
      animations: { enabled: false }
    },
    plotOptions: {
      bar: { columnWidth: '90%', borderRadius: 2 }
    },
    colors: [function({ value, dataPointIndex }) {
      const bucketPrice = dataPointIndex * BUCKET_SIZE
      if (bucketPrice >= minVal.value && bucketPrice <= maxVal.value) {
        return '#38bdf8' // Cor ativa (Azul vibrante)
      }
      return '#334155' // Cor inativa (Cinza escuro)
    }],
    tooltip: {
      fixed: { enabled: false },
      x: { show: false },
      y: { title: { formatter: function (seriesName) { return '' } } },
      marker: { show: false }
    }
  }
})

// Estilo dinâmico para a "pista" entre os dois thumbs
const trackStyle = computed(() => {
  const minPercent = ((minVal.value - absoluteMin.value) / (absoluteMax.value - absoluteMin.value)) * 100
  const maxPercent = ((maxVal.value - absoluteMin.value) / (absoluteMax.value - absoluteMin.value)) * 100
  return {
    left: `${minPercent}%`,
    width: `${maxPercent - minPercent}%`
  }
})

function onMinInput() {
  if (minVal.value >= maxVal.value) {
    minVal.value = maxVal.value - 1
  }
}

function onMaxInput() {
  if (maxVal.value <= minVal.value) {
    maxVal.value = minVal.value + 1
  }
}

function onSliderChange() {
  emit('filter', { min: minVal.value, max: maxVal.value })
}
</script>

<style scoped>
.price-histogram-filter {
  background: rgba(30, 41, 59, 0.4);
  border: 1px solid var(--border-glass);
  border-radius: 12px;
  padding: 1rem 1.2rem;
  margin-bottom: 1.5rem;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: -15px; /* Puxa o gráfico pra cima */
  z-index: 10;
  position: relative;
}

.filter-header h4 {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.price-display {
  font-weight: 700;
  color: #38bdf8;
  font-size: 0.95rem;
}

.histogram-container {
  position: relative;
  height: 100px;
  padding-top: 20px;
}

.range-slider-wrapper {
  position: absolute;
  bottom: 5px;
  width: 100%;
  height: 24px;
}

.range-input {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  position: absolute;
  pointer-events: none;
  background: transparent;
  height: 4px;
  top: 50%;
  transform: translateY(-50%);
  margin: 0;
  z-index: 20;
}

/* Base invisible track */
.range-input::-webkit-slider-runnable-track {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

/* Thumbs */
.range-input::-webkit-slider-thumb {
  -webkit-appearance: none;
  pointer-events: auto;
  height: 18px;
  width: 18px;
  border-radius: 50%;
  background: #38bdf8;
  cursor: grab;
  margin-top: -7px;
  border: 2px solid #0f172a;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
  transition: transform 0.1s;
}

.range-input::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.range-input::-webkit-slider-thumb:active {
  cursor: grabbing;
}

/* Pista de destaque entre os thumbs */
.range-track-highlight {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  height: 4px;
  background: #38bdf8;
  border-radius: 4px;
  z-index: 15;
  pointer-events: none;
}
</style>
