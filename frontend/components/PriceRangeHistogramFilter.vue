<template>
  <div class="mini-price-slider">
    <div class="slider-top">
      <span class="label">
        <SlidersHorizontal :size="12" class="inline-icon" />
        {{ t('filters.price_range', 'Faixa de Preço:') }}
      </span>
      <span class="price-val">
        R$ {{ minVal }} — {{ maxVal >= MAX_PRICE_CAP ? 'R$ ' + MAX_PRICE_CAP + '+' : 'R$ ' + maxVal }}
      </span>
    </div>
    
    <!-- Histograma com Eixo Y e Barras -->
    <div class="histogram-body">
      <!-- Eixo Y Discreto -->
      <div class="y-axis">
        <span class="y-tick">{{ maxVolumeLabel }}</span>
        <span class="y-tick">0</span>
      </div>

      <!-- Mini Histograma de Barras com Escala Suavizada -->
      <div class="bars-container">
        <div 
          v-for="(bucket, idx) in bucketList" 
          :key="idx" 
          class="mini-bar"
          :class="{ active: isBucketActive(bucket) }"
          :style="{ height: Math.max(bucket.heightPerc, 10) + '%' }"
          :title="getBucketTooltip(bucket)"
        ></div>
      </div>
    </div>

    <!-- Dual Range Inputs Sobrepostos -->
    <div class="range-wrapper">
      <input 
        type="range" 
        :min="absoluteMin" 
        :max="MAX_PRICE_CAP" 
        :step="stepSize"
        v-model.number="minVal" 
        @input="onMinInput" 
        @change="onSliderChange"
        class="slider-thumb min-thumb"
      />
      <input 
        type="range" 
        :min="absoluteMin" 
        :max="MAX_PRICE_CAP" 
        :step="stepSize"
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

// Teto fixo para evitar que produtos de 2.000 ou 5.000 reais quebrem a escala
const MAX_PRICE_CAP = 500
const absoluteMin = ref(0)
const absoluteMax = ref(MAX_PRICE_CAP)
const minVal = ref(0)
const maxVal = ref(MAX_PRICE_CAP)
const stepSize = ref(5)
const isInitialized = ref(false)

const NUM_BUCKETS = 20

watch(() => props.items, (newItems) => {
  if (!newItems || newItems.length === 0) return
  
  if (!isInitialized.value) {
    minVal.value = 0
    maxVal.value = MAX_PRICE_CAP
    isInitialized.value = true
  }
}, { immediate: true })

const bucketList = computed(() => {
  if (!props.items || props.items.length === 0) return []

  const minRange = 0
  const maxRange = MAX_PRICE_CAP
  const bucketWidth = maxRange / NUM_BUCKETS // Cada bucket tem R$ 25 de largura

  const buckets = Array.from({ length: NUM_BUCKETS }, (_, i) => {
    const pMin = Math.round(i * bucketWidth)
    const pMax = Math.round((i + 1) * bucketWidth)
    return {
      priceMin: pMin,
      priceMax: pMax,
      isLast: i === NUM_BUCKETS - 1,
      count: 0,
      volume: 0,
      scaledScore: 0,
      heightPerc: 10
    }
  })

  for (const item of props.items) {
    const price = item.preco || 0
    if (price > 0) {
      // Se for maior ou igual a 500, cai no último bucket (500+)
      const idx = Math.min(Math.floor(price / bucketWidth), NUM_BUCKETS - 1)
      if (idx >= 0 && buckets[idx]) {
        const sales = item.vendas_totais || 0
        buckets[idx].count += 1
        buckets[idx].volume += sales
      }
    }
  }

  // Escala balanceada e suavizada
  let maxScore = 1
  for (const b of buckets) {
    if (b.count > 0) {
      const volWeight = b.volume > 0 ? Math.sqrt(b.volume) : 0
      const countWeight = b.count * 6
      b.scaledScore = volWeight + countWeight
      if (b.scaledScore > maxScore) {
        maxScore = b.scaledScore
      }
    }
  }

  return buckets.map(b => {
    let height = 0
    if (b.scaledScore > 0) {
      height = Math.round((b.scaledScore / maxScore) * 88) + 12
    }
    return {
      ...b,
      heightPerc: height
    }
  })
})

function isBucketActive(bucket) {
  if (maxVal.value >= MAX_PRICE_CAP) {
    return bucket.priceMax >= minVal.value
  }
  return bucket.priceMax >= minVal.value && bucket.priceMin <= maxVal.value
}

function getBucketTooltip(bucket) {
  const rangeLabel = bucket.isLast 
    ? `R$ ${bucket.priceMin} a R$ 500+` 
    : `R$ ${bucket.priceMin} a R$ ${bucket.priceMax}`
  return `${rangeLabel}: ${bucket.count} produtos (${bucket.volume.toLocaleString('pt-BR')} vendas)`
}

const maxVolumeLabel = computed(() => {
  const maxVol = Math.max(...bucketList.value.map(b => b.volume), 0)
  if (maxVol >= 1000) return `${(maxVol / 1000).toFixed(0)}k`
  return String(maxVol)
})

const trackStyle = computed(() => {
  const range = MAX_PRICE_CAP - absoluteMin.value || 1
  const minPercent = ((minVal.value - absoluteMin.value) / range) * 100
  const maxPercent = ((maxVal.value - absoluteMin.value) / range) * 100
  return {
    left: `${Math.max(0, Math.min(minPercent, 100))}%`,
    width: `${Math.max(0, Math.min(maxPercent - minPercent, 100))}%`
  }
})

function onMinInput() {
  if (minVal.value >= maxVal.value) {
    minVal.value = maxVal.value - stepSize.value
  }
}

function onMaxInput() {
  if (maxVal.value <= minVal.value) {
    maxVal.value = minVal.value + stepSize.value
  }
}

function onSliderChange() {
  const minFilter = minVal.value <= 0 ? null : minVal.value
  // Se estiver no topo (500+), não filtra preço máximo para incluir todos os produtos acima
  const maxFilter = maxVal.value >= MAX_PRICE_CAP ? null : maxVal.value
  emit('filter', { min: minFilter, max: maxFilter })
}
</script>

<style scoped>
.mini-price-slider {
  background: #f8fafc;
  border: 1.5px solid #cbd5e1;
  border-radius: 11px;
  padding: 0.4rem 0.75rem 0.35rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  width: 100%;
  min-width: 235px;
  max-width: 290px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

@media (max-width: 768px) {
  .mini-price-slider {
    min-width: 100%;
    max-width: 100%;
    padding: 0.5rem 0.8rem 0.45rem 0.8rem;
  }
}

.slider-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
}

.label {
  font-weight: 700;
  color: #475569;
  font-size: 0.74rem;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.price-val {
  font-weight: 800;
  color: #2563eb;
  font-size: 0.78rem;
}

.histogram-body {
  display: flex;
  align-items: flex-end;
  gap: 5px;
  height: 26px;
  margin-top: 2px;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
  padding-right: 3px;
  border-right: 1px solid #cbd5e1;
}

.y-tick {
  font-size: 0.58rem;
  font-weight: 700;
  color: #94a3b8;
  line-height: 1;
}

.bars-container {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  flex: 1;
  height: 100%;
  padding: 0 1px;
}

.mini-bar {
  flex: 1;
  background: #cbd5e1;
  border-radius: 2px 2px 0 0;
  transition: all 0.15s ease;
  min-height: 3px;
}

.mini-bar.active {
  background: #2563eb;
}

.mini-bar:hover {
  filter: brightness(0.9);
  transform: scaleY(1.05);
}

.range-wrapper {
  position: relative;
  height: 12px;
  display: flex;
  align-items: center;
  margin-top: 1px;
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
  box-shadow: 0 1px 3px rgba(37, 99, 235, 0.45);
  transition: transform 0.1s;
}

.slider-thumb::-webkit-slider-thumb:hover {
  transform: scale(1.25);
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
