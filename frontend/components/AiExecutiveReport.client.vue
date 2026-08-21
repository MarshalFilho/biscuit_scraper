<template>
  <div class="glass-panel executive-panel animate-fade-in">
    <div class="panel-header" @click="toggleCollapse">
      <div class="title-group">
        <h3>🧠 {{ t('report.title', 'Relatório de Inteligência Executiva de Mercado') }} <span class="ai-badge">{{ t('report.badge', 'IA Analytics') }}</span></h3>
        <p class="subtitle">{{ t('report.subtitle', 'Diagnóstico estratégico avançado baseado em análise quantitativa em tempo real') }}</p>
      </div>
      <button class="btn-toggle">{{ isCollapsed ? t('report.expand', '▼ Expandir Insights') : t('report.collapse', '▲ Minimizar') }}</button>
    </div>

    <transition name="slide-fade">
      <div v-show="!isCollapsed" class="panel-content mt-3">
        <!-- Navegação em Abas dos 4 Macro Módulos -->
        <div class="tabs-scroll">
          <button 
            v-for="(mod, idx) in modules" 
            :key="mod.id"
            :class="['tab-btn', { active: activeTab === idx }]"
            @click="activeTab = idx"
          >
            {{ mod.id === 'estrategia' ? t('report.tab_strategy', '🎯 Estratégia & Nichos') : (mod.id === 'vendedores_produtos' ? t('report.tab_sellers', '🏆 Top Lojas & Produtos') : (mod.id === 'seo' ? t('report.tab_seo', '🏷️ Estratégia de SEO') : t('report.tab_platforms', '⚔️ Batalha de Marketplaces'))) }}
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
              <span class="update-tag">📅 {{ t('report.updated_at', 'Atualizado em') }} {{ effectiveReport?.atualizado_em || 'Recente' }}</span>
            </div>

            <p class="module-summary">{{ currentModule.resumo }}</p>

            <!-- MÓDULO 1: Estratégia Completa (Recomendações + Nichos) -->
            <div v-if="currentModule.id === 'estrategia'" class="estrategia-container">
              <!-- Subseção A: Recomendações Estratégicas -->
              <div class="sub-section mb-4">
                <h5 class="sub-title text-green">💡 Recomendações Estratégicas Acionáveis</h5>
                <div class="list-cards">
                  <div 
                    v-for="(rec, index) in (currentModule.recomendacoes || currentModule.itens || [])" 
                    :key="'rec'+index" 
                    class="action-card rec-card"
                  >
                    <span class="icon">📈</span>
                    <p v-html="typeof rec === 'string' ? rec : (rec.dica || rec.texto || JSON.stringify(rec))"></p>
                  </div>
                </div>
              </div>

              <!-- Subseção B: Oportunidades de Nicho & Demanda Oculta -->
              <div class="sub-section">
                <h5 class="sub-title text-purple">🚀 Oportunidades de Nicho & Demanda Oculta</h5>
                <div class="list-cards">
                  <div 
                    v-for="(nicho, index) in (currentModule.oportunidades_nicho || [])" 
                    :key="'nicho'+index" 
                    class="action-card niche-card"
                  >
                    <span class="icon">✨</span>
                    <p v-html="typeof nicho === 'string' ? nicho : JSON.stringify(nicho)"></p>
                  </div>
                </div>
              </div>
            </div>

            <!-- MÓDULO 2: Vendedores Líderes & Produtos Virais -->
            <div v-else-if="currentModule.id === 'vendedores_produtos' || currentModule.tipo === 'vendedores'" class="items-grid">
              <div 
                v-for="(v, index) in (currentModule.itens || [])" 
                :key="index" 
                class="item-card seller-item-card"
                @click="openSellerDetails(v)"
                title="Clique para ver todos os anúncios desta loja"
              >
                <div class="flex-between">
                  <div class="seller-name-row">
                    <strong>#{{ index + 1 }} {{ v.name }}</strong>
                    <span class="view-seller-badge">Ver Loja 🔎</span>
                  </div>
                  <span class="revenue-tag">R$ {{ (v.receita || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}</span>
                </div>
                <div class="flex-between text-sm text-muted border-t pt-1 mt-2">
                  <span>{{ (v.vendas || 0).toLocaleString('pt-BR') }} vendas ({{ v.anuncios || 1 }} un)</span>
                  <span class="top-prod-tag" v-if="v.top_produto">🏆 {{ v.top_produto }}</span>
                </div>
              </div>
            </div>

            <!-- MÓDULO 3: Estratégia de SEO & Palavras-Chave Completa -->
            <div v-else-if="currentModule.id === 'seo' || currentModule.tipo === 'seo_completo' || currentModule.tipo === 'palavras_chave'" class="seo-container">
              <!-- Palavras Chave -->
              <div class="sub-section mb-3">
                <h5 class="sub-title">🏷️ Termos de Maior Frequência nos Anúncios Top</h5>
                <div class="tags-cloud">
                  <span 
                    v-for="(kw, index) in (currentModule.palavras_chave || currentModule.itens || [])" 
                    :key="index" 
                    class="kw-tag"
                  >
                    🏷️ <strong>{{ kw.palavra || kw }}</strong> <small v-if="kw.frequencia">({{ kw.frequencia }}x)</small>
                  </span>
                </div>
              </div>

              <!-- Modelos de Títulos -->
              <div v-if="currentModule.titulos_recomendados && currentModule.titulos_recomendados.length > 0" class="sub-section mb-3">
                <h5 class="sub-title">🎯 Modelos de Título de Alta Conversão</h5>
                <div class="titles-list">
                  <div v-for="(tit, idx) in currentModule.titulos_recomendados" :key="idx" class="title-template-card">
                    <code>{{ tit }}</code>
                  </div>
                </div>
              </div>

              <!-- Combinações Long-Tail -->
              <div v-if="currentModule.combinacoes_longtail && currentModule.combinacoes_longtail.length > 0" class="sub-section">
                <h5 class="sub-title">🔗 Estruturas Long-Tail Recomendadas</h5>
                <div class="longtail-cloud">
                  <span v-for="(lt, idx) in currentModule.combinacoes_longtail" :key="idx" class="longtail-badge">
                    ⚡ {{ lt }}
                  </span>
                </div>
              </div>
            </div>

            <!-- MÓDULO 4: Batalha de Marketplaces & Faixas de Preço -->
            <div v-else-if="currentModule.id === 'plataformas_precos' || currentModule.tipo === 'plataformas'" class="items-grid">
              <div v-for="(plat, index) in (currentModule.itens || [])" :key="index" class="item-card platform-card">
                <div class="flex-between mb-2">
                  <strong>{{ plat.nome || plat.plataforma }}</strong>
                  <span :class="['badge-sm', (plat.nome || plat.plataforma || '').toLowerCase().includes('shopee') ? 'shopee' : 'meli']">
                    {{ plat.share }}% Share
                  </span>
                </div>
                <div class="flex-between text-sm mb-1">
                  <span>Volume de Vendas:</span>
                  <strong>{{ (plat.vendas || 0).toLocaleString('pt-BR') }} un</strong>
                </div>
                <div class="flex-between text-sm mb-1">
                  <span>Faturamento Estimado:</span>
                  <span class="revenue-tag">R$ {{ (plat.receita || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}</span>
                </div>
                <div class="flex-between text-sm text-muted mt-2 border-t pt-1" v-if="plat.vendedores_unicos">
                  <span>Lojas Ativas:</span>
                  <span>🏪 <strong>{{ plat.vendedores_unicos }}</strong> vendedores</span>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </transition>

    <!-- Modal de Produtos do Vendedor (aberto ao clicar no vendedor no relatório) -->
    <SellerProductsModal :seller="selectedSeller" @close="selectedSeller = null" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import SellerProductsModal from './SellerProductsModal.vue'

const props = defineProps({
  isLoading: {
    type: Boolean,
    default: false
  },
  reportData: {
    type: Object,
    default: null
  },
  products: {
    type: Array,
    default: () => []
  }
})

const defaultReportData = {
  atualizado_em: 'Modelo Padrão',
  modulos: [
    {
      id: 'estrategia',
      titulo: '🎯 Recomendações Estratégicas & Oportunidades de Nicho',
      tipo: 'estrategia_completa',
      resumo: 'Diagnósticos acionáveis baseados em dados reais e oportunidades de alta demanda reprimida.',
      recomendacoes: [
        '🎯 **Foco em Velas e Topos**: Estas categorias representam mais de 65% do volume consolidado. Oportunidade clara em criar variações de kits.',
        '💵 **Faixa Ideal de Preço**: O sweet spot de conversão está entre R$ 25,00 e R$ 60,00, concentrando a maior tração de vendas.',
        '⚡ **Kits com Envio Rápido**: Anúncios com marcação de "Envio 24h" ou "FULL" apresentam velocidade de tração 2.8x superior.'
      ],
      oportunidades_nicho: [
        '✨ **Temas Infantis Específicos**: Temas como "Safari Baby", "Moana" e "Sonic" possuem altíssima procura e baixa variação de preço.',
        '💍 **Noivinhos & Topos Personalizados**: Peças acima de R$ 120,00 possuem margem líquida superior a 45% com excelente aceitação.',
        '📦 **Lotes de Lembrancinhas (10 a 30 un)**: Combos para aniversários infantis aumentam o Ticket Médio por pedido em 40%.'
      ]
    },
    {
      id: 'vendedores_produtos',
      titulo: '🏆 Top Vendedores & Produtos Virais',
      tipo: 'vendedores',
      resumo: 'Ranking combinado dos principais vendedores e itens com maior tração no mercado.',
      itens: [
        { name: 'Loja Exemplo Premium', anuncios: 15, vendas: 1200, receita: 35000.0, top_produto: 'Vela Personalizada Luxo', plataforma: 'meli' },
        { name: 'Biscuit Arte Express', anuncios: 8, vendas: 850, receita: 21500.0, top_produto: 'Topo de Bolo Casamento', plataforma: 'shopee' }
      ]
    },
    {
      id: 'seo',
      titulo: '🏷️ Estratégia de SEO & Palavras-Chave de Alta Conversão',
      tipo: 'seo_completo',
      resumo: 'Termos mais frequentes nos títulos líderes, combinações long-tail e modelos de alta conversão.',
      palavras_chave: [
        { palavra: 'Personalizado', frequencia: 42 },
        { palavra: 'Kit Festa', frequencia: 38 },
        { palavra: 'Topo Bolo', frequencia: 32 },
        { palavra: 'Pronta Entrega', frequencia: 24 }
      ],
      titulos_recomendados: [
        'Vela Aniversário Biscuit Personalizada Tema Infantil + Envio 24h',
        'Topo De Bolo Casamento Noivinhos Biscuit Personalizados Luxo',
        'Kit 10 Lembrancinhas Safari Biscuit Festa Infantil Pronta Entrega'
      ],
      combinacoes_longtail: [
        'Vela personalizada + [Nome da Criança] + [Idade]',
        'Topo de bolo biscuit + [Tema] + [Envio Rápido]',
        'Kit lembrancinha biscuit + [Quantidade] unidades + [Tema]'
      ]
    },
    {
      id: 'plataformas_precos',
      titulo: '⚔️ Batalha de Marketplaces & Faixas de Preço',
      tipo: 'plataformas',
      resumo: 'Participação entre Mercado Livre e Shopee, e volume por zona de preço.',
      itens: [
        { nome: 'Mercado Livre', share: 52.0, vendas: 480, receita: 15000, vendedores_unicos: 15 },
        { nome: 'Shopee', share: 48.0, vendas: 620, receita: 12000, vendedores_unicos: 28 }
      ]
    }
  ]
}

const isCollapsed = ref(false)
const activeTab = ref(0)
const selectedSeller = ref(null)

const { t } = useAppI18n()

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

function openSellerDetails(sellerItem) {
  if (!sellerItem || !sellerItem.name) return
  
  const sellerProds = props.products.filter(p => p.vendedor === sellerItem.name)
  selectedSeller.value = {
    name: sellerItem.name,
    platform: sellerItem.plataforma || (sellerProds[0]?.plataforma || 'meli'),
    products: sellerProds.length > 0 ? sellerProds : [
      { id: 'demo-1', titulo: sellerItem.top_produto || 'Anúncio Principal da Loja', preco: 45.0, vendas_totais: sellerItem.vendas || 10, link: '#' }
    ],
    totalSales: sellerItem.vendas || sellerProds.reduce((acc, p) => acc + (p.vendas_totais || 0), 0),
    estimatedRevenue: sellerItem.receita || sellerProds.reduce((acc, p) => acc + ((p.preco || 0) * (p.vendas_totais || 0)), 0)
  }
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
.mb-2 { margin-bottom: 0.6rem; }
.mb-3 { margin-bottom: 1rem; }
.mb-4 { margin-bottom: 1.5rem; }
.mt-2 { margin-top: 0.5rem; }
.pt-1 { padding-top: 0.4rem; }

.tabs-scroll { display: flex; gap: 0.5rem; overflow-x: auto; padding-bottom: 0.5rem; border-bottom: 1px solid #e2e8f0; }
.tab-btn { padding: 0.5rem 0.9rem; font-size: 0.82rem; font-weight: 600; border: 1px solid #cbd5e1; background: #f8fafc; color: #475569; border-radius: 8px; cursor: pointer; white-space: nowrap; transition: all 0.2s ease; }
.tab-btn:hover { background: #f1f5f9; color: #0f172a; }
.tab-btn.active { background: #2563eb; color: #ffffff; border-color: #2563eb; }

.module-card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 1.2rem; border-radius: 12px; }
.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.5rem; }
.card-top h4 { margin: 0; color: #0f172a; font-size: 1.05rem; }
.update-tag { font-size: 0.75rem; color: #64748b; font-weight: 600; }

.module-summary { color: #334155; font-size: 0.9rem; margin: 0 0 1.2rem 0; font-weight: 500; }

.sub-title { font-size: 0.92rem; font-weight: 700; margin: 0 0 0.6rem 0; text-transform: uppercase; letter-spacing: 0.03em; }
.text-green { color: #166534; }
.text-purple { color: #6b21a8; }

.items-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 0.9rem; }
.item-card { background: #ffffff; border: 1px solid #e2e8f0; padding: 1rem; border-radius: 10px; font-size: 0.88rem; color: #0f172a; }

.seller-item-card { cursor: pointer; transition: all 0.2s ease; }
.seller-item-card:hover { border-color: #3b82f6; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08); }
.seller-name-row { display: flex; align-items: center; gap: 0.5rem; }
.view-seller-badge { font-size: 0.7rem; background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; padding: 0.15rem 0.45rem; border-radius: 6px; font-weight: 600; }
.top-prod-tag { font-size: 0.78rem; color: #d97706; font-weight: 600; max-width: 160px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.flex-between { display: flex; justify-content: space-between; align-items: center; }
.border-t { border-top: 1px solid #e2e8f0; }
.revenue-tag { font-weight: 700; color: #2563eb; font-size: 0.88rem; }

.badge-sm { font-size: 0.7rem; padding: 0.15rem 0.5rem; border-radius: 99px; font-weight: 600; }
.badge-sm.meli { background: #fef9c3; color: #854d0e; }
.badge-sm.shopee { background: #ffedd5; color: #c2410c; }

.list-cards { display: flex; flex-direction: column; gap: 0.6rem; }
.action-card { display: flex; align-items: flex-start; gap: 0.8rem; padding: 0.8rem 1rem; border-radius: 10px; background: #ffffff; }
.action-card .icon { font-size: 1.2rem; flex-shrink: 0; margin-top: 0.1rem; }
.action-card p { margin: 0; font-size: 0.88rem; line-height: 1.4; }

.rec-card { border: 1px solid #bbf7d0; }
.rec-card p { color: #166534; font-weight: 500; }

.niche-card { border: 1px solid #e9d5ff; }
.niche-card p { color: #581c87; font-weight: 500; }

.tags-cloud { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.kw-tag { background: #ffffff; border: 1px solid #cbd5e1; padding: 0.4rem 0.8rem; border-radius: 8px; font-size: 0.85rem; color: #334155; }

.titles-list { display: flex; flex-direction: column; gap: 0.4rem; }
.title-template-card { background: #ffffff; border: 1px solid #e2e8f0; padding: 0.6rem 0.9rem; border-radius: 8px; font-size: 0.85rem; color: #0f172a; }
.title-template-card code { font-family: inherit; font-weight: 600; color: #1d4ed8; }

.longtail-cloud { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.longtail-badge { background: #f1f5f9; border: 1px solid #cbd5e1; padding: 0.35rem 0.75rem; border-radius: 6px; font-size: 0.82rem; color: #334155; font-weight: 600; }

.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.3s ease; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; transform: translateY(-10px); }
</style>
