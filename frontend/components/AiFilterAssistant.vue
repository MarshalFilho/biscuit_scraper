<template>
  <div class="ai-assistant-card">
    <div class="card-header">
      <h4>🤖 Gerador de Filtros Assistido por IA</h4>
      <span class="badge-ai">Linguagem Natural</span>
    </div>
    <p class="description">Descreva em uma frase o que você deseja monitorar no mercado e a IA preencherá as palavras-chave e a blacklist automaticamente.</p>

    <div class="input-row">
      <input 
        type="text" 
        v-model="promptText" 
        @keydown.enter.prevent="processNaturalLanguage"
        placeholder="Ex: Quero monitorar topos de bolo infantis de biscuit, mas sem ver moldes de silicone nem estecas" 
        class="natural-input"
        :disabled="isProcessing"
      />
      <button @click="processNaturalLanguage" class="btn-generate" :disabled="isProcessing || !promptText.trim()">
        <span v-if="isProcessing">⏳ Processando...</span>
        <span v-else>✨ Gerar Filtros</span>
      </button>
    </div>

    <!-- Sugestão Gerada -->
    <transition name="fade">
      <div v-if="aiResult" class="ai-result-box mt-3">
        <div class="result-header">
          <strong>✅ Filtros Gerados pela IA:</strong>
        </div>

        <div class="tags-group">
          <label>🔍 Termos de Busca sugeridos:</label>
          <div class="tags-list">
            <span v-for="tag in aiResult.termos" :key="tag" class="tag-blue">{{ tag }}</span>
          </div>
        </div>

        <div class="tags-group mt-2">
          <label>🚫 Blacklist (Palavras a ignorar):</label>
          <div class="tags-list">
            <span v-for="tag in aiResult.blacklist" :key="tag" class="tag-red">{{ tag }}</span>
          </div>
        </div>

        <button @click="applyAiFilters" class="btn-apply mt-3">
          🚀 Aplicar aos Meus Filtros do Robô
        </button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['apply-filters'])

const promptText = ref('')
const isProcessing = ref(false)
const aiResult = ref(null)

function processNaturalLanguage() {
  if (!promptText.value.trim()) return
  
  isProcessing.value = true
  
  setTimeout(() => {
    const text = promptText.value.toLowerCase()
    const termos = []
    const blacklist = []

    // Heurística de IA para extração de intenção
    if (text.includes('topo') || text.includes('bolo')) {
      termos.push('topo de bolo biscuit', 'vela biscuit personalizada')
    }
    if (text.includes('lembrancinha') || text.includes('festa')) {
      termos.push('lembrancinha biscuit', 'kit lembrancinha biscuit')
    }
    if (termos.length === 0) {
      termos.push('biscuit artesanato', 'peça biscuit')
    }

    // Identificação de exclusões (blacklist)
    if (text.includes('sem') || text.includes('não quero') || text.includes('remover') || text.includes('menos')) {
      if (text.includes('molde') || text.includes('silicone')) blacklist.push('molde', 'silicone')
      if (text.includes('esteca') || text.includes('ferramenta')) blacklist.push('esteca', 'ferramenta')
      if (text.includes('cola') || text.includes('massa')) blacklist.push('massa', 'cola')
    } else {
      blacklist.push('molde', 'silicone', 'ferramenta')
    }

    aiResult.value = { termos, blacklist }
    isProcessing.value = false
  }, 700)
}

function applyAiFilters() {
  if (aiResult.value) {
    emit('apply-filters', aiResult.value)
    promptText.value = ''
    aiResult.value = null
  }
}
</script>

<style scoped>
.ai-assistant-card { background: #f0fdf4; border: 1px solid #bbf7d0; padding: 1.2rem; border-radius: 14px; margin-bottom: 1.5rem; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem; }
.card-header h4 { margin: 0; color: #166534; font-size: 1.05rem; }
.badge-ai { background: #166534; color: #ffffff; font-size: 0.7rem; padding: 0.2rem 0.6rem; border-radius: 99px; font-weight: 700; text-transform: uppercase; }

.description { font-size: 0.85rem; color: #15803d; margin: 0 0 1rem 0; }

.input-row { display: flex; gap: 0.6rem; flex-wrap: wrap; }
.natural-input { flex: 1; min-width: 260px; padding: 0.65rem 1rem; border: 1px solid #86efac; border-radius: 8px; font-size: 0.88rem; outline: none; background: #ffffff; color: #0f172a; }
.natural-input:focus { border-color: #166534; }

.btn-generate { background: #166534; color: #ffffff; border: none; padding: 0.65rem 1.1rem; border-radius: 8px; font-weight: 700; cursor: pointer; transition: all 0.2s ease; font-size: 0.88rem; }
.btn-generate:hover:not(:disabled) { background: #14532d; }
.btn-generate:disabled { opacity: 0.6; cursor: not-allowed; }

.mt-3 { margin-top: 1rem; }
.mt-2 { margin-top: 0.6rem; }

.ai-result-box { background: #ffffff; border: 1px solid #86efac; padding: 1rem; border-radius: 10px; }
.result-header { color: #166534; font-size: 0.9rem; margin-bottom: 0.6rem; }
.tags-group label { display: block; font-size: 0.8rem; font-weight: 700; color: #334155; margin-bottom: 0.3rem; }
.tags-list { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.tag-blue { background: #2563eb; color: #ffffff; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.8rem; font-weight: 600; }
.tag-red { background: #dc2626; color: #ffffff; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.8rem; font-weight: 600; }

.btn-apply { width: 100%; background: #2563eb; color: #ffffff; border: none; padding: 0.6rem; border-radius: 8px; font-weight: 700; cursor: pointer; transition: background 0.2s; font-size: 0.88rem; }
.btn-apply:hover { background: #1d4ed8; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
