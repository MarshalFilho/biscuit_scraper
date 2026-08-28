<template>
  <div class="container">
    <Navbar 
      :projectName="nomeProjeto" 
      :user="authUser" 
      @auth-change="handleAuthChange" 
      @open-keywords="isKeywordsModalOpen = true"
      @open-request-term="isRequestTermModalOpen = true"
    />

    <AntiBotAlert :alerta="statusAlerta" />

    <!-- Modal de Gerenciamento de Palavras-Chave & IA (Exclusivo Admin) -->
    <KeywordsManager 
      :isOpen="isKeywordsModalOpen" 
      :user="authUser" 
      @close="isKeywordsModalOpen = false" 
      @saved="onKeywordsSaved" 
    />

    <!-- Modal de Solicitação de Novo Termo (Exclusivo Cliente) -->
    <RequestTermModal 
      v-if="isRequestTermModalOpen" 
      :user="authUser" 
      @close="isRequestTermModalOpen = false" 
      @toast="handleClientToast" 
    />

    <!-- Modal do Administrador: Recusar Solicitação com Motivo -->
    <div v-if="isRejectModalOpen" class="modal-backdrop" @click.self="isRejectModalOpen = false">
      <div class="modal-card glass-panel animate-scale-up" style="max-width: 480px;">
        <div class="modal-header">
          <div class="header-left">
            <div class="icon-badge" style="background: #fee2e2; border-color: #fecdd3; color: #dc2626;">⚠️</div>
            <div>
              <h3>{{ t('admin.reject_modal_title', 'Recusar Solicitação de Termo') }}</h3>
              <p class="subtitle">{{ t('admin.reject_modal_subtitle', 'Informe ao cliente o motivo pelo qual este termo não pôde ser aprovado.') }}</p>
            </div>
          </div>
          <button class="close-btn" @click="isRejectModalOpen = false">✕</button>
        </div>

        <div class="modal-body" v-if="rejectingRequest">
          <div class="reject-summary-box">
            <span>🔍 <strong>Termo:</strong> {{ rejectingRequest.termo }}</span>
            <span>👤 <strong>Cliente:</strong> {{ rejectingRequest.solicitante_email }}</span>
          </div>

          <div class="form-group">
            <label class="form-label">
              {{ t('admin.reject_reason_label', 'Motivo da recusa (será exibido ao cliente):') }} <span class="required">*</span>
            </label>
            <textarea 
              v-model="rejectReason" 
              :placeholder="t('admin.reject_reason_placeholder', 'Ex: Termo fora do nicho cadastrado ou volume de busca irrelevante...')" 
              class="glass-textarea" 
              rows="3"
              maxlength="200"
              required
            ></textarea>
          </div>

          <!-- Chips de Motivos Rápidos -->
          <div class="quick-reasons-row">
            <small class="text-muted">{{ t('admin.quick_reasons', 'Motivos rápidos:') }}</small>
            <div class="chips-list">
              <button type="button" class="reason-chip" @click="applyQuickReason('Termo fora do nicho de atuação monitorado')">
                🎯 {{ t('admin.reason_out_of_niche', 'Fora do nicho') }}
              </button>
              <button type="button" class="reason-chip" @click="applyQuickReason('Volume de buscas e anúncios muito baixo nos marketplaces')">
                📉 {{ t('admin.reason_low_volume', 'Baixo volume') }}
              </button>
              <button type="button" class="reason-chip" @click="applyQuickReason('Este nicho já é atendido por outro termo ativo na sua lista')">
                🔁 {{ t('admin.reason_duplicate', 'Já existente') }}
              </button>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-cancel" @click="isRejectModalOpen = false">
              {{ t('request_term.cancel', 'Cancelar') }}
            </button>
            <button type="button" class="btn-confirm-reject" :disabled="!rejectReason.trim()" @click="confirmRejectAdminRequest">
              {{ t('admin.btn_confirm_reject', 'Confirmar e Enviar Motivo') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ t('global.connecting_db', 'Conectando à base de dados segura do Supabase...') }}</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>{{ t('global.error_loading', '⚠️ Ocorreu um erro ao carregar os dados:') }} {{ error }}</p>
    </div>

    <!-- PAINEL EXCLUSIVO ADMIN: Central de Autorizações & Histórico de Decisões -->
    <section v-if="isAdmin" class="admin-approval-panel glass-panel animate-fade-in">
      <div class="admin-header-row">
        <div class="admin-title-box">
          <div class="admin-badge-row">
            <span class="admin-crown-badge">👑 PAINEL DO ADMINISTRADOR</span>
            <span class="pending-count-badge" v-if="adminPendingRequests.length > 0">
              {{ adminPendingRequests.length }} pendente(s)
            </span>
          </div>
          <h3>{{ t('admin.approval_title', 'Central de Autorizações & Solicitações de Clientes Básicos') }}</h3>
          <p class="admin-subtitle">{{ t('admin.approval_subtitle', 'Analise, autorize ou recuse os novos termos e nichos solicitados pelos clientes.') }}</p>
        </div>

        <!-- Abas do Administrador: Pendentes vs Histórico -->
        <div class="admin-nav-tabs">
          <button 
            type="button" 
            class="admin-nav-tab" 
            :class="{ active: adminActiveTab === 'pending' }" 
            @click="adminActiveTab = 'pending'"
          >
            ⏳ {{ t('admin.tab_pending', 'Solicitações Pendentes') }}
            <span class="tab-counter" v-if="adminPendingRequests.length > 0">{{ adminPendingRequests.length }}</span>
          </button>
          <button 
            type="button" 
            class="admin-nav-tab" 
            :class="{ active: adminActiveTab === 'history' }" 
            @click="adminActiveTab = 'history'"
          >
            📋 {{ t('admin.tab_history', 'Histórico de Decisões') }}
            <span class="tab-counter secondary" v-if="adminDecisionHistory.length > 0">{{ adminDecisionHistory.length }}</span>
          </button>
        </div>
      </div>

      <!-- ABA 1: Solicitações Pendentes -->
      <div v-if="adminActiveTab === 'pending'">
        <div v-if="adminPendingRequests.length > 0" class="admin-requests-grid">
          <div v-for="req in adminPendingRequests" :key="req.id" class="admin-request-card">
            <div class="req-card-left">
              <div class="req-main-info">
                <strong class="req-term-title">🔍 {{ req.termo }}</strong>
                <span v-if="req.nicho" class="req-nicho-pill">{{ req.nicho }}</span>
                <span class="user-tier-pill">BÁSICO</span>
              </div>
              <p v-if="req.motivo" class="req-reason-text">"{{ req.motivo }}"</p>
              <div class="req-footer-meta">
                <span class="meta-item">👤 <strong>{{ req.solicitante_email || 'Cliente' }}</strong></span>
                <span v-if="req.membro_desde" class="meta-item">📅 {{ t('admin.member_since', 'Membro desde:') }} {{ formatDateShort(req.membro_desde) }}</span>
                <span class="meta-item">📊 {{ req.total_termos_ativos || 0 }} {{ t('admin.active_terms_count', 'termos ativos no robô') }}</span>
                <span v-if="req.data_solicitacao" class="meta-item">🕒 {{ t('admin.last_request_date', 'Pedido em:') }} {{ formatDateShort(req.data_solicitacao) }}</span>
              </div>
            </div>
            <div class="req-card-actions">
              <button type="button" class="btn-action-approve" @click="approveAdminRequest(req)" :title="t('admin.btn_approve', '✓ Autorizar Termo')">
                {{ t('admin.btn_approve', '✓ Autorizar Termo') }}
              </button>
              <button type="button" class="btn-action-reject" @click="openRejectModal(req)" :title="t('admin.btn_reject', '✕ Recusar')">
                {{ t('admin.btn_reject', '✕ Recusar') }}
              </button>
            </div>
          </div>
        </div>

        <div v-else class="admin-empty-requests">
          <span class="empty-icon">✨</span>
          <div>
            <strong>{{ t('admin.no_pending', 'Nenhuma solicitação pendente no momento.') }}</strong>
            <p>{{ t('admin.no_pending_desc', 'Quando os clientes do plano Básico solicitarem novos termos, eles aparecerão aqui para sua aprovação com 1 clique.') }}</p>
          </div>
        </div>
      </div>

      <!-- ABA 2: Histórico de Decisões com Filtros & Paginação -->
      <div v-else-if="adminActiveTab === 'history'" class="admin-history-section animate-fade-in">
        <!-- Barra de Filtros e Busca do Histórico -->
        <div class="history-controls-row">
          <div class="history-search-box">
            <span class="search-icon">🔍</span>
            <input 
              type="text" 
              v-model="historySearchQuery" 
              :placeholder="t('admin.search_history_placeholder', 'Filtrar por termo ou cliente...')" 
              class="history-search-input"
            />
            <button v-if="historySearchQuery" class="clear-search-btn" @click="historySearchQuery = ''">✕</button>
          </div>

          <div class="history-filter-pills">
            <button 
              type="button" 
              class="history-pill-btn" 
              :class="{ active: historyStatusFilter === 'all' }" 
              @click="historyStatusFilter = 'all'; historyCurrentPage = 1"
            >
              {{ t('admin.filter_all_status', 'Todos os Status') }} ({{ adminDecisionHistory.length }})
            </button>
            <button 
              type="button" 
              class="history-pill-btn approved" 
              :class="{ active: historyStatusFilter === 'aprovada' }" 
              @click="historyStatusFilter = 'aprovada'; historyCurrentPage = 1"
            >
              {{ t('admin.filter_approved', '✓ Aprovadas') }}
            </button>
            <button 
              type="button" 
              class="history-pill-btn rejected" 
              :class="{ active: historyStatusFilter === 'recusada' }" 
              @click="historyStatusFilter = 'recusada'; historyCurrentPage = 1"
            >
              {{ t('admin.filter_rejected', '✕ Recusadas') }}
            </button>
          </div>
        </div>

        <!-- Lista de Itens do Histórico -->
        <div v-if="paginatedDecisionHistory.length > 0" class="history-items-list">
          <div v-for="item in paginatedDecisionHistory" :key="item.id" class="history-item-card" :class="item.status">
            <div class="history-item-header">
              <div class="history-term-box">
                <strong class="history-term-name">🔍 {{ item.termo }}</strong>
                <span v-if="item.nicho" class="req-nicho-pill">{{ item.nicho }}</span>
                <span class="status-badge" :class="item.status">
                  {{ item.status === 'aprovada' ? t('admin.status_approved', 'APROVADA') : t('admin.status_rejected', 'RECUSADA') }}
                </span>
              </div>
              <span class="history-date-badge">
                🕒 {{ formatDateShort(item.data_decisao || item.data_solicitacao) }}
              </span>
            </div>

            <div class="history-item-body">
              <div class="history-meta-row">
                <span>👤 <strong>{{ t('admin.col_client', 'Cliente') }}:</strong> {{ item.solicitante_email || 'Cliente' }}</span>
                <span v-if="item.data_solicitacao">📅 <strong>{{ t('admin.last_request_date', 'Pedido:') }}</strong> {{ formatDateShort(item.data_solicitacao) }}</span>
              </div>

              <!-- Motivo original do cliente -->
              <p v-if="item.motivo" class="history-client-reason">
                💬 <strong>Pedido do cliente:</strong> "{{ item.motivo }}"
              </p>

              <!-- Justificativa da decisão -->
              <div v-if="item.status === 'recusada'" class="history-decision-note rejected">
                ⚠️ <strong>{{ t('admin.reason_label', 'Justificativa da Recusa:') }}</strong> "{{ item.motivo_recusa || 'Fora dos critérios de monitoramento.' }}"
              </div>
              <div v-else class="history-decision-note approved">
                ✓ <strong>{{ t('admin.approved_note', 'Termo adicionado à rotina de monitoramento do robô.') }}</strong>
              </div>
            </div>
          </div>

          <!-- Paginação do Histórico -->
          <div class="history-pagination" v-if="historyTotalPages > 1">
            <button 
              type="button" 
              class="btn-page" 
              :disabled="historyCurrentPage <= 1"
              @click="historyCurrentPage--"
            >
              {{ t('admin.btn_prev', '◀ Anterior') }}
            </button>
            <span class="page-indicator">
              {{ t('admin.page_info', 'Página {current} de {total}').replace('{current}', historyCurrentPage).replace('{total}', historyTotalPages) }}
            </span>
            <button 
              type="button" 
              class="btn-page" 
              :disabled="historyCurrentPage >= historyTotalPages"
              @click="historyCurrentPage++"
            >
              {{ t('admin.btn_next', 'Próximo ▶') }}
            </button>
          </div>
        </div>

        <!-- Histórico Vazio -->
        <div v-else class="admin-empty-requests">
          <span class="empty-icon">📂</span>
          <div>
            <strong>{{ t('admin.no_history', 'Nenhuma decisão registrada no histórico.') }}</strong>
            <p>{{ t('admin.no_history_desc', 'Assim que você autorizar ou recusar solicitações de termos, os registros detalhados aparecerão aqui.') }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Estado Vazio para Novos Usuários Sem Produtos Raspados (Apenas Clientes Pro e Básico) -->
    <div v-else-if="!isAdmin && productsRaw.length === 0" class="empty-account-container animate-fade-in">
      <div class="empty-account-card glass-panel">
        <div class="empty-icon-circle">📊</div>
        <h2>{{ t('onboarding.welcome_title', 'Sua conta está pronta para o monitoramento!') }}</h2>
        <p class="empty-description">
          {{ isBasic ? t('onboarding.basic_desc', 'Sua conta do Plano Básico está ativa! Quando a raspagem automática for executada para os termos aprovados, seus produtos aparecerão aqui. Você também pode solicitar novos termos ao administrador.') : t('onboarding.welcome_desc', 'Ainda não foram coletados produtos para o seu usuário. Configure seu nicho e termos de busca clicando no botão abaixo.') }}
        </p>
        <div class="empty-actions">
          <!-- Se for Admin ou Pro: Configurar Termos -->
          <button v-if="canManageDirectly" type="button" class="btn-configure-terms" @click="isKeywordsModalOpen = true">
            🎯 {{ isAdmin ? t('keywords.badge', 'Configurar Termos & IA') : t('keywords.badge_pro', 'Meus Termos & IA') }}
          </button>
          <!-- Se for Basic: Solicitar Termo -->
          <button v-else type="button" class="btn-request-term-large" @click="isRequestTermModalOpen = true">
            💡 {{ t('request_term.btn_label', 'Solicitar Termo ao Administrador') }}
          </button>
        </div>
        <div class="empty-schedule-box">
          <span>⏰ <strong>{{ t('onboarding.schedule_info', 'Rotina Agendada:') }}</strong> {{ t('filters.daily_info', 'A raspagem automática é executada diariamente às 22h00 para todos os seus termos.') }}</span>
        </div>
      </div>
    </div>

    <div v-else>
      <!-- Relatório de Inteligência Executiva por IA (Fase 4) -->
      <AiExecutiveReport 
        :isLoading="loading || isFetchingNewData" 
        :reportData="aiReportData"
        :products="processedProducts"
      />

      <!-- Super Bloco Unificado de Controle (Filtros Globais + Linha do Tempo + Abas de Visão) -->
      <div class="glass-panel unified-control-panel animate-fade-in">
        <!-- 1. Linha Superior: Filtros Globais em Tempo Real & Badge de Atualização -->
        <div class="control-header-row">
          <div class="filters-main-row">
            <!-- Plataforma -->
            <div class="filter-item">
              <label>{{ t('filters.platform', 'Plataforma:') }}</label>
              <div class="toggle-group">
                <button 
                  type="button" 
                  :class="['toggle-btn', { active: selectedPlatform === 'Todas' }]" 
                  @click="selectedPlatform = 'Todas'"
                >
                  🌐 {{ t('filters.both', 'Todas') }}
                </button>
                <button 
                  type="button" 
                  :class="['toggle-btn meli-btn', { active: selectedPlatform === 'meli' }]" 
                  @click="selectedPlatform = 'meli'"
                >
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" class="plat-icon">
                    <circle cx="12" cy="12" r="11" fill="#FFE600"/>
                    <path d="M7 12.5L10.5 15.5L17 8.5" stroke="#2D3277" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  Mercado Livre
                </button>
                <button 
                  type="button" 
                  :class="['toggle-btn shopee-btn', { active: selectedPlatform === 'shopee' }]" 
                  @click="selectedPlatform = 'shopee'"
                >
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" class="plat-icon">
                    <rect width="24" height="24" rx="5" fill="#EE4D2D"/>
                    <path d="M7 9V7C7 4.79086 8.79086 3 11 3H13C15.2091 3 17 4.79086 17 7V9M5 9H19L17.5 21H6.5L5 9Z" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M12 11V15M12 15C11 15 9.5 14.2 9.5 13C9.5 11.8 12 12.2 12 11M12 15C13 15 14.5 15.8 14.5 17" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round"/>
                  </svg>
                  Shopee
                </button>
              </div>
            </div>

            <!-- Categoria -->
            <div class="filter-item flex-1">
              <label>{{ t('filters.category', 'Categoria:') }}</label>
              <select v-model="selectedCategory" class="glass-input">
                <option value="Todas">{{ t('filters.all_categories', 'Todas as Categorias') }}</option>
                <option v-for="cat in dynamicCategories" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </div>

            <!-- Vendas Mínimas -->
            <div class="filter-item">
              <label>{{ t('filters.min_sales', 'Vendas Mín:') }}</label>
              <input type="number" v-model="minSales" :placeholder="t('filters.min_sales_placeholder', 'Ex: 50')" class="glass-input sales-input" />
            </div>

            <!-- Filtro de Visibilidade (Ativos, Todos, Ocultos) -->
            <div class="filter-item">
              <div class="toggle-group-small">
                <button 
                  type="button" 
                  :class="['tog-btn-sm', { active: visibilityStatus === 'active' }]"
                  @click="visibilityStatus = 'active'"
                  :title="t('table.status_active_tooltip', 'Mostrar apenas anúncios ativos')"
                >
                  🟢 {{ t('table.status_active', 'Ativos') }}
                </button>
                <button 
                  type="button" 
                  :class="['tog-btn-sm', { active: visibilityStatus === 'all' }]"
                  @click="visibilityStatus = 'all'"
                  :title="t('table.status_all_tooltip', 'Mostrar todos')"
                >
                  👁️ {{ t('table.status_all', 'Todos') }}
                </button>
                <button 
                  type="button" 
                  :class="['tog-btn-sm', { active: visibilityStatus === 'hidden' }]"
                  @click="visibilityStatus = 'hidden'"
                  :title="t('table.status_hidden_tooltip', 'Mostrar apenas ocultados')"
                >
                  🚫 {{ t('table.status_hidden', 'Ocultos') }}
                </button>
              </div>
            </div>

            <!-- Checkbox Rápido 0 vendas -->
            <div class="filter-item checkboxes-item">
              <label class="checkbox-label">
                <input type="checkbox" v-model="hideZeroSales" />
                {{ t('filters.hide_zero', 'Ocultar 0 vendas') }}
              </label>
            </div>

            <!-- Botão Histograma -->
            <div class="filter-item">
              <button 
                type="button" 
                class="btn-toggle-histogram" 
                @click="showPriceHistogram = !showPriceHistogram"
              >
                📊 {{ showPriceHistogram ? t('filters.hide_price_range', 'Ocultar Faixa de Preços') : t('filters.filter_price_range', 'Filtrar Faixa de Preços') }}
              </button>
            </div>
          </div>

          <div class="header-update-badge" :title="t('filters.daily_info', 'Rotina de raspagem executada automaticamente 1 vez por dia às 22h00')">
            <span>🕒 <strong>{{ t('filters.latest_scrape', 'Última atualização:') }}</strong> {{ lastScrapeFormatted }}</span>
          </div>
        </div>
        
        <!-- Histograma de Preços Expansível -->
        <transition name="slide-fade">
          <div v-if="showPriceHistogram" class="histogram-expand-wrapper">
            <PriceRangeHistogramFilter 
              :items="processedProducts" 
              @filter="(r) => { minPrice = r.min; maxPrice = r.max }" 
            />
          </div>
        </transition>

        <!-- 2. Linha Intermediária: Linha do Tempo e Comparador de Datas Embutido -->
        <TimelineScrapeSelector 
          :rawItems="productsRaw" 
          :embedded="true"
          @select-date="onTimelineSelectDate"
          @compare-dates="onTimelineCompareDates"
        />

        <!-- 3. Linha Inferior: Abas de Navegação das Visões (Posicionadas no final do bloco) -->
        <div class="control-bottom-row">
          <div class="view-tabs-group full-width">
            <button 
              :class="['view-tab-btn', { active: activeViewTab === 'overview' }]" 
              @click="activeViewTab = 'overview'"
            >
              {{ t('tabs.overview', '📊 Visão Geral de Mercado') }}
            </button>
            <button 
              :class="['view-tab-btn', { active: activeViewTab === 'trending' }]" 
              @click="activeViewTab = 'trending'"
            >
              {{ t('tabs.trending', '🚀 Produtos em Alta & Aceleração') }}
            </button>
            <button 
              :class="['view-tab-btn', { active: activeViewTab === 'pricing' }]" 
              @click="activeViewTab = 'pricing'"
            >
              {{ t('tabs.pricing', '🏷️ Estratégias de Preço & Oportunidades') }}
            </button>
          </div>
        </div>
      </div>

      <!-- VISÃO 1: Visão Geral de Mercado (KPIs, Gráficos e Tabela) -->
      <div v-if="activeViewTab === 'overview'" class="overview-layout">
        <!-- SEÇÃO 2: Métricas Financeiras & KPIs -->
        <section class="dashboard-section">
          <div class="section-header">
            <div class="section-title-box">
              <span class="section-badge green">💰 Métricas</span>
              <h3>{{ t('sections.kpi_title', 'Resultados & Métricas Consolidadas') }}</h3>
            </div>
            <p class="section-subtitle">{{ t('sections.kpi_subtitle', 'Resumo dos valores, preços e volume capturados no nicho monitorado.') }}</p>
          </div>
          <KpiCards 
            :totalProducts="totalProducts"
            :averagePrice="averagePrice"
            :topPlatform="topPlatform"
            :topProduct="topProduct"
            :estimatedRevenue="estimatedRevenue"
            :dateRangeText="dateRangeText"
          />
        </section>

        <!-- SEÇÃO 3: Mapeamento Visual de Concorrência & Gráficos -->
        <section class="dashboard-section">
          <div class="section-header">
            <div class="section-title-box">
              <span class="section-badge blue">📊 Concorrência</span>
              <h3>{{ t('sections.charts_title', 'Mapeamento Visual de Concorrência') }}</h3>
            </div>
            <p class="section-subtitle">{{ t('sections.charts_subtitle', 'Distribuição de lojas líderes, faixas de preço e categorias de mercado.') }}</p>
          </div>
          
          <div class="charts-container">
            <!-- Linha 1 de Gráficos: Top Produtos + Barras de Faixa de Preço -->
            <div class="charts-row">
              <TopProductsChart :items="filteredProducts" class="half-width" />
              <PriceVsSalesChart :items="filteredProducts" class="half-width" />
            </div>
            
            <!-- Linha 2 de Gráficos: Vendedores em Destaque (Expandido) -->
            <div class="charts-row">
              <TopSellersChart :items="filteredProducts" class="full-width" />
            </div>

            <!-- Linha 3 de Gráficos: Share de Volume por Categoria -->
            <div class="charts-row">
              <CategoryVolumeChart :items="filteredProducts" class="full-width" />
            </div>
          </div>
        </section>

        <!-- SEÇÃO 4: Catálogo Detalhado de Anúncios -->
        <section class="dashboard-section">
          <div class="section-header">
            <div class="section-title-box">
              <span class="section-badge purple">🔍 Produtos</span>
              <h3>{{ t('sections.table_title', 'Catálogo Completo de Anúncios') }}</h3>
            </div>
            <p class="section-subtitle">{{ t('sections.table_subtitle', 'Detalhamento de cada anúncio coletado com preço, vendedor e link oficial.') }}</p>
          </div>
          <DataTable :items="filteredProducts" @delete-product="onDeleteProduct" class="full-width" />
        </section>
      </div>

      <!-- VISÃO 2: Ranking de Aceleração & Tendências -->
      <div v-else-if="activeViewTab === 'trending'">
        <TrendingProductsTab :products="filteredProducts" />
      </div>

      <!-- VISÃO 3: Monitor de Estratégias de Preço -->
      <div v-else-if="activeViewTab === 'pricing'">
        <PriceStrategyMonitor :products="filteredProducts" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { createClient } from '@supabase/supabase-js'
import Navbar from '~/components/Navbar.vue'
import AntiBotAlert from '~/components/AntiBotAlert.vue'
import KpiCards from '~/components/KpiCards.vue'
import DataTable from '~/components/DataTable.vue'
import TopProductsChart from '~/components/TopProductsChart.client.vue'
import PriceVsSalesChart from '~/components/PriceVsSalesChart.client.vue'
import CategoryVolumeChart from '~/components/CategoryVolumeChart.client.vue'
import TopSellersChart from '~/components/TopSellersChart.client.vue'

import TimelineScrapeSelector from '~/components/TimelineScrapeSelector.vue'
import PriceRangeHistogramFilter from '~/components/PriceRangeHistogramFilter.vue'
import TrendingProductsTab from '~/components/TrendingProductsTab.vue'
import PriceStrategyMonitor from '~/components/PriceStrategyMonitor.vue'
import KeywordsManager from '~/components/KeywordsManager.vue'
import RequestTermModal from '~/components/RequestTermModal.vue'

const supabase = useSupabase()
const toast = useToast()
const { t, locale } = useAppI18n()

// Estados Básicos & Autenticação
const authUser = ref(null)
const productsRaw = ref([])
const loading = ref(true)
const error = ref(null)
const nomeProjeto = ref('SmartDashboard AI')
const statusAlerta = ref(null)

const currentRole = computed(() => {
  if (!authUser.value) return 'basic'
  const appRole = String(authUser.value.app_metadata?.role || '').toLowerCase()
  const userRole = String(authUser.value.user_metadata?.role || '').toLowerCase()
  const directRole = String(authUser.value.role || '').toLowerCase()
  const email = String(authUser.value.email || '').toLowerCase()

  if (appRole === 'admin' || userRole === 'admin' || directRole === 'admin' || email === 'adm@gmail.com') return 'admin'
  if (appRole === 'pro' || userRole === 'pro' || directRole === 'pro' || email === 'marshalfilho@gmail.com' || email === 'isadora@gmail.com') return 'pro'
  return 'basic'
})

const isAdmin = computed(() => currentRole.value === 'admin')
const isPro = computed(() => currentRole.value === 'pro')
const isBasic = computed(() => currentRole.value === 'basic')
const canManageDirectly = computed(() => currentRole.value === 'pro')

const isKeywordsModalOpen = ref(false)
const isRequestTermModalOpen = ref(false)
const adminPendingRequests = ref([])
const adminActiveTab = ref('pending') // 'pending' | 'history'
const adminDecisionHistory = ref([])
const historySearchQuery = ref('')
const historyStatusFilter = ref('all')
const historyCurrentPage = ref(1)
const historyItemsPerPage = ref(6)

const filteredDecisionHistory = computed(() => {
  let list = adminDecisionHistory.value
  if (historyStatusFilter.value !== 'all') {
    list = list.filter(item => item.status === historyStatusFilter.value)
  }
  if (historySearchQuery.value.trim()) {
    const q = historySearchQuery.value.toLowerCase().trim()
    list = list.filter(item => 
      (item.termo && item.termo.toLowerCase().includes(q)) ||
      (item.solicitante_email && item.solicitante_email.toLowerCase().includes(q)) ||
      (item.nicho && item.nicho.toLowerCase().includes(q)) ||
      (item.motivo_recusa && item.motivo_recusa.toLowerCase().includes(q))
    )
  }
  return list
})

const historyTotalPages = computed(() => Math.max(1, Math.ceil(filteredDecisionHistory.value.length / historyItemsPerPage.value)))

const paginatedDecisionHistory = computed(() => {
  const start = (historyCurrentPage.value - 1) * historyItemsPerPage.value
  return filteredDecisionHistory.value.slice(start, start + historyItemsPerPage.value)
})

const isRejectModalOpen = ref(false)
const rejectingRequest = ref(null)
const rejectReason = ref('')

function formatDateShort(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString(locale.value === 'pt' ? 'pt-BR' : 'en-US', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function openRejectModal(req) {
  rejectingRequest.value = req
  rejectReason.value = ''
  isRejectModalOpen.value = true
}

function applyQuickReason(reason) {
  rejectReason.value = reason
}

async function confirmRejectAdminRequest() {
  if (!rejectingRequest.value) return
  const req = rejectingRequest.value
  const motivoRecusa = rejectReason.value.trim() || 'Termo não atende aos critérios de monitoramento do plano'

  try {
    const targetId = req.target_user_id || authUser.value?.id
    const { data: cfg } = await supabase
      .from('configuracoes_scraper')
      .select('regras_categoria')
      .eq('user_id', targetId)
      .limit(1)
      .maybeSingle()

    let rawCategory = cfg?.regras_categoria || {}
    let rateLimit = []

    if (Array.isArray(rawCategory)) {
      rateLimit = rawCategory
    } else if (rawCategory && typeof rawCategory === 'object') {
      rateLimit = Array.isArray(rawCategory.rate_limit) ? rawCategory.rate_limit : []
    }

    const decisionItem = {
      id: req.id || `dec_${Date.now()}`,
      termo: req.termo,
      nicho: req.nicho || '',
      motivo: req.motivo || '',
      solicitante_email: req.solicitante_email || 'Cliente',
      data_solicitacao: req.data_solicitacao || new Date().toISOString(),
      status: 'recusada',
      motivo_recusa: motivoRecusa,
      data_decisao: new Date().toISOString()
    }

    let existingHistory = []
    if (rawCategory && typeof rawCategory === 'object' && Array.isArray(rawCategory.historico_solicitacoes)) {
      existingHistory = [...rawCategory.historico_solicitacoes]
    }
    existingHistory.unshift(decisionItem)

    const updatedCategory = {
      rate_limit: rateLimit,
      solicitacao_pendente: {
        ...req,
        status: 'recusada',
        motivo_recusa: motivoRecusa,
        data_recusa: new Date().toISOString()
      },
      historico_solicitacoes: existingHistory
    }

    await supabase
      .from('configuracoes_scraper')
      .upsert({
        user_id: targetId,
        regras_categoria: updatedCategory,
        updated_at: new Date().toISOString()
      }, { onConflict: 'user_id' })

    adminPendingRequests.value = adminPendingRequests.value.filter(r => r.id !== req.id)
    adminDecisionHistory.value.unshift(decisionItem)
    isRejectModalOpen.value = false
    rejectingRequest.value = null
    toast.info(`Solicitação recusada e motivo enviado ao cliente com sucesso.`, 'Pedido Recusado')
  } catch (err) {
    toast.error('Erro ao recusar solicitação: ' + err.message)
  }
}

async function approveAdminRequest(req) {
  try {
    const targetId = req.target_user_id || authUser.value?.id
    const { data: cfg } = await supabase
      .from('configuracoes_scraper')
      .select('termos_busca, regras_categoria')
      .eq('user_id', targetId)
      .limit(1)
      .maybeSingle()

    const currentTerms = Array.isArray(cfg?.termos_busca) ? [...cfg.termos_busca] : []
    let rawCategory = cfg?.regras_categoria || {}
    let rateLimit = []

    if (Array.isArray(rawCategory)) {
      rateLimit = rawCategory
    } else if (rawCategory && typeof rawCategory === 'object') {
      rateLimit = Array.isArray(rawCategory.rate_limit) ? rawCategory.rate_limit : []
    }

    if (!currentTerms.includes(req.termo)) {
      currentTerms.push(req.termo)
    }

    const decisionItem = {
      id: req.id || `dec_${Date.now()}`,
      termo: req.termo,
      nicho: req.nicho || '',
      motivo: req.motivo || '',
      solicitante_email: req.solicitante_email || 'Cliente',
      data_solicitacao: req.data_solicitacao || new Date().toISOString(),
      status: 'aprovada',
      motivo_recusa: '',
      data_decisao: new Date().toISOString()
    }

    let existingHistory = []
    if (rawCategory && typeof rawCategory === 'object' && Array.isArray(rawCategory.historico_solicitacoes)) {
      existingHistory = [...rawCategory.historico_solicitacoes]
    }
    existingHistory.unshift(decisionItem)

    const updatedCategory = {
      rate_limit: rateLimit,
      solicitacao_pendente: null,
      historico_solicitacoes: existingHistory
    }

    await supabase
      .from('configuracoes_scraper')
      .upsert({
        user_id: targetId,
        termos_busca: currentTerms,
        regras_categoria: updatedCategory,
        updated_at: new Date().toISOString()
      }, { onConflict: 'user_id' })

    adminPendingRequests.value = adminPendingRequests.value.filter(r => r.id !== req.id)
    adminDecisionHistory.value.unshift(decisionItem)
    toast.success(`Termo "${req.termo}" autorizado e adicionado à lista de busca do robô!`, 'Termo Autorizado')
  } catch (err) {
    toast.error('Erro ao autorizar solicitação: ' + err.message)
  }
}

function onKeywordsSaved(payload) {
  if (payload?.blacklist) {
    blacklist.value = payload.blacklist
  }
  loadDashboardData()
}

function handleClientToast(payload) {
  if (payload?.type === 'success') {
    toast.success(payload.message, payload.title)
  } else if (payload?.type === 'error') {
    toast.error(payload.message, payload.title)
  }
}

// Estado das Visões da Dashboard
const activeViewTab = ref('overview') // 'overview', 'trending', 'pricing'
const timelineSelectedDate = ref(null)
const timelineCompareRange = ref(null)

function onTimelineSelectDate(dateStr) {
  timelineCompareRange.value = null
  timelineSelectedDate.value = dateStr
}

function onTimelineCompareDates({ dateA, dateB }) {
  timelineSelectedDate.value = null
  timelineCompareRange.value = { dateA, dateB }
}

// Configurações e Categorias dinâmicas
const blacklist = ref([])
const blockedProducts = ref([]) // Lista de objetos/links de produtos excluídos manualmente
const categoryRules = ref([])

function loadBlockedProducts() {
  const savedBlocked = localStorage.getItem('scraper_blocked_products')
  if (savedBlocked) {
    try {
      blockedProducts.value = JSON.parse(savedBlocked)
    } catch (e) {
      blockedProducts.value = []
    }
  }
}

async function onDeleteProduct(product) {
  const identifier = product.link || product.id || product.titulo
  const existsIndex = blockedProducts.value.findIndex(p => (typeof p === 'string' ? p === identifier : (p.link === product.link || p.id === product.id)))
  
  if (existsIndex === -1) {
    const itemToBlock = {
      id: product.id,
      titulo: product.titulo,
      link: product.link,
      plataforma: product.plataforma,
      preco: product.preco,
      bloqueado_em: new Date().toISOString()
    }
    blockedProducts.value.push(itemToBlock)
  } else {
    blockedProducts.value.splice(existsIndex, 1) // Remove do bloqueio (Restaura)
  }
  
  localStorage.setItem('scraper_blocked_products', JSON.stringify(blockedProducts.value))
  
  // Tenta salvar na nuvem se autenticado
  if (authUser.value) {
    try {
      await supabase.from('configuracoes_scraper').upsert({
        user_id: authUser.value.id,
        blocked_products: blockedProducts.value
      }, { onConflict: 'user_id' })
    } catch (e) {
      console.warn("Erro ao salvar blocked_products no Supabase:", e)
    }
  }
}

function onUpdateBlacklist(list) { blacklist.value = list }
function onUpdateCategories(rules) { categoryRules.value = rules }

// Estado dos Super Filtros
const selectedCategory = ref('Todas')
const selectedPlatform = ref('Todas')
const selectedTimeframe = ref('7') // '7', '15', '30', 'all'
const minPrice = ref(null)
const maxPrice = ref(null)
const minSales = ref(null)
const hideZeroSales = ref(false)
const visibilityStatus = ref('active') // 'active', 'all', 'hidden'
const showPriceHistogram = ref(false)

const defaultCategoryRules = [
  { keyword: 'vela', category: 'Velas de Aniversário' },
  { keyword: 'topo', category: 'Topos de Bolo' },
  { keyword: 'noivinho', category: 'Topos de Bolo' },
  { keyword: 'lembrancinha', category: 'Lembrancinhas' },
  { keyword: 'chaveiro', category: 'Chaveiros' },
  { keyword: 'massa', category: 'Kits & Insumos' },
  { keyword: 'base', category: 'Kits & Insumos' },
  { keyword: 'cortador', category: 'Kits & Insumos' },
  { keyword: 'boneco', category: 'Bonecos & Esculturas' },
  { keyword: 'funko', category: 'Bonecos & Esculturas' },
  { keyword: 'escultura', category: 'Bonecos & Esculturas' }
]

const activeCategoryRules = computed(() => {
  return categoryRules.value && categoryRules.value.length > 0 ? categoryRules.value : defaultCategoryRules
})

const dynamicCategories = computed(() => {
  const cats = new Set(activeCategoryRules.value.map(r => r.category))
  cats.add('Outros')
  return Array.from(cats)
})

function getCategoryByRules(title) {
  const t = (title || '').toLowerCase()
  for (const rule of activeCategoryRules.value) {
    if (t.includes(rule.keyword.toLowerCase())) return rule.category
  }
  return 'Outros'
}

function getHistoricalData(item, daysAgo) {
  if (!item.historico_coletas || item.historico_coletas.length === 0) return null
  if (daysAgo === 'all') {
    return item.historico_coletas[item.historico_coletas.length - 1]
  }

  const targetDate = new Date()
  targetDate.setDate(targetDate.getDate() - parseInt(daysAgo))
  
  let closest = null
  let minDiff = Infinity
  
  const historyToCheck = item.historico_coletas.slice(1)
  if (historyToCheck.length === 0) return null
  
  for (const entry of historyToCheck) {
    const entryDate = new Date(entry.data_coleta)
    const diff = Math.abs(entryDate - targetDate)
    
    if (diff < minDiff && diff <= (parseInt(daysAgo) * 86400000 + 172800000)) {
      minDiff = diff
      closest = entry
    }
  }
  return closest
}

const aiReportData = ref(null)

const lastScrapeFormatted = computed(() => {
  if (!productsRaw.value || productsRaw.value.length === 0) return t('global.no_scrapes', 'Sem registros de raspagem')
  let maxDate = null
  for (const p of productsRaw.value) {
    if (p.criado_em) {
      const d = new Date(p.criado_em)
      if (!maxDate || d > maxDate) maxDate = d
    }
    if (p.historico_coletas && Array.isArray(p.historico_coletas)) {
      for (const h of p.historico_coletas) {
        if (h.data_coleta) {
          const d = new Date(h.data_coleta)
          if (!maxDate || d > maxDate) maxDate = d
        }
      }
    }
  }
  if (!maxDate) return t('global.no_scrapes', 'Sem registros de raspagem')
  const dateLocale = locale.value === 'pt' ? 'pt-BR' : 'en-US'
  const dateFormatted = maxDate.toLocaleDateString(dateLocale, { day: '2-digit', month: '2-digit', year: 'numeric' })
  const hours = String(maxDate.getHours()).padStart(2, '0')
  const minutes = String(maxDate.getMinutes()).padStart(2, '0')
  const atWord = t('global.at', 'às')
  return `${dateFormatted} ${atWord} ${hours}:${minutes}`
})

async function loadDashboardData() {
  try {
    loading.value = true
    error.value = null
    loadBlockedProducts()
    
    // 1. Obtém sessão do usuário logado
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.user) {
      authUser.value = session.user
    }

    // 2. Carrega configurações do tenant
    try {
      let cfgQuery = supabase.from('configuracoes_scraper').select('blocked_products, relatorio_insights, nome_projeto, status_alerta')
      if (authUser.value) {
        cfgQuery = cfgQuery.eq('user_id', authUser.value.id)
      }
      const { data: cfg } = await cfgQuery.limit(1).maybeSingle()
      
      if (cfg) {
        if (cfg.status_alerta) statusAlerta.value = cfg.status_alerta
        if (cfg.relatorio_insights) aiReportData.value = cfg.relatorio_insights
        else aiReportData.value = null
        if (cfg.nome_projeto) nomeProjeto.value = cfg.nome_projeto
        if (cfg.blocked_products && Array.isArray(cfg.blocked_products)) {
          blockedProducts.value = cfg.blocked_products
          localStorage.setItem('scraper_blocked_products', JSON.stringify(cfg.blocked_products))
        }
      } else {
        aiReportData.value = null
        blockedProducts.value = []
      }
    } catch (e) {
      console.warn("Nao foi possivel carregar configuracoes do Supabase:", e)
    }

    // 3. Carrega produtos
    let prodQuery = supabase
      .from('produtos')
      .select(`
        id, plataforma, titulo, link, id_externo, vendedor, criado_em,
        historico_coletas ( preco, vendas_totais, data_coleta )
      `)

    // Se NÃO for admin, filtra pelo usuário específico
    if (authUser.value && !isAdmin.value) {
      prodQuery = prodQuery.eq('user_id', authUser.value.id)
    }
      
    const { data: prodData, error: prodErr } = await prodQuery
    if (prodErr) throw prodErr
    
    if (prodData) {
      productsRaw.value = prodData.map(p => {
        const sortedHistory = p.historico_coletas ? p.historico_coletas.sort((a, b) => new Date(b.data_coleta) - new Date(a.data_coleta)) : []
        const latestHistory = sortedHistory.length > 0 ? sortedHistory[0] : {}
        return {
          id: p.id,
          plataforma: p.plataforma,
          titulo: p.titulo,
          link: p.link,
          vendedor: p.vendedor || null,
          criado_em: p.criado_em,
          preco: latestHistory.preco || 0,
          vendas_totais: latestHistory.vendas_totais || 0,
          historico_coletas: sortedHistory
        }
      })
    }

    // 4. Se for Admin, carrega todas as solicitações pendentes e histórico de todos os clientes
    if (isAdmin.value) {
      try {
        const { data: allCfgs } = await supabase
          .from('configuracoes_scraper')
          .select('user_id, termos_busca, regras_categoria, updated_at')

        if (allCfgs) {
          const pending = []
          const history = []
          for (const cfg of allCfgs) {
            const rawCat = cfg.regras_categoria
            if (rawCat && typeof rawCat === 'object') {
              // Solicitação Pendente (não concluída)
              if (rawCat.solicitacao_pendente && rawCat.solicitacao_pendente.status !== 'aprovada' && rawCat.solicitacao_pendente.status !== 'recusada') {
                const activeCount = Array.isArray(cfg.termos_busca) ? cfg.termos_busca.length : 0
                pending.push({
                  ...rawCat.solicitacao_pendente,
                  target_user_id: cfg.user_id,
                  total_termos_ativos: activeCount,
                  membro_desde: cfg.updated_at || rawCat.solicitacao_pendente.data_solicitacao
                })
              }
              // Histórico de Decisões
              if (Array.isArray(rawCat.historico_solicitacoes)) {
                for (const h of rawCat.historico_solicitacoes) {
                  history.push({
                    ...h,
                    target_user_id: cfg.user_id
                  })
                }
              }
            }
          }
          adminPendingRequests.value = pending
          adminDecisionHistory.value = history.sort((a, b) => new Date(b.data_decisao || b.data_solicitacao) - new Date(a.data_decisao || a.data_solicitacao))
        }
      } catch (e) {
        console.warn('Erro ao carregar solicitacoes para admin:', e)
      }
    }
  } catch (err) {
    console.error(err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function handleAuthChange(user) {
  authUser.value = user
  loadDashboardData()
}

onMounted(() => {
  loadDashboardData()
})

// Texto explicativo do período para os KPIs
const dateRangeText = computed(() => {
  if (productsRaw.value.length === 0) return t('global.loading_dates', 'Carregando datas...')
  
  const dates = []
  for (const p of productsRaw.value) {
    if (p.historico_coletas) {
      for (const h of p.historico_coletas) {
        if (h.data_coleta) dates.push(new Date(h.data_coleta))
      }
    }
  }

  if (dates.length === 0) return t('global.real_time_updates', 'Dados atualizados em tempo real')
  
  const minDate = new Date(Math.min(...dates))
  const maxDate = new Date(Math.max(...dates))
  
  const dateLocale = locale.value === 'pt' ? 'pt-BR' : 'en-US'
  const formatStr = (d) => d.toLocaleDateString(dateLocale)
  const periodName = selectedTimeframe.value === 'all' ? t('global.all_history', 'Todo o Histórico') : t('global.last_days', 'Últimos {days} Dias').replace('{days}', selectedTimeframe.value)

  return `${formatStr(minDate)} ${t('global.until', 'até')} ${formatStr(maxDate)} (${periodName})`
})

// Processa métricas e variações com base no período selecionado
const processedProducts = computed(() => {
  return productsRaw.value
    .map(p => {
      let snapshot = p
      let hist = null
      let varInfo = null
      let salesDiff = null

      if (timelineCompareRange.value) {
        const { dateA, dateB } = timelineCompareRange.value
        const entryA = p.historico_coletas?.find(h => h.data_coleta && h.data_coleta.startsWith(dateA))
        const entryB = p.historico_coletas?.find(h => h.data_coleta && h.data_coleta.startsWith(dateB))
        
        const priceB = entryB ? entryB.preco : p.preco
        const salesB = entryB ? entryB.vendas_totais : p.vendas_totais
        const priceA = entryA ? entryA.preco : p.preco
        const salesA = entryA ? entryA.vendas_totais : 0

        snapshot = { ...p, preco: priceB, vendas_totais: salesB }
        hist = { preco: priceA, vendas_totais: salesA }
        salesDiff = Math.max(0, salesB - salesA)
        if (priceA > 0) {
          const diff = priceB - priceA
          if (Math.abs(diff) > 0.05) {
            varInfo = { diff, perc: (diff / priceA) * 100, isPositive: diff > 0, isNegative: diff < 0 }
          }
        }
      } else if (timelineSelectedDate.value && timelineSelectedDate.value !== 'latest') {
        const histEntry = p.historico_coletas?.find(h => h.data_coleta && h.data_coleta.startsWith(timelineSelectedDate.value))
        if (histEntry) {
          snapshot = { ...p, preco: histEntry.preco, vendas_totais: histEntry.vendas_totais }
        } else {
          snapshot = { ...p, _hiddenByTimeline: true }
        }
        hist = getHistoricalData(snapshot, selectedTimeframe.value)
        if (hist) {
          salesDiff = Math.max(0, snapshot.vendas_totais - hist.vendas_totais)
          if (hist.preco > 0) {
            const diff = snapshot.preco - hist.preco
            if (Math.abs(diff) > 0.05) {
              varInfo = { diff, perc: (diff / hist.preco) * 100, isPositive: diff > 0, isNegative: diff < 0 }
            }
          }
        }
      } else {
        hist = getHistoricalData(p, selectedTimeframe.value)
        if (hist) {
          salesDiff = Math.max(0, p.vendas_totais - hist.vendas_totais)
          if (hist.preco > 0) {
            const diff = p.preco - hist.preco
            if (Math.abs(diff) > 0.05) {
              varInfo = { diff, perc: (diff / hist.preco) * 100, isPositive: diff > 0, isNegative: diff < 0 }
            }
          }
        }
      }

      const createdDate = snapshot.criado_em ? new Date(snapshot.criado_em) : new Date()
      const isNew = (snapshot.historico_coletas && snapshot.historico_coletas.length === 1) || (new Date() - createdDate < 86400000)

      return {
        ...snapshot,
        categoria: getCategoryByRules(snapshot.titulo),
        isNew,
        hist,
        varInfo,
        salesDiff
      }
    })
    .map(p => {
      const isBlocked = blockedProducts.value.some(b => {
        if (!b) return false
        if (typeof b === 'string') return b === p.link || b === p.id || b === p.titulo
        return (b.link && b.link === p.link) || (b.id && b.id === p.id) || (b.titulo && b.titulo === p.titulo)
      })
      if (isBlocked) {
        p._isHidden = true
      }
      return p
    })
    .filter(p => {
      if (p._hiddenByTimeline) return false
      
      const t = p.titulo.toLowerCase()
      if (blacklist.value.some(word => t.includes(word))) return false
      
      return true
    })
    .sort((a, b) => (b.vendas_totais || 0) - (a.vendas_totais || 0))
})

// Aplica os Super Filtros Globais
const filteredProducts = computed(() => {
  let result = processedProducts.value

  if (visibilityStatus.value === 'active') {
    result = result.filter(p => !p._isHidden)
  } else if (visibilityStatus.value === 'hidden') {
    result = result.filter(p => p._isHidden)
  }

  if (selectedCategory.value !== 'Todas') {
    result = result.filter(p => p.categoria === selectedCategory.value)
  }
  if (selectedPlatform.value !== 'Todas') {
    result = result.filter(p => p.plataforma === selectedPlatform.value)
  }
  if (minPrice.value !== null && minPrice.value !== '') {
    result = result.filter(p => p.preco >= Number(minPrice.value))
  }
  if (maxPrice.value !== null && maxPrice.value !== '') {
    result = result.filter(p => p.preco <= Number(maxPrice.value))
  }
  if (minSales.value !== null && minSales.value !== '') {
    result = result.filter(p => (p.vendas_totais || 0) >= Number(minSales.value))
  }
  if (hideZeroSales.value) {
    result = result.filter(p => (p.vendas_totais || 0) > 0)
  }

  return result
})

// KPIs Globais
const totalProducts = computed(() => filteredProducts.value.length)
const averagePrice = computed(() => {
  if (filteredProducts.value.length === 0) return 0
  const validPrices = filteredProducts.value.filter(p => p.preco > 0)
  if (validPrices.length === 0) return 0
  const sum = validPrices.reduce((acc, p) => acc + p.preco, 0)
  return sum / validPrices.length
})
const topPlatform = computed(() => {
  if (filteredProducts.value.length === 0) return ''
  const counts = filteredProducts.value.reduce((acc, p) => {
    acc[p.plataforma] = (acc[p.plataforma] || 0) + 1
    return acc
  }, {})
  return Object.keys(counts).reduce((a, b) => counts[a] > counts[b] ? a : b)
})
const topProduct = computed(() => filteredProducts.value.length > 0 ? filteredProducts.value[0] : null)
const estimatedRevenue = computed(() => filteredProducts.value.reduce((acc, p) => acc + ((p.preco || 0) * (p.vendas_totais || 0)), 0))
</script>

<style scoped>
.filters-panel { padding: 1.5rem; margin-bottom: 2rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05); }
.filters-header { margin-bottom: 1.2rem; }
.filters-header h4 { margin: 0 0 0.2rem 0; color: #0f172a; font-size: 1.15rem; }
.filters-info { color: #64748b; font-size: 0.85rem; }

.filters-grid { display: flex; flex-wrap: wrap; gap: 1.5rem; align-items: flex-end; }
.filter-group { display: flex; flex-direction: column; gap: 0.5rem; }
.filter-group label { color: #475569; font-size: 0.85rem; font-weight: 600; }

.glass-input { background: #ffffff; border: 1px solid #cbd5e1; color: #0f172a; padding: 0.6rem 1rem; border-radius: 8px; outline: none; transition: border 0.3s; font-size: 0.95rem; }
.glass-input:focus { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15); }
.highlight-select { border-color: #93c5fd; background: #eff6ff; font-weight: 600; color: #1e40af; }
.glass-input.tiny { width: 80px; text-align: center; padding: 0.6rem 0.5rem; }

.range-inputs { display: flex; align-items: center; gap: 0.5rem; }
.range-sep { color: #64748b; font-size: 0.85rem; }

.checkbox-group { justify-content: center; height: 100%; padding-bottom: 0.8rem; }
.checkbox-label { display: flex; align-items: center; gap: 0.5rem; cursor: pointer; color: #0f172a !important; font-size: 0.92rem !important; font-weight: 600; }

.content-grid { display: flex; flex-direction: column; gap: 2rem; }
.charts-row { display: flex; gap: 2rem; flex-wrap: wrap; }
.full-width { width: 100%; }
.half-width { flex: 1; min-width: 400px; }

.loading-state, .error-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 40vh; color: #64748b; font-size: 1.2rem; }
.spinner { width: 40px; height: 40px; border: 4px solid #cbd5e1; border-left-color: #2563eb; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1rem; }
@keyframes spin { to { transform: rotate(360deg); } }

.last-update-banner {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1e40af;
  padding: 0.65rem 1.1rem;
  border-radius: 12px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.view-tabs-bar {
  display: flex;
  gap: 0.75rem;
  background: #ffffff;
  padding: 0.6rem;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
}

.tab-btn {
  flex: 1;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #475569;
  padding: 0.75rem 1.2rem;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.92rem;
  cursor: pointer;
  transition: all 0.25 ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.tab-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
  transform: translateY(-1px);
}

.tab-btn.active {
  background: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

.overview-layout {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.dashboard-section {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.25rem;
  box-shadow: 0 4px 15px -2px rgba(15, 23, 42, 0.04);
}

.section-header {
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f1f5f9;
}

.section-title-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.25rem;
}

.section-title-box h3 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 800;
  color: #0f172a;
}

.section-subtitle {
  margin: 0;
  font-size: 0.82rem;
  color: #64748b;
}

.section-badge {
  font-size: 0.75rem;
  font-weight: 800;
  padding: 0.2rem 0.55rem;
  border-radius: 99px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.section-badge.green {
  background: #ecfdf5;
  color: #059669;
  border: 1px solid #a7f3d0;
}

.section-badge.blue {
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}

.section-badge.purple {
  background: #faf5ff;
  color: #7c3aed;
  border: 1px solid #ddd6fe;
}

.charts-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.unified-control-panel {
  padding: 1rem 1.25rem;
  margin-bottom: 1.25rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 16px;
  box-shadow: 0 4px 15px -2px rgba(15, 23, 42, 0.04);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.toggle-group-small {
  display: flex;
  background: #f1f5f9;
  padding: 0.2rem;
  border-radius: 8px;
  gap: 0.2rem;
  border: 1px solid #e2e8f0;
}

.tog-btn-sm {
  border: none;
  background: none;
  padding: 0.35rem 0.6rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 700;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.tog-btn-sm:hover {
  color: #0f172a;
}

.tog-btn-sm.active {
  background: #ffffff;
  color: #0f172a;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}

.control-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  padding-bottom: 0.9rem;
  border-bottom: 1px solid #f1f5f9;
}

.view-tabs-group {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  background: #f8fafc;
  padding: 0.35rem;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.view-tab-btn {
  background: transparent;
  border: 1px solid transparent;
  color: #475569;
  padding: 0.55rem 1.1rem;
  border-radius: 9px;
  font-weight: 700;
  font-size: 0.88rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.view-tab-btn:hover {
  background: #ffffff;
  color: #0f172a;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.view-tab-btn.active {
  background: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
  box-shadow: 0 3px 10px rgba(37, 99, 235, 0.25);
}

.control-bottom-row {
  padding-top: 0.8rem;
  border-top: 1px solid #f1f5f9;
}

.view-tabs-group.full-width {
  display: flex;
  width: 100%;
  gap: 0.5rem;
}

.view-tabs-group.full-width .view-tab-btn {
  flex: 1;
  justify-content: center;
  text-align: center;
  padding: 0.75rem 1rem;
}

.header-update-badge {
  font-size: 0.82rem;
  color: #1e40af;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  padding: 0.45rem 0.9rem;
  border-radius: 99px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.filters-main-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-item label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #475569;
  white-space: nowrap;
}

.flex-1 {
  flex: 1;
  min-width: 200px;
}

.sales-input {
  width: 90px;
}

.checkboxes-item {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.checkbox-label {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.82rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
}

.btn-toggle-histogram {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #334155;
  font-size: 0.82rem;
  font-weight: 700;
  padding: 0.5rem 0.9rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-toggle-histogram:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.histogram-expand-wrapper {
  padding-top: 0.5rem;
  border-top: 1px dashed #e2e8f0;
}

.empty-account-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 3rem 1rem;
}

.empty-account-card {
  max-width: 600px;
  width: 100%;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 2.5rem 2rem;
  text-align: center;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
}

.empty-icon-circle {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  font-size: 2rem;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 auto 1.2rem auto;
}

.empty-account-card h2 {
  margin: 0 0 0.6rem 0;
  font-size: 1.35rem;
  font-weight: 800;
  color: #0f172a;
}

.empty-description {
  margin: 0 0 1.5rem 0;
  font-size: 0.95rem;
  color: #64748b;
  line-height: 1.5;
}

.btn-configure-terms {
  background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%);
  color: #ffffff;
  border: none;
  padding: 0.75rem 1.6rem;
  border-radius: 99px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3);
  transition: all 0.2s ease;
}

.btn-configure-terms:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4);
}

.btn-request-term-large {
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
  color: #ffffff;
  border: none;
  padding: 0.75rem 1.6rem;
  border-radius: 99px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.3);
  transition: all 0.2s ease;
}

.btn-request-term-large:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(2, 132, 199, 0.4);
}

.empty-schedule-box {
  margin-top: 1.8rem;
  padding: 0.8rem 1rem;
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  font-size: 0.82rem;
  color: #475569;
}

/* Painel Exclusivo Admin */
.admin-approval-panel {
  background: #fdf4ff;
  border: 1.5px solid #f0abfc;
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 4px 15px -2px rgba(162, 28, 175, 0.08);
}

.admin-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.admin-badge-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.3rem;
}

.admin-crown-badge {
  font-size: 0.72rem;
  font-weight: 800;
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #fde68a;
  padding: 0.2rem 0.6rem;
  border-radius: 99px;
  letter-spacing: 0.04em;
}

.pending-count-badge {
  font-size: 0.72rem;
  font-weight: 800;
  background: #fae8ff;
  color: #a21caf;
  border: 1px solid #f5d0fe;
  padding: 0.2rem 0.55rem;
  border-radius: 99px;
}

.admin-title-box h3 {
  margin: 0 0 0.2rem 0;
  font-size: 1.15rem;
  font-weight: 800;
  color: #701a75;
}

.admin-subtitle {
  margin: 0;
  font-size: 0.82rem;
  color: #86198f;
}

.btn-manage-terms {
  background: #a21caf;
  color: #ffffff;
  border: none;
  padding: 0.55rem 1.1rem;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(162, 28, 175, 0.25);
  transition: all 0.2s ease;
}

.btn-manage-terms:hover {
  background: #86198f;
  transform: translateY(-1px);
}

.admin-requests-grid {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.admin-request-card {
  background: #ffffff;
  border: 1px solid #f5d0fe;
  border-radius: 12px;
  padding: 0.9rem 1.1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.2rem;
  box-shadow: 0 2px 6px rgba(162, 28, 175, 0.05);
}

.req-card-left {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}

.req-main-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.req-term-title {
  color: #0f172a;
  font-size: 0.95rem;
}

.req-nicho-pill {
  font-size: 0.7rem;
  font-weight: 700;
  background: #f1f5f9;
  color: #475569;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.req-reason-text {
  margin: 0;
  font-size: 0.82rem;
  color: #475569;
  font-style: italic;
}

.req-footer-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.75rem;
  color: #94a3b8;
}

.req-card-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-action-approve {
  background: #059669;
  color: #ffffff;
  border: none;
  padding: 0.45rem 0.9rem;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-action-approve:hover {
  background: #047857;
  transform: translateY(-1px);
}

.btn-action-reject {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #64748b;
  padding: 0.45rem 0.8rem;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-action-reject:hover {
  background: #fee2e2;
  color: #b91c1c;
  border-color: #fca5a5;
}

.user-tier-pill {
  font-size: 0.65rem;
  font-weight: 800;
  background: #e0f2fe;
  color: #0369a1;
  border: 1px solid #bae6fd;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  letter-spacing: 0.04em;
}

.req-footer-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.8rem;
  font-size: 0.78rem;
  color: #64748b;
  margin-top: 0.2rem;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: #f8fafc;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  border: 1px solid #f1f5f9;
}

.reject-summary-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.75rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.85rem;
  color: #334155;
  margin-bottom: 1rem;
}

.quick-reasons-row {
  margin-top: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.chips-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.reason-chip {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #334155;
  padding: 0.35rem 0.7rem;
  border-radius: 99px;
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.reason-chip:hover {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #b91c1c;
}

.btn-confirm-reject {
  background: #dc2626;
  border: 1px solid #b91c1c;
  color: #ffffff;
  padding: 0.6rem 1.2rem;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-confirm-reject:hover:not(:disabled) {
  background: #b91c1c;
  transform: translateY(-1px);
}

.btn-confirm-reject:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.admin-nav-tabs {
  display: flex;
  gap: 0.5rem;
  background: #fdf4ff;
  border: 1px solid #f5d0fe;
  padding: 0.3rem;
  border-radius: 12px;
}

.admin-nav-tab {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: transparent;
  border: none;
  padding: 0.45rem 0.9rem;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 700;
  color: #86198f;
  cursor: pointer;
  transition: all 0.2s ease;
}

.admin-nav-tab:hover {
  background: #fae8ff;
  color: #701a75;
}

.admin-nav-tab.active {
  background: #a21caf;
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(162, 28, 175, 0.25);
}

.tab-counter {
  font-size: 0.7rem;
  font-weight: 800;
  background: #fae8ff;
  color: #a21caf;
  padding: 0.1rem 0.45rem;
  border-radius: 99px;
}

.admin-nav-tab.active .tab-counter {
  background: #ffffff;
  color: #a21caf;
}

.tab-counter.secondary {
  background: #f1f5f9;
  color: #475569;
}

.admin-nav-tab.active .tab-counter.secondary {
  background: #ffffff;
  color: #701a75;
}

/* Histórico Controls */
.history-controls-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.8rem;
  margin-bottom: 1rem;
}

.history-search-box {
  display: flex;
  align-items: center;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.4rem 0.75rem;
  gap: 0.4rem;
  flex: 1;
  max-width: 380px;
}

.history-search-input {
  border: none;
  outline: none;
  font-size: 0.85rem;
  color: #0f172a;
  width: 100%;
  background: transparent;
}

.clear-search-btn {
  background: transparent;
  border: none;
  font-size: 0.8rem;
  color: #94a3b8;
  cursor: pointer;
}

.history-filter-pills {
  display: flex;
  gap: 0.4rem;
}

.history-pill-btn {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  color: #64748b;
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.history-pill-btn:hover {
  background: #f8fafc;
  color: #0f172a;
}

.history-pill-btn.active {
  background: #0f172a;
  color: #ffffff;
  border-color: #0f172a;
}

.history-pill-btn.approved.active {
  background: #059669;
  border-color: #059669;
  color: #ffffff;
}

.history-pill-btn.rejected.active {
  background: #dc2626;
  border-color: #dc2626;
  color: #ffffff;
}

/* History Cards */
.history-items-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.history-item-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1rem 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.history-item-card.aprovada {
  border-left: 4px solid #10b981;
}

.history-item-card.recusada {
  border-left: 4px solid #ef4444;
}

.history-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-term-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.history-term-name {
  font-size: 0.95rem;
  color: #0f172a;
}

.status-badge {
  font-size: 0.68rem;
  font-weight: 800;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  letter-spacing: 0.04em;
}

.status-badge.aprovada {
  background: #dcfce7;
  color: #15803d;
  border: 1px solid #bbf7d0;
}

.status-badge.recusada {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fecdd3;
}

.history-date-badge {
  font-size: 0.75rem;
  color: #94a3b8;
}

.history-item-body {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.history-meta-row {
  display: flex;
  gap: 1.2rem;
  font-size: 0.8rem;
  color: #475569;
}

.history-client-reason {
  margin: 0;
  font-size: 0.82rem;
  color: #64748b;
  font-style: italic;
}

.history-decision-note {
  font-size: 0.82rem;
  padding: 0.5rem 0.8rem;
  border-radius: 8px;
  margin-top: 0.2rem;
}

.history-decision-note.rejected {
  background: #fef2f2;
  border: 1px solid #fee2e2;
  color: #991b1b;
}

.history-decision-note.approved {
  background: #f0fdf4;
  border: 1px solid #dcfce7;
  color: #166534;
}

/* History Pagination */
.history-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 0.75rem;
}

.btn-page {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #334155;
  padding: 0.4rem 0.85rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-page:hover:not(:disabled) {
  background: #f1f5f9;
  color: #0f172a;
}

.btn-page:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-indicator {
  font-size: 0.8rem;
  font-weight: 600;
  color: #64748b;
}

.admin-empty-requests {
  background: #ffffff;
  border: 1px dashed #f0abfc;
  border-radius: 12px;
  padding: 1.2rem;
  display: flex;
  align-items: center;
  gap: 0.9rem;
  color: #701a75;
  font-size: 0.88rem;
}

.empty-icon {
  font-size: 1.5rem;
}

.admin-empty-requests p {
  margin: 0.2rem 0 0 0;
  font-size: 0.8rem;
  color: #86198f;
}
</style>
