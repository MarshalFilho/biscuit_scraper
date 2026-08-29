<template>
  <div class="timeline-bar-wrapper animate-fade-in">
    <div class="timeline-range-bar">
      <!-- 1. Título & Ícone da Barra -->
      <div class="bar-brand-section">
        <div class="bar-icon-pill">
          <span>📈</span>
        </div>
        <div class="bar-title-wrap">
          <div class="title-with-badge">
            <h4>{{ t('timeline.range_title', 'Comparador de Evolução Histórica') }}</h4>
            <span class="range-badge-pulse">{{ t('timeline.growth_badge', 'Análise de Crescimento') }}</span>
          </div>
          <p class="bar-desc">{{ t('timeline.range_desc', 'Selecione a data inicial e final para comparar oscilação de preços, vendas acumuladas e tendências:') }}</p>
        </div>
      </div>

      <!-- 2. Seletores de Data: Data Inicial (De) ➔ Data Final (Até) -->
      <div class="bar-selectors-section">
        <div class="date-picker-box box-start">
          <span class="picker-label">
            <span class="dot-indicator dot-start"></span>
            {{ t('timeline.from_date', 'De (Data Inicial):') }}
          </span>
          <div class="select-wrapper">
            <select v-model="selectedStartDate" @change="onStartDateChange" class="range-select" :disabled="availableDates.length === 0">
              <option v-for="d in availableDates" :key="'start-' + d.dateStr" :value="d.dateStr">
                {{ d.labelFull }} ({{ d.count }} {{ t('timeline.items', 'itens') }})
              </option>
            </select>
          </div>
        </div>

        <div class="range-arrow-indicator" :title="t('timeline.range_arrow_tooltip', 'Comparando período')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M5 12H19M19 12L13 6M19 12L13 18" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>

        <div class="date-picker-box box-end">
          <span class="picker-label">
            <span class="dot-indicator dot-end"></span>
            {{ t('timeline.to_date', 'Até (Data Final):') }}
          </span>
          <div class="select-wrapper">
            <select v-model="selectedEndDate" @change="onEndDateChange" class="range-select" :disabled="availableDates.length === 0">
              <option v-for="d in availableDates" :key="'end-' + d.dateStr" :value="d.dateStr">
                {{ d.labelFull }} ({{ d.count }} {{ t('timeline.items', 'itens') }})
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- 3. Atalhos Rápidos (Presets) -->
      <div class="bar-presets-section">
        <span class="presets-label">{{ t('timeline.presets', 'Atalhos:') }}</span>
        <div class="preset-buttons">
          <button 
            type="button" 
            class="btn-preset" 
            :class="{ active: isPresetActive(7) }"
            @click="applyDaysPreset(7)"
            :title="t('timeline.preset_7_title', 'Comparar evolução dos últimos 7 dias')"
          >
            ⚡ {{ t('timeline.preset_7_days', 'Últimos 7 Dias') }}
          </button>
          <button 
            type="button" 
            class="btn-preset" 
            :class="{ active: isPresetActive(3) }"
            @click="applyDaysPreset(3)"
            :title="t('timeline.preset_3_title', 'Comparar últimos 3 dias')"
          >
            ⚡ {{ t('timeline.preset_3_days', 'Últimos 3 Dias') }}
          </button>
          <button 
            type="button" 
            class="btn-preset" 
            :class="{ active: isAllHistoryActive }"
            @click="applyAllHistoryPreset"
            :title="t('timeline.preset_all_title', 'Comparar todo o histórico coletado')"
          >
            🌐 {{ t('timeline.preset_all', 'Todo o Período') }}
          </button>
          <button 
            type="button" 
            class="btn-preset" 
            :class="{ active: isSingleDayActive }"
            @click="applySingleDayPreset"
            :title="t('timeline.preset_latest_title', 'Ver apenas a última coleta')"
          >
            📸 {{ t('timeline.preset_latest', 'Última Coleta') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 4. Barra Informativa de Status da Comparação -->
    <div v-if="selectedStartDate && selectedEndDate" class="comparison-status-strip">
      <div class="status-left">
        <span class="status-icon">📊</span>
        <span class="status-text">
          {{ t('timeline.comparing_text', 'Comparando') }}
          <strong>{{ formatDateBadge(selectedStartDate) }}</strong>
          {{ t('timeline.until_text', 'até') }}
          <strong>{{ formatDateBadge(selectedEndDate) }}</strong>
          <span class="diff-days-pill" v-if="daysDifference > 0">
            ⏳ {{ daysDifference }} {{ daysDifference === 1 ? t('timeline.day_singular', 'dia') : t('timeline.days_plural', 'dias') }} {{ t('timeline.of_evolution', 'de evolução') }}
          </span>
          <span class="diff-days-pill single" v-else>
            📸 {{ t('timeline.single_day_snapshot', 'Retrato de 1 dia') }}
          </span>
        </span>
      </div>
      <div class="status-right" v-if="matchingProductsCount > 0">
        <span class="count-badge">📦 {{ matchingProductsCount }} {{ t('timeline.items_with_history', 'produtos analisados') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useAppI18n } from '~/composables/useAppI18n'

const { t, locale } = useAppI18n()

const props = defineProps({
  rawItems: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false }
})

const emit = defineEmits(['select-date', 'compare-dates'])

const selectedStartDate = ref(null)
const selectedEndDate = ref(null)

// Extrai todas as datas únicas ordenadas da MAIS ANTIGA para a MAIS RECENTE
const availableDates = computed(() => {
  const map = new Map()

  for (const item of props.rawItems) {
    if (item.historico_coletas && Array.isArray(item.historico_coletas)) {
      for (const h of item.historico_coletas) {
        if (h.data_coleta) {
          const dateStr = h.data_coleta.split('T')[0]
          if (!map.has(dateStr)) {
            map.set(dateStr, { dateStr, count: 0 })
          }
          map.get(dateStr).count += 1
        }
      }
    }
  }

  // Ordenadas da MAIS ANTIGA para a MAIS RECENTE
  const sorted = Array.from(map.values()).sort((a, b) => new Date(a.dateStr) - new Date(b.dateStr))

  return sorted.map((d, index) => {
    const isLatest = index === sorted.length - 1
    const dObj = new Date(d.dateStr + 'T00:00:00')
    const formatted = dObj.toLocaleDateString(locale.value === 'pt' ? 'pt-BR' : 'en-US', { day: '2-digit', month: '2-digit', year: 'numeric' })
    const formattedShort = dObj.toLocaleDateString(locale.value === 'pt' ? 'pt-BR' : 'en-US', { day: '2-digit', month: 'short' })
    
    return {
      dateStr: d.dateStr,
      count: d.count,
      labelShort: formattedShort,
      labelFull: isLatest ? `${formatted} (${t('timeline.most_recent', 'Mais recente')})` : formatted
    }
  })
})

const daysDifference = computed(() => {
  if (!selectedStartDate.value || !selectedEndDate.value) return 0
  const start = new Date(selectedStartDate.value + 'T00:00:00')
  const end = new Date(selectedEndDate.value + 'T00:00:00')
  const diffTime = Math.abs(end - start)
  return Math.round(diffTime / (1000 * 60 * 60 * 24))
})

const matchingProductsCount = computed(() => {
  return props.rawItems?.length || 0
})

const isSingleDayActive = computed(() => {
  if (availableDates.value.length === 0) return false
  const latest = availableDates.value[availableDates.value.length - 1].dateStr
  return selectedStartDate.value === latest && selectedEndDate.value === latest
})

const isAllHistoryActive = computed(() => {
  if (availableDates.value.length < 2) return false
  const first = availableDates.value[0].dateStr
  const latest = availableDates.value[availableDates.value.length - 1].dateStr
  return selectedStartDate.value === first && selectedEndDate.value === latest
})

function isPresetActive(days) {
  if (availableDates.value.length < 2) return false
  const latest = availableDates.value[availableDates.value.length - 1].dateStr
  if (selectedEndDate.value !== latest) return false
  return daysDifference.value === days
}

function onStartDateChange() {
  if (new Date(selectedStartDate.value) > new Date(selectedEndDate.value)) {
    // Se a data inicial for maior que a final, ajusta a final para ser igual
    selectedEndDate.value = selectedStartDate.value
  }
  emitCurrentRange()
}

function onEndDateChange() {
  if (new Date(selectedEndDate.value) < new Date(selectedStartDate.value)) {
    // Se a data final for menor que a inicial, ajusta a inicial para ser igual
    selectedStartDate.value = selectedEndDate.value
  }
  emitCurrentRange()
}

function applyDaysPreset(days) {
  if (availableDates.value.length === 0) return
  const latest = availableDates.value[availableDates.value.length - 1].dateStr
  selectedEndDate.value = latest

  const target = new Date(latest + 'T00:00:00')
  target.setDate(target.getDate() - days)

  // Encontra a data mais próxima disponível no array
  let closest = availableDates.value[0].dateStr
  let minDiff = Infinity
  for (const d of availableDates.value) {
    const dTime = new Date(d.dateStr + 'T00:00:00')
    const diff = Math.abs(dTime - target)
    if (diff < minDiff) {
      minDiff = diff
      closest = d.dateStr
    }
  }

  selectedStartDate.value = closest
  emitCurrentRange()
}

function applyAllHistoryPreset() {
  if (availableDates.value.length === 0) return
  selectedStartDate.value = availableDates.value[0].dateStr
  selectedEndDate.value = availableDates.value[availableDates.value.length - 1].dateStr
  emitCurrentRange()
}

function applySingleDayPreset() {
  if (availableDates.value.length === 0) return
  const latest = availableDates.value[availableDates.value.length - 1].dateStr
  selectedStartDate.value = latest
  selectedEndDate.value = latest
  emitCurrentRange()
}

function emitCurrentRange() {
  if (selectedStartDate.value && selectedEndDate.value) {
    if (selectedStartDate.value === selectedEndDate.value) {
      emit('select-date', selectedEndDate.value)
    } else {
      emit('compare-dates', {
        dateA: selectedStartDate.value,
        dateB: selectedEndDate.value
      })
    }
  }
}

function formatDateBadge(dateStr) {
  if (!dateStr) return ''
  const dObj = new Date(dateStr + 'T00:00:00')
  return dObj.toLocaleDateString(locale.value === 'pt' ? 'pt-BR' : 'en-US', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

// Inicialização automática com 7 dias ou todo o período
watch(availableDates, (newDates) => {
  if (newDates.length > 0 && !selectedStartDate.value && !selectedEndDate.value) {
    if (newDates.length >= 2) {
      applyDaysPreset(7)
    } else {
      selectedStartDate.value = newDates[0].dateStr
      selectedEndDate.value = newDates[0].dateStr
      emitCurrentRange()
    }
  }
}, { immediate: true })

onMounted(() => {
  if (availableDates.value.length > 0) {
    if (availableDates.value.length >= 2) {
      applyDaysPreset(7)
    } else {
      selectedStartDate.value = availableDates.value[0].dateStr
      selectedEndDate.value = availableDates.value[0].dateStr
      emitCurrentRange()
    }
  }
})
</script>

<style scoped>
.timeline-bar-wrapper {
  margin-top: 1rem;
  border-top: 1px solid #f1f5f9;
  padding-top: 1rem;
}

.timeline-range-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.25rem;
  flex-wrap: wrap;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 0.85rem 1.15rem;
}

.bar-brand-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 260px;
}

.bar-icon-pill {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.bar-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.title-with-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.title-with-badge h4 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 800;
  color: #0f172a;
}

.range-badge-pulse {
  font-size: 0.68rem;
  font-weight: 700;
  background: #fdf2f8;
  color: #db2777;
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
  border: 1px solid #fbcfe8;
  text-transform: uppercase;
}

.bar-desc {
  margin: 0;
  font-size: 0.76rem;
  color: #64748b;
}

.bar-selectors-section {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.date-picker-box {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.picker-label {
  font-size: 0.74rem;
  font-weight: 700;
  color: #475569;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.dot-indicator {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.dot-start {
  background: #6366f1;
}

.dot-end {
  background: #10b981;
}

.range-select {
  background: #ffffff;
  border: 1.5px solid #cbd5e1;
  border-radius: 9px;
  padding: 0.45rem 0.75rem;
  font-size: 0.84rem;
  font-weight: 700;
  color: #1e293b;
  cursor: pointer;
  outline: none;
  min-width: 175px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.range-select:focus {
  border-color: #d97706;
  box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.15);
}

.range-arrow-indicator {
  color: #94a3b8;
  display: flex;
  align-items: center;
  padding-top: 1rem;
}

.bar-presets-section {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.presets-label {
  font-size: 0.74rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
}

.preset-buttons {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.btn-preset {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #334155;
  padding: 0.38rem 0.75rem;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.btn-preset:hover {
  background: #f1f5f9;
  border-color: #94a3b8;
  transform: translateY(-1px);
}

.btn-preset.active {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
  color: #ffffff;
  border-color: #b45309;
  box-shadow: 0 2px 8px rgba(217, 119, 6, 0.28);
}

.comparison-status-strip {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  background: #fdfbf7;
  border: 1px solid #fed7aa;
  border-radius: 10px;
  padding: 0.55rem 1rem;
  margin-top: 0.65rem;
}

.status-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-icon {
  font-size: 1.05rem;
}

.status-text {
  font-size: 0.82rem;
  color: #78350f;
}

.status-text strong {
  color: #451a03;
  font-weight: 800;
}

.diff-days-pill {
  display: inline-flex;
  align-items: center;
  background: #fff7ed;
  color: #c2410c;
  border: 1px solid #ffedd5;
  padding: 0.15rem 0.55rem;
  border-radius: 99px;
  font-size: 0.72rem;
  font-weight: 800;
  margin-left: 0.4rem;
}

.diff-days-pill.single {
  background: #f0fdf4;
  color: #15803d;
  border-color: #dcfce7;
}

.status-right {
  display: flex;
  align-items: center;
}

.count-badge {
  font-size: 0.76rem;
  font-weight: 700;
  color: #92400e;
  background: #fef3c7;
  border: 1px solid #fde68a;
  padding: 0.2rem 0.6rem;
  border-radius: 99px;
}

@media (max-width: 960px) {
  .timeline-range-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  .bar-brand-section, .bar-selectors-section, .bar-presets-section {
    width: 100%;
  }
  .range-select {
    width: 100%;
    min-width: 0;
  }
  .date-picker-box {
    flex: 1;
  }
}
</style>
