<template>
  <div class="mini-price-slider">
    <div class="slider-top">
      <span class="label">
        <SlidersHorizontal :size="13" class="inline-icon" />
        {{ t('filters.price_range', 'Faixa de Preço:') }}
      </span>
      <span class="price-val">R$ {{ minVal }} — R$ {{ maxVal === absoluteMax ? maxVal + '+' : maxVal }}</span>
    </div>
    
    <!-- Mini Histograma de Barras CSS (Clean & Instantâneo) -->
    <div class="bars-container">
      <div 
        v-for="(bucket, idx) in bucketList" 
        :key="idx" 
        class="mini-bar"
        :class="{ active: bucket.price >= minVal && bucket.price <= maxVal }"
        :style="{ height: Math.max(bucket.heightPerc, 12) + '%' }"
        :title="`R$ ${bucket.price}: ${bucket.volume} ${t('kpis.sales_suffix', 'vendas')}`"
      ></div>
    </div>

    <!-- Dual Range Inputs Sobrepostos -->
    <div class="range-wrapper">
      <input 
        type="range" 
        :min="absoluteMin" 
        :max="absoluteMax" 
        v-model.number="minVal" 
        @input="onMinInput" 
        @change="onSliderChange"
        class="slider-thumb min-thumb"
      />
      <input 
        type="range" 
        :min="absoluteMin" 
        :max="absoluteMax" 
        v-model.number="maxVal" 
        @input="onMaxInput" 
        @change="onSliderChange"
        class="slider-thumb max-thumb"
      />
      <div class="slider-track-highlight" :style="trackStyle"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { SlidersHorizontal } from 'lucide-vue-next'
import { useAppI18n } from '~/composables/useAppI18n'

const { t } = useAppI18n()

const props = defineProps({
  items: { type: Array, default: () => [] }
})

const emit = defineEmits(['filter'])

const absoluteMin = ref(0)
const absoluteMax = ref(300)
const minVal = ref(0)
const maxVal = ref(300)
const isInitialized = ref(false)

const NUM_BUCKETS = 24

watch(() => props.items, (newItems) => {
  if (!newItems || newItems.length === 0) return
  
  const validPrices = newItems.map(i => i.preco).filter(p => typeof p === 'number' && p > 0).sort((a, b) => a - b)
  if (validPrices.length === 0) return
  
  const minP = validPrices[0]
  const p95Idx = Math.min(Math.floor(validPrices.length * 0.95), validPrices.length - 1)
  const maxP = Math.max(validPrices[p95Idx], minP + 10)

  const calcMin = minP < 40 ? 0 : Math.floor(minP / 10) * 10
  const calcMax = Math.ceil(maxP / 10) * 10 || 300

  absoluteMin.value = calcMin
  absoluteMax.value = calcMax
  
  if (!isInitialized.value) {
    minVal.value = calcMin
    maxVal.value = calcMax
    isInitialized.value = true
  } else {
    if (minVal.value < calcMin) minVal.value = calcMin
    if (maxVal.value > calcMax) maxVal.value = calcMax
  }
}, { immediate: true })

const bucketList = computed(() => {
  if (!props.items || props.items.length === 0) return []

  const step = (absoluteMax.value - absoluteMin.value) / NUM_BUCKETS || 10
  const buckets = Array.from({ length: NUM_BUCKETS }, (_, i) => ({
    price: Math.round(absoluteMin.value + (i * step)),
    volume: 0,
    heightPerc: 10
  }))

  let maxVol = 1
  for (const item of props.items) {
    if (item.preco > 0) {
      const idx = Math.min(Math.floor((item.preco - absoluteMin.value) / step), NUM_BUCKETS - 1)
      if (idx >= 0 && buckets[idx]) {
        const sales = item.vendas_totais || 1
        buckets[idx].volume += sales
        if (buckets[idx].volume > maxVol) {
          maxVol = buckets[idx].volume
        }
      }
    }
  }

  return buckets.map(b => ({
    ...b,
    heightPerc: Math.round((b.volume / maxVol) * 100)
  }))
})

const trackStyle = computed(() => {
  const range = absoluteMax.value - absoluteMin.value || 1
  const minPercent = ((minVal.value - absoluteMin.value) / range) * 100
  const maxPercent = ((maxVal.value - absoluteMin.value) / range) * 100
  return {
    left: `${Math.max(0, Math.min(minPercent, 100))}%`,
    width: `${Math.max(0, Math.min(maxPercent - minPercent, 100))}%`
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
.mini-price-slider {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  padding: 0.5rem 0.8rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  max-width: 480px;
}

.slider-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.78rem;
}

.label {
  font-weight: 700;
  color: #475569;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.price-val {
  font-weight: 800;
  color: #2563eb;
  font-size: 0.82rem;
}

.bars-container {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 20px;
  padding: 0 2px;
}

.mini-bar {
  flex: 1;
  background: #cbd5e1;
  border-radius: 2px 2px 0 0;
  transition: all 0.15s ease;
  min-height: 2px;
}

.mini-bar.active {
  background: #2563eb;
}

.range-wrapper {
  position: relative;
  height: 12px;
  display: flex;
  align-items: center;
}

.slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  position: absolute;
  pointer-events: none;
  background: transparent;
  height: 3px;
  margin: 0;
  z-index: 20;
  left: 0;
}

.slider-thumb::-webkit-slider-runnable-track {
  width: 100%;
  height: 3px;
  background: #e2e8f0;
  border-radius: 99px;
}

.slider-thumb::-webkit-slider-thumb {
  -webkit-appearance: none;
  pointer-events: auto;
  height: 12px;
  width: 12px;
  border-radius: 50%;
  background: #2563eb;
  cursor: grab;
  margin-top: -4.5px;
  border: 2px solid #ffffff;
  box-shadow: 0 1px 3px rgba(37, 99, 235, 0.4);
  transition: transform 0.1s;
}

.slider-thumb::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.slider-track-highlight {
  position: absolute;
  height: 3px;
  background: #2563eb;
  border-radius: 99px;
  z-index: 15;
  pointer-events: none;
}
</style>
