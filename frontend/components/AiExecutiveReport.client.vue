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
              <span class="update-tag">📅 Atualizado em {{ reportData.atualizado_em || 'hoje' }}</span>
            </div>

            <p class="module-summary">{{ currentModule.resumo }}</p>

          <!-- Renderização Específica por Tipo de Módulo -->
          <!-- 1. Vendedores -->
          <div v-if="currentModule.tipo === 'vendedores'" class="items-grid">
            <div v-for="(v, index) in currentModule.itens" :key="index" class="item-card flex-between">
              <div>
                <strong>#{{ index + 1 }} {{ v.name }}</strong>
                <span class="sub-text">{{ v.anuncios }} anúncios ativos</span>
              </div>
              <div class="text-right">
                <span class="sales-tag">{{ v.vendas.toLocaleString('pt-BR') }} vendas</span>
                <span class="revenue-tag">R$ {{ (v.receita || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}</span>
              </div>
            </div>
          </div>

          <!-- 2. Produtos Virais -->
          <div v-else-if="currentModule.tipo === 'produtos'" class="items-grid">
            <div v-for="(p, index) in currentModule.itens" :key="index" class="item-card">
              <div class="flex-between mb-1">
                <strong class="title-truncate">{{ p.titulo }}</strong>
                <span :class="['badge-sm', p.plataforma]">{{ p.plataforma === 'meli' ? 'Mercado Livre' : 'Shopee' }}</span>
              </div>
              <div class="flex-between text-sm">
                <span>R$ {{ p.preco.toFixed(2) }}</span>
                <span class="sales-tag">{{ p.vendas.toLocaleString('pt-BR') }} vendas acumuladas</span>
              </div>
            </div>
          </div>

          <!-- 3. Palavras-Chave -->
          <div v-else-if="currentModule.tipo === 'palavras_chave'" class="tags-cloud">
            <span v-for="(kw, index) in currentModule.itens" :key="index" class="kw-tag">
              🏷️ <strong>{{ kw.palavra }}</strong> ({{ kw.frequencia }}x nos anúncios top)
            </span>
          </div>

          <!-- 4. Oceano Azul / Faixas -->
          <div v-else-if="currentModule.tipo === 'faixas_preco'" class="items-grid">
            <div v-for="(f, index) in currentModule.itens" :key="index" class="item-card flex-between">
              <strong>{{ f.faixa }}</strong>
              <span class="sales-tag">{{ f.vendas.toLocaleString('pt-BR') }} vendas nesta faixa</span>
            </div>
          </div>

          <!-- 5. Plataformas -->
          <div v-else-if="currentModule.tipo === 'plataformas'" class="items-grid">
            <div v-for="(plat, index) in currentModule.itens" :key="index" class="item-card flex-between">
              <strong>{{ plat.nome || plat.plataforma || (index === 0 ? 'Mercado Livre' : 'Shopee') }}</strong>
              <span class="sales-tag">
                {{ (plat.vendas || 0).toLocaleString('pt-BR') }} vendas
                <small v-if="plat.share"> ({{ plat.share }}% share)</small>
              </span>
            </div>
          </div>

          <!-- 6. Alertas / 7. Recomendações / Oportunidades -->
          <div v-else class="list-cards">
            <div v-for="(item, index) in currentModule.itens" :key="index" class="action-card">
              <span class="icon">💡</span>
              <p>{{ typeof item === 'string' ? item : (item.dica || item.alerta || item.texto || item.resumo || JSON.stringify(item)) }}</p>
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

const props = defineProps({
  isLoading: {
    type: Boolean,
    default: false
  },
  reportData: {
    type: Object,
    default: () => ({
      atualizado_em: '28/07/2026',
      modulos: [
        {
          id: 'top_sellers',
          titulo: '🏆 Top Vendedores em Ascensão',
          tipo: 'vendedores',
          resumo: 'Identificação dos maiores vendedores em volume acumulado.',
          itens: [
            { name: 'ArteEmBiscuit_Oficial', vendas: 450, receita: 18000, anuncios: 12 },
            { name: 'LembrancinhasExpress', vendas: 310, receita: 11470, anuncios: 8 }
          ]
        },
        {
          id: 'viral_products',
          titulo: '🔥 Produtos Virais & Tendências',
          tipo: 'produtos',
          resumo: 'Produtos com alta tração e velocidade de vendas.',
          itens: [
            { titulo: 'Kit 10 Lembrancinhas Maternidade Biscuit', preco: 35.00, vendas: 210, plataforma: 'shopee' },
            { titulo: 'Topo de Bolo Aniversario Infantil Personalizado', preco: 58.00, vendas: 180, plataforma: 'meli' }
          ]
        },
        {
          id: 'seo_strategy',
          titulo: '🎯 Estratégia de Títulos & SEO',
          tipo: 'palavras_chave',
          resumo: 'Palavras com maior frequência nos anúncios de maior giro.',
          itens: [
            { palavra: 'Personalizado', frequencia: 42 },
            { palavra: 'Kit', frequencia: 38 },
            { palavra: 'Infantil', frequencia: 29 },
            { palavra: 'Pronta Entrega', frequencia: 24 }
          ]
        },
        {
          id: 'ocean_blue',
          titulo: '💡 Faixas de Preço & Oceano Azul',
          tipo: 'faixas_preco',
          resumo: 'Faixa de R$ 25 a R$ 50 concentra o maior faturamento do mercado.',
          itens: [
            { faixa: 'Até R$25', vendas: 140 },
            { faixa: 'R$25-50', vendas: 390 },
            { faixa: 'R$50-100', vendas: 180 }
          ]
        },
        {
          id: 'platform_battle',
          titulo: '⚔️ Mercado Livre vs Shopee',
          tipo: 'plataformas',
          resumo: 'Shopee domina o volume de unidades e Mercado Livre domina peças de maior ticket.',
          itens: [
            { plataforma: 'Mercado Livre', vendas: 480 },
            { plataforma: 'Shopee', vendas: 620 }
          ]
        },
        {
          id: 'alerts',
          titulo: '📉 Alertas de Estagnação',
          tipo: 'alertas',
          resumo: 'Alertas de variação de preços e saturação de mercado.',
          itens: [
            { alerta: 'Concorrência elevada na faixa de R$ 15,00 a R$ 20,00 na Shopee.' },
            { alerta: 'Oportunidade para criação de kits combinados no Mercado Livre.' }
          ]
        },
        {
          id: 'action_recommendations',
          titulo: '📝 Recomendações Práticas',
          tipo: 'recomendacoes',
          resumo: 'Ações recomendadas para aumentar suas vendas imediatamente.',
          itens: [
            { dica: 'Crie um anúncio de Kit Lembrancinhas com frete grátis na faixa de R$45,00 a R$65,00.' },
            { dica: 'Adicione os termos "Pronta Entrega" e "Personalizado" aos seus anúncios.' }
          ]
        }
      ]
    })
  }
})

const isCollapsed = ref(false)
const activeTab = ref(0)

const modules = computed(() => props.reportData?.modulos || [])
const currentModule = computed(() => modules.value[activeTab.value] || null)

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
