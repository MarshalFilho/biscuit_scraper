<template>
  <div class="glass-panel executive-panel animate-fade-in">
    <div class="panel-header" @click="toggleCollapse">
      <div class="title-group">
        <h3>🧠 Relatório de Inteligência Executiva de Mercado <span class="ai-badge">IA Analytics</span></h3>
        <p class="subtitle">Análise avançada dos 7 módulos estratégicos baseados em dados reais</p>
      </div>
      <button class="btn-toggle">{{ isCollapsed ? '▼ Expandir Insights' : '▲ Minimizar' }}</button>
    </div>

    <transition name="slide-fade">
      <div v-show="!isCollapsed" class="panel-content mt-3">
        <!-- Navegação em Abas dos 7 Módulos -->
        <div class="tabs-scroll">
          <button 
            v-for="(mod, idx) in modules" 
            :key="mod.id"
            :class="['tab-btn', { active: activeTab === idx }]"
            @click="activeTab = idx"
          >
            {{ mod.titulo }}
          </button>
        </div>

        <!-- Conteúdo do Módulo Ativo -->
        <div class="module-card mt-3">
          <div v-if="isLoading">
            <div class="card-top mb-2">
              <div class="skeleton skeleton-title" style="width: 40%"></div>
              <div class="skeleton skeleton-text" style="width: 20%"></div>
            </div>
            <div class="skeleton skeleton-text" style="width: 80%"></div>
            <div class="skeleton skeleton-text" style="width: 60%; margin-bottom: 2rem;"></div>
            
            <div class="items-grid">
              <div class="skeleton skeleton-card" v-for="i in 3" :key="'skel'+i"></div>
            </div>
          </div>
          
          <div v-else-if="currentModule">
            <div class="card-top">
              <h4>{{ currentModule.titulo }}</h4>
              <span class="update-tag">📅 Atualizado em {{ effectiveReport?.atualizado_em || 'Recente' }}</span>
            </div>

            <p class="module-summary">{{ currentModule.resumo }}</p>

          <!-- Renderização Específica por Tipo de Módulo -->
          <!-- 1. Estratégia (lista_texto) -->
          <div v-if="currentModule.tipo === 'lista_texto'" class="list-cards">
            <div v-for="(item, index) in currentModule.itens" :key="index" class="action-card">
              <span class="icon">💡</span>
              <p v-html="typeof item === 'string' ? item : item.dica"></p>
            </div>
          </div>

          <!-- 2. Vendedores & Produtos (vendedores) -->
          <div v-else-if="currentModule.tipo === 'vendedores'" class="items-grid">
            <div v-for="(v, index) in currentModule.itens" :key="index" class="item-card flex-between" style="flex-direction: column; align-items: stretch; gap: 0.5rem;">
              <div class="flex-between">
                <strong>#{{ index + 1 }} {{ v.name }}</strong>
                <span class="revenue-tag">R$ {{ (v.receita || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}</span>
              </div>
              <div class="flex-between text-sm text-muted border-t pt-1" style="border-top: 1px solid #e2e8f0; padding-top: 0.5rem;">
                <span>{{ v.vendas.toLocaleString('pt-BR') }} vendas ({{ v.anuncios }} un)</span>
                <span class="title-truncate" :title="v.top_produto" style="max-width: 150px; text-align: right; font-size: 0.8rem;" v-if="v.top_produto">🏆 {{ v.top_produto }}</span>
              </div>
            </div>
          </div>

          <!-- 3. SEO (palavras_chave) -->
          <div v-else-if="currentModule.tipo === 'palavras_chave'" class="tags-cloud">
            <span v-for="(kw, index) in currentModule.itens" :key="index" class="kw-tag">
              🏷️ <strong>{{ kw.palavra }}</strong> ({{ kw.frequencia }}x)
            </span>
          </div>

          <!-- 4. Plataformas & Preços (plataformas) -->
          <div v-else-if="currentModule.tipo === 'plataformas'" class="items-grid">
            <div v-for="(plat, index) in currentModule.itens" :key="index" class="item-card">
              <div class="flex-between mb-1">
                <strong>{{ plat.nome || plat.plataforma }}</strong>
                <span :class="['badge-sm', (plat.nome || plat.plataforma).toLowerCase().includes('shopee') ? 'shopee' : 'meli']">
                  {{ plat.share }}% Share
                </span>
              </div>
              <div class="flex-between text-sm">
                <span>{{ (plat.vendas || 0).toLocaleString('pt-BR') }} Vendas</span>
                <span class="revenue-tag">R$ {{ (plat.receita || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}</span>
              </div>
              <div class="text-sm mt-1" v-if="plat.vendedores_unicos">
                🏪 {{ plat.vendedores_unicos }} Vendedores Únicos
              </div>
            </div>
          </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const defaultReportData = {
  atualizado_em: 'Modelo Padrão',
  modulos: [
    {
      id: 'estrategia',
      titulo: '🎯 Recomendações Estratégicas & Oportunidades de Nicho',
      tipo: 'lista_texto',
      resumo: 'Ações imediatas e oportunidades de alta demanda baseadas nos dados da extração atual.',
      itens: [
        '🎯 **Foco em Velas e Topos**: Estas categorias representam a maior parte do volume de buscas ativo.',
        '💵 **Faixa Ideal de Preço**: Identifique na sua lista os produtos que estão no "sweet spot" entre R$ 25 e R$ 60.',
        '✨ **Oportunidades de Nicho**: Explore temas como "Sonic" e "Safari" que costumam ter excelente margem.'
      ]
    },
    {
      id: 'vendedores_produtos',
      titulo: '🏆 Top Vendedores & Produtos Virais',
      tipo: 'vendedores',
      resumo: 'Ranking de vendedores simulado. O relatório real puxará os concorrentes que mais vendem hoje.',
      itens: [
        { name: 'Loja Exemplo Premium', anuncios: 15, vendas: 1200, receita: 35000.0, top_produto: 'Vela Personalizada Luxo' },
        { name: 'Biscuit Arte Express', anuncios: 8, vendas: 850, receita: 21500.0, top_produto: 'Topo de Bolo Casamento' }
      ]
    },
    {
      id: 'seo',
      titulo: '🏷️ Estratégia de SEO & Palavras-Chave de Alta Conversão',
      tipo: 'palavras_chave',
      resumo: 'Palavras que mais atraem vendas no mercado de Biscuit.',
      itens: [
        { palavra: 'Personalizado', frequencia: 42 },
        { palavra: 'Kit Festa', frequencia: 38 },
        { palavra: 'Pronta Entrega', frequencia: 24 }
      ]
    },
    {
      id: 'plataformas_precos',
      titulo: '⚔️ Batalha de Marketplaces & Faixas de Preço',
      tipo: 'plataformas',
      resumo: 'A divisão de mercado será calculada automaticamente com base nas suas extrações.',
      itens: [
        { nome: 'Mercado Livre', share: 45.5, vendas: 480, receita: 15000, vendedores_unicos: 15 },
        { nome: 'Shopee', share: 54.5, vendas: 620, receita: 12000, vendedores_unicos: 28 }
      ]
    }
  ]
}

const props = defineProps({
  isLoading: {
    type: Boolean,
    default: false
  },
  reportData: {
    type: Object,
    default: null
  }
})

const isCollapsed = ref(false)
const activeTab = ref(0)

const effectiveReport = computed(() => {
  if (props.reportData && Array.isArray(props.reportData.modulos) && props.reportData.modulos.length > 0) {
    return props.reportData
  }
  return defaultReportData
})

const modules = computed(() => effectiveReport.value.modulos || [])
const currentModule = computed(() => modules.value[activeTab.value] || modules.value[0] || null)

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
}
</script>

<style scoped>
.executive-panel { padding: 1.5rem; background: #ffffff; border: 1px solid #cbd5e1; border-radius: 16px; margin-bottom: 1.5rem; box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.06); }
.panel-header { display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
.title-group h3 { margin: 0 0 0.2rem 0; color: #0f172a; font-size: 1.2rem; display: flex; align-items: center; gap: 0.6rem; }
.subtitle { color: #64748b; font-size: 0.85rem; margin: 0; }
.ai-badge { background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; font-size: 0.72rem; padding: 0.2rem 0.6rem; border-radius: 99px; font-weight: 700; text-transform: uppercase; }
.btn-toggle { background: transparent; border: none; color: #2563eb; font-weight: 700; cursor: pointer; font-size: 0.88rem; }

.mt-3 { margin-top: 1rem; }
.mb-1 { margin-bottom: 0.3rem; }

.tabs-scroll { display: flex; gap: 0.5rem; overflow-x: auto; padding-bottom: 0.5rem; border-bottom: 1px solid #e2e8f0; }
.tab-btn { padding: 0.5rem 0.9rem; font-size: 0.82rem; font-weight: 600; border: 1px solid #cbd5e1; background: #f8fafc; color: #475569; border-radius: 8px; cursor: pointer; white-space: nowrap; transition: all 0.2s ease; }
.tab-btn:hover { background: #f1f5f9; color: #0f172a; }
.tab-btn.active { background: #2563eb; color: #ffffff; border-color: #2563eb; }

.module-card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 1.2rem; border-radius: 12px; }
.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.5rem; }
.card-top h4 { margin: 0; color: #0f172a; font-size: 1.05rem; }
.update-tag { font-size: 0.75rem; color: #64748b; font-weight: 600; }

.module-summary { color: #334155; font-size: 0.9rem; margin: 0 0 1rem 0; font-weight: 500; }

.items-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 0.8rem; }
.item-card { background: #ffffff; border: 1px solid #e2e8f0; padding: 0.8rem 1rem; border-radius: 10px; font-size: 0.88rem; color: #0f172a; }
.flex-between { display: flex; justify-content: space-between; align-items: center; }
.text-right { text-align: right; }
.sub-text { display: block; font-size: 0.78rem; color: #64748b; margin-top: 0.1rem; }
.sales-tag { font-weight: 700; color: #059669; font-size: 0.85rem; display: block; }
.revenue-tag { font-weight: 700; color: #2563eb; font-size: 0.85rem; display: block; }
.title-truncate { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 200px; }

.badge-sm { font-size: 0.7rem; padding: 0.15rem 0.5rem; border-radius: 99px; font-weight: 600; }
.badge-sm.meli { background: #fef9c3; color: #854d0e; }
.badge-sm.shopee { background: #ffedd5; color: #c2410c; }

.tags-cloud { display: flex; flex-wrap: wrap; gap: 0.6rem; }
.kw-tag { background: #ffffff; border: 1px solid #cbd5e1; padding: 0.4rem 0.8rem; border-radius: 8px; font-size: 0.85rem; color: #334155; }

.list-cards { display: flex; flex-direction: column; gap: 0.6rem; }
.action-card { display: flex; align-items: center; gap: 0.8rem; background: #ffffff; border: 1px solid #bbf7d0; padding: 0.8rem 1rem; border-radius: 10px; }
.action-card .icon { font-size: 1.2rem; }
.action-card p { margin: 0; font-size: 0.88rem; color: #166534; font-weight: 600; }

.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.3s ease; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; transform: translateY(-10px); }
</style>
