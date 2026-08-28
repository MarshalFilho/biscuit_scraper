<template>
  <div :class="['timeline-container animate-fade-in', { 'embedded-mode': embedded, 'glass-panel': !embedded }]">
    <div class="timeline-header">
      <div class="header-info">
        <div class="badge-row">
          <span class="timeline-badge">📅 {{ t('timeline.badge', 'Linha do Tempo de Coletas') }}</span>
        </div>
        <h3>{{ t('timeline.title', 'Evolução Histórica e Comparação de Datas') }}</h3>
        <p class="timeline-sub">{{ t('timeline.subtitle', 'Selecione uma data para ver o retrato daquele dia ou compare duas datas para ver o crescimento real de vendas e preços.') }}</p>
      </div>

      <!-- Alternador de Modo -->
      <div class="mode-tabs">
        <button 
          :class="['mode-tab-btn', { active: !compareMode }]" 
          @click="setSingleMode"
        >
          📸 {{ t('timeline.mode_single', 'Retrato do Dia') }}
        </button>
        <button 
          :class="['mode-tab-btn', { active: compareMode }]" 
          @click="setCompareMode"
        >
          📊 {{ t('timeline.mode_compare', 'Comparar 2 Datas') }}
        </button>
      </div>
    </div>

    <!-- MODO 1: Retrato do Dia (1 Data) -->
    <div v-if="!compareMode" class="timeline-content">
      <div class="pills-label-row">
        <small class="text-muted">{{ t('timeline.click_date_hint', '👉 Clique em uma data para ver o estado do mercado naquele dia:') }}</small>
      </div>
      <div class="timeline-scroll-wrapper">
        <div v-if="isLoading" class="timeline-pills">
          <div v-for="i in 5" :key="'skel-pill'+i" class="skeleton timeline-pill" style="width: 130px; height: 38px; border-radius: 20px;"></div>
        </div>
        <div v-else-if="availableDates.length > 0" class="timeline-pills">
          <button
            v-for="d in availableDates"
            :key="d.dateStr"
            :class="['timeline-pill', { active: selectedDate === d.dateStr }]"
            @click="selectSingleDate(d.dateStr)"
          >
            <span class="pill-dot"></span>
            <span class="pill-date">{{ d.label }}</span>
            <span class="pill-count">{{ d.count }} {{ t('timeline.items', 'itens') }}</span>
          </button>
        </div>
        <div v-else class="text-muted text-sm py-2">
          {{ t('timeline.no_history', 'Nenhuma data histórica registrada ainda.') }}
        </div>
      </div>
    </div>

    <!-- MODO 2: Comparação Real de 2 Datas (A vs B) -->
    <div v-else class="compare-mode-container">
      <div class="compare-selectors-grid">
        <!-- Ponto A: Data Base (Mais antiga) -->
        <div class="compare-box box-a">
          <label>{{ t('timeline.base_date_label', '📍 Data Base (Ponto A - Passado):') }}</label>
          <select v-model="compareDateA" @change="onDateAChange" class="glass-select">
            <option v-for="d in datesForPointA" :key="'a-'+d.dateStr" :value="d.dateStr">
              {{ d.label }} ({{ d.count }} {{ t('timeline.items', 'itens') }})
            </option>
          </select>
        </div>

        <div class="compare-divider">
          <span>➔ VS ➔</span>
        </div>

        <!-- Ponto B: Data Atual (Mais recente) -->
        <div class="compare-box box-b">
          <label>{{ t('timeline.compare_date_label', '🎯 Data de Comparação (Ponto B - Mais Recente):') }}</label>
          <select v-model="compareDateB" @change="onDateBChange" class="glass-select">
            <option v-for="d in datesForPointB" :key="'b-'+d.dateStr" :value="d.dateStr">
              {{ d.label }} ({{ d.count }} {{ t('timeline.items', 'itens') }})
            </option>
          </select>
        </div>
      </div>

      <div v-if="compareDateA && compareDateB" class="compare-status-pill">
        <span>{{ t('timeline.analyzing_growth', '📊 Analisando crescimento e oscilação de preços entre {dateA} e {dateB}').replace('{dateA}', formatDateLabel(compareDateA)).replace('{dateB}', formatDateLabel(compareDateB)) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAppI18n } from '~/composables/useAppI18n'

const { t, locale } = useAppI18n()

const props = defineProps({
  rawItems: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false },
  embedded: { type: Boolean, default: false }
})

const emit = defineEmits(['select-date', 'compare-dates'])

const compareMode = ref(false)
const selectedDate = ref('latest')
const compareDateA = ref(null)
const compareDateB = ref(null)

// Extrai todas as datas de coleta únicas disponíveis nos históricos dos produtos
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

  // Ordenadas da MAIS RECENTE para a MAIS ANTIGA
  const sorted = Array.from(map.values()).sort((a, b) => new Date(b.dateStr) - new Date(a.dateStr))

  return sorted.map((d, index) => {
    const isToday = index === 0
    const dObj = new Date(d.dateStr + 'T00:00:00')
    const formatted = dObj.toLocaleDateString(locale.value === 'pt' ? 'pt-BR' : 'en-US', { day: '2-digit', month: 'short' })
    const latestText = t('timeline.latest', 'Última')
    return {
      dateStr: d.dateStr,
      count: d.count,
      label: isToday ? `${formatted} (${latestText})` : formatted
    }
  })
})

// Ponto A: datas permitidas (qualquer data exceto a mais recente se houver mais de uma)
const datesForPointA = computed(() => {
  return availableDates.value
})

// Ponto B: datas permitidas (datas mais recentes que o Ponto A)
const datesForPointB = computed(() => {
  if (!compareDateA.value) return availableDates.value
  const dateATime = new Date(compareDateA.value).getTime()
  const valid = availableDates.value.filter(d => new Date(d.dateStr).getTime() > dateATime)
  return valid.length > 0 ? valid : availableDates.value
})

function setSingleMode() {
  compareMode.value = false
  if (availableDates.value.length > 0) {
    selectedDate.value = availableDates.value[0].dateStr
  }
  emit('select-date', selectedDate.value)
}

function setCompareMode() {
  compareMode.value = true
  if (availableDates.value.length >= 2) {
    // Ponto A = mais antiga, Ponto B = mais recente
    compareDateB.value = availableDates.value[0].dateStr
    compareDateA.value = availableDates.value[availableDates.value.length - 1].dateStr
  } else if (availableDates.value.length === 1) {
    compareDateA.value = availableDates.value[0].dateStr
    compareDateB.value = availableDates.value[0].dateStr
  }
  emitCompare()
}

function onDateAChange() {
  if (new Date(compareDateA.value) >= new Date(compareDateB.value)) {
    // Ajusta B para a data mais recente disponível
    if (availableDates.value.length > 0) {
      compareDateB.value = availableDates.value[0].dateStr
    }
  }
  emitCompare()
}

function onDateBChange() {
  if (new Date(compareDateA.value) >= new Date(compareDateB.value)) {
    // Ajusta A para a data mais antiga disponível
    if (availableDates.value.length > 1) {
      compareDateA.value = availableDates.value[availableDates.value.length - 1].dateStr
    }
  }
  emitCompare()
}

function selectSingleDate(dateStr) {
  selectedDate.value = dateStr
  emit('select-date', dateStr)
}

function emitCompare() {
  if (compareDateA.value && compareDateB.value) {
    emit('compare-dates', { dateA: compareDateA.value, dateB: compareDateB.value })
  }
}

function formatDateLabel(dateStr) {
  if (!dateStr) return ''
  const item = availableDates.value.find(d => d.dateStr === dateStr)
  return item ? item.label : dateStr
}

onMounted(() => {
  if (availableDates.value.length > 0) {
    selectedDate.value = availableDates.value[0].dateStr
  }
})
</script>

<style scoped>
.timeline-container {
  padding: 1.4rem 1.6rem;
  margin-bottom: 2rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
}

.timeline-container.embedded-mode {
  padding: 1rem 0 0 0;
  margin-bottom: 0;
  background: transparent;
  border: none;
  border-top: 1px solid #f1f5f9;
  border-radius: 0;
  box-shadow: none;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.2rem;
}

.badge-row {
  margin-bottom: 0.3rem;
}

.timeline-badge {
  font-size: 0.72rem;
  font-weight: 800;
  color: #2563eb;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  padding: 0.2rem 0.6rem;
  border-radius: 99px;
  text-transform: uppercase;
}

.header-info h3 {
  margin: 0.2rem 0;
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
}

.timeline-sub {
  margin: 0;
  font-size: 0.85rem;
  color: #64748b;
}

.mode-tabs {
  display: flex;
  background: #f1f5f9;
  padding: 0.25rem;
  border-radius: 10px;
  gap: 0.25rem;
}

.mode-tab-btn {
  background: none;
  border: none;
  padding: 0.45rem 0.9rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 700;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-tab-btn:hover {
  color: #0f172a;
}

.mode-tab-btn.active {
  background: #ffffff;
  color: #2563eb;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.pills-label-row {
  margin-bottom: 0.6rem;
}

.timeline-scroll-wrapper {
  overflow-x: auto;
  padding-bottom: 0.4rem;
}

.timeline-pills {
  display: flex;
  gap: 0.6rem;
  align-items: center;
}

.timeline-pill {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 0.5rem 1rem;
  border-radius: 99px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  font-size: 0.88rem;
  color: #334155;
}

.timeline-pill:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}

.timeline-pill.active {
  background: #eff6ff;
  border-color: #3b82f6;
  color: #1d4ed8;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
}

.pill-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #94a3b8;
}

.timeline-pill.active .pill-dot {
  background: #2563eb;
}

.pill-count {
  font-size: 0.75rem;
  color: #64748b;
  background: #ffffff;
  padding: 0.15rem 0.45rem;
  border-radius: 99px;
  border: 1px solid #e2e8f0;
}

.timeline-pill.active .pill-count {
  background: #dbeafe;
  color: #1e40af;
  border-color: #bfdbfe;
}

.compare-mode-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.2rem;
}

.compare-selectors-grid {
  display: flex;
  align-items: center;
  gap: 1.2rem;
  flex-wrap: wrap;
}

.compare-box {
  flex: 1;
  min-width: 220px;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.compare-box label {
  font-size: 0.82rem;
  font-weight: 700;
  color: #475569;
}

.glass-select {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  padding: 0.6rem 0.8rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #0f172a;
  outline: none;
}

.glass-select:focus {
  border-color: #2563eb;
}

.compare-divider {
  font-weight: 900;
  font-size: 0.82rem;
  color: #64748b;
  padding-top: 1rem;
}

.compare-status-pill {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1e40af;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  font-size: 0.88rem;
  text-align: center;
}
</style>
