<template>
  <div class="glass-panel timeline-container animate-fade-in">
    <div class="timeline-header">
      <div class="header-info">
        <span class="timeline-badge">📅 {{ t('timeline.badge', 'LINHA DO TEMPO DE COLETAS') }}</span>
        <h3>{{ t('timeline.title', 'Explore a Evolução Histórica do Mercado') }}</h3>
        <p class="timeline-sub">{{ t('timeline.subtitle', 'Selecione uma data específica para ver o Retrato do Mercado daquele dia ou ative a comparação entre datas') }}</p>
      </div>

      <div class="timeline-controls">
        <button 
          :class="['mode-btn', { active: compareMode }]" 
          @click="toggleCompareMode"
          :title="t('timeline.compare_tooltip', 'Comparar duas coletas passadas lado a lado')"
        >
          ⚔️ {{ compareMode ? t('timeline.mode_single', 'Modo Único') : t('timeline.mode_compare', 'Modo Comparar Datas') }}
        </button>
      </div>
    </div>

    <!-- Pílulas da Linha do Tempo -->
    <div class="timeline-scroll-wrapper">
      <transition name="fade" mode="out-in">
        <div v-if="isLoading" class="timeline-pills">
          <div v-for="i in 5" :key="'skel-pill'+i" class="skeleton timeline-pill" style="width: 120px; height: 36px; border-radius: 20px;"></div>
        </div>
        <div v-else-if="availableDates.length > 0" class="timeline-pills">
        <button
          v-for="d in availableDates"
          :key="d.dateStr"
          :class="[
            'timeline-pill',
            { 
              active: !compareMode && selectedDate === d.dateStr,
              'selected-a': compareMode && compareDateA === d.dateStr,
              'selected-b': compareMode && compareDateB === d.dateStr
            }
          ]"
          @click="handleDateClick(d.dateStr)"
        >
          <span class="pill-dot"></span>
          <span class="pill-date">{{ d.label }}</span>
          <small class="pill-count">{{ d.count }} {{ t('timeline.records', 'registros') }}</small>
        </button>
        </div>
      </transition>
    </div>

    <!-- Banner comparativo quando no Modo Comparação -->
    <div v-if="compareMode && compareDateA && compareDateB" class="compare-summary-banner">
      <div class="compare-col">
        <span class="compare-tag tag-a">📍 {{ t('timeline.point_a', 'Ponto A (Base):') }}</span>
        <strong>{{ formatDateLabel(compareDateA) }}</strong>
      </div>
      <div class="compare-vs">VS</div>
      <div class="compare-col">
        <span class="compare-tag tag-b">🎯 {{ t('timeline.point_b', 'Ponto B (Atual):') }}</span>
        <strong>{{ formatDateLabel(compareDateB) }}</strong>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAppI18n } from '~/composables/useAppI18n'

const { t, locale } = useAppI18n()

const props = defineProps({
  rawItems: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false }
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

  const sorted = Array.from(map.values()).sort((a, b) => new Date(b.dateStr) - new Date(a.dateStr))

  return sorted.map((d, index) => {
    const isToday = index === 0
    const dObj = new Date(d.dateStr + 'T00:00:00')
    const formatted = dObj.toLocaleDateString(locale.value === 'pt' ? 'pt-BR' : 'en-US', { day: '2-digit', month: 'short' })
    return {
      dateStr: d.dateStr,
      count: d.count,
      label: isToday ? `${formatted} (${t('timeline.latest', 'Última')})` : formatted
    }
  })
})

function handleDateClick(dateStr) {
  if (!compareMode.value) {
    selectedDate.value = dateStr
    emit('select-date', dateStr)
  } else {
    if (!compareDateA.value || (compareDateA.value && compareDateB.value)) {
      compareDateA.value = dateStr
      compareDateB.value = null
    } else {
      compareDateB.value = dateStr
      emit('compare-dates', { dateA: compareDateA.value, dateB: compareDateB.value })
    }
  }
}

function toggleCompareMode() {
  compareMode.value = !compareMode.value
  if (!compareMode.value) {
    compareDateA.value = null
    compareDateB.value = null
    emit('select-date', selectedDate.value)
  }
}

function formatDateLabel(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString(locale.value === 'pt' ? 'pt-BR' : 'en-US', { day: '2-digit', month: 'long', year: 'numeric' })
}
</script>

<style scoped>
.timeline-container { padding: 1.5rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
.timeline-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.2rem; flex-wrap: wrap; gap: 1rem; }
.header-info h3 { margin: 0.3rem 0 0.2rem 0; color: #0f172a; font-size: 1.2rem; }
.timeline-sub { color: #64748b; font-size: 0.85rem; margin: 0; }
.timeline-badge { font-size: 0.72rem; font-weight: 700; color: #2563eb; background: #eff6ff; padding: 0.2rem 0.6rem; border-radius: 99px; border: 1px solid #bfdbfe; text-transform: uppercase; }

.mode-btn { background: #f8fafc; border: 1px solid #cbd5e1; color: #334155; padding: 0.45rem 0.9rem; border-radius: 8px; font-weight: 600; font-size: 0.85rem; cursor: pointer; transition: all 0.2s ease; }
.mode-btn:hover { background: #f1f5f9; color: #0f172a; }
.mode-btn.active { background: #2563eb; color: #ffffff; border-color: #2563eb; shadow: 0 2px 4px rgba(37,99,235,0.2); }

.timeline-scroll-wrapper { overflow-x: auto; padding-bottom: 0.5rem; }
.timeline-pills { display: flex; gap: 0.75rem; width: max-content; }
.timeline-pill { background: #f8fafc; border: 1px solid #e2e8f0; padding: 0.6rem 1rem; border-radius: 12px; cursor: pointer; transition: all 0.2s ease; display: flex; flex-direction: column; align-items: flex-start; min-width: 120px; }
.timeline-pill:hover { background: #f1f5f9; border-color: #cbd5e1; transform: translateY(-1px); }

.pill-dot { width: 8px; height: 8px; border-radius: 50%; background: #94a3b8; margin-bottom: 0.3rem; }
.pill-date { font-weight: 700; color: #1e293b; font-size: 0.9rem; }
.pill-count { font-size: 0.75rem; color: #64748b; margin-top: 0.1rem; }

.timeline-pill.active { background: #eff6ff; border-color: #2563eb; }
.timeline-pill.active .pill-dot { background: #2563eb; }
.timeline-pill.active .pill-date { color: #2563eb; }

.timeline-pill.selected-a { background: #fef3c7; border-color: #f59e0b; }
.timeline-pill.selected-a .pill-dot { background: #d97706; }
.timeline-pill.selected-a .pill-date { color: #b45309; }

.timeline-pill.selected-b { background: #dcfce7; border-color: #22c55e; }
.timeline-pill.selected-b .pill-dot { background: #16a34a; }
.timeline-pill.selected-b .pill-date { color: #15803d; }

.compare-summary-banner { display: flex; align-items: center; justify-content: space-around; background: #f8fafc; border: 1px solid #cbd5e1; padding: 0.8rem 1.2rem; border-radius: 10px; margin-top: 1rem; }
.compare-col { display: flex; flex-direction: column; gap: 0.2rem; }
.compare-tag { font-size: 0.75rem; font-weight: 700; }
.compare-tag.tag-a { color: #b45309; }
.compare-tag.tag-b { color: #15803d; }
.compare-vs { font-weight: 900; color: #94a3b8; font-size: 1.1rem; }
</style>
