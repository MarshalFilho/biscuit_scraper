<template>
  <div class="mini-price-slider">
    <div class="slider-top">
      <span class="label">{{ t('filters.price_range', 'Faixa de Preço:') }}</span>
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

const NUM_BUCKETS = 28 // 28 barras minimalistas e fluidas

watch(() => props.items, (newItems) => {
  if (!newItems || newItems.length === 0) return
  
  const validPrices = newItems.map(i => i.preco).filter(p => typeof p === 'number' && p > 0)
  if (validPrices.length === 0) return
  
  const maxP = Math.max(...validPrices)
  const calculatedMax = Math.ceil(maxP / 10) * 10 || 300
  absoluteMax.value = calculatedMax
  
  if (!isInitialized.value) {
    minVal.value = 0
    maxVal.value = calculatedMax
    isInitialized.value = true
  } else if (maxVal.value > calculatedMax) {
    maxVal.value = calculatedMax
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
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  padding: 0.6rem 0.9rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.slider-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
}

.label {
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-size: 0.72rem;
}

.price-val {
  font-weight: 800;
  color: #2563eb;
  font-size: 0.84rem;
}

.bars-container {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  height: 28px;
  padding: 0 4px;
}

.mini-bar {
  flex: 1;
  background: #e2e8f0;
  border-radius: 2px 2px 0 0;
  transition: all 0.15s ease;
  min-height: 3px;
}

.mini-bar.active {
  background: #3b82f6;
}

.range-wrapper {
  position: relative;
  height: 14px;
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
  height: 14px;
  width: 14px;
  border-radius: 50%;
  background: #2563eb;
  cursor: grab;
  margin-top: -5.5px;
  border: 2px solid #ffffff;
  box-shadow: 0 1px 4px rgba(37, 99, 235, 0.4);
  transition: transform 0.1s;
}

.slider-thumb::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.slider-thumb::-webkit-slider-thumb:active {
  cursor: grabbing;
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
