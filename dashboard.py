import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import sys
import subprocess
import time

# Configurações de caminho
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from config import carregar_config, salvar_config, REPORTS_DIR, DATA_DIR

# Configuração da Página
st.set_page_config(page_title="Biscuit Scraper Pro", layout="wide", page_icon="✨")

# --- INJEÇÃO DE CSS PREMIUM (Light Mode Principal) ---
st.markdown("""
    <style>
    /* Estilo Base: Glassmorphism suave focado no Light Mode (se adapta ao Dark via propriedades nativas do ST) */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 0, 0, 0.1);
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    
    /* Hover effect */
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1), 0 6px 6px rgba(0, 0, 0, 0.05);
        border-color: #FF6B35;
    }
    
    /* Se o usuário mudar o tema do Streamlit para Dark, ajustamos as métricas */
    @media (prefers-color-scheme: dark) {
        div[data-testid="metric-container"] {
            background: rgba(30, 30, 35, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
    }

    .premium-title {
        font-size: 3.5rem;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #FF6B35, #FFC000);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        letter-spacing: -1px;
    }
    
    .premium-subtitle {
        color: #71717A;
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 30px;
    }

    @media (prefers-color-scheme: dark) {
        .premium-subtitle {
            color: #A1A1AA;
        }
    }

    /* Cards da IA */
    .ai-card {
        background: linear-gradient(135deg, rgba(255,107,53,0.1) 0%, rgba(255,192,0,0.1) 100%);
        border-left: 4px solid #FF6B35;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    @media (prefers-color-scheme: dark) {
        .ai-card {
            background: linear-gradient(135deg, rgba(255,107,53,0.05) 0%, rgba(255,192,0,0.05) 100%);
        }
    }
    .ai-card h4 {
        margin-top: 0;
        color: #FF6B35;
    }
    </style>
""", unsafe_allow_html=True)


# Carrega configurações
if 'config' not in st.session_state:
    st.session_state.config = carregar_config()

config = st.session_state.config

def update_config():
    salvar_config(st.session_state.config)
    st.toast('Configurações salvas com sucesso!', icon='✅')

# Funções Modal (Dialogs)
@st.dialog("Editar Termos de Busca")
def dialog_termos():
    st.write("Digite os termos que o robô deve pesquisar nas lojas (um por linha):")
    termos_atuais = "\n".join(st.session_state.config.get("TERMOS_BUSCA", []))
    novos_termos = st.text_area("Termos:", value=termos_atuais, height=300, label_visibility="collapsed")
    if st.button("Salvar Termos", type="primary"):
        st.session_state.config["TERMOS_BUSCA"] = [t.strip() for t in novos_termos.split("\n") if t.strip()]
        update_config()
        st.rerun()

@st.dialog("Editar Palavras Negativas")
def dialog_negativas():
    st.write("Anúncios que contiverem essas palavras serão sumariamente **ignorados**:")
    negativas_atuais = "\n".join(st.session_state.config.get("PALAVRAS_NEGATIVAS", []))
    novas_negativas = st.text_area("Palavras Negativas:", value=negativas_atuais, height=300, label_visibility="collapsed")
    if st.button("Salvar Palavras", type="primary"):
        st.session_state.config["PALAVRAS_NEGATIVAS"] = [n.strip() for n in novas_negativas.split("\n") if n.strip()]
        update_config()
        st.rerun()


def load_data():
    todos_dados = []
    arquivos_json = [
        os.path.join(DATA_DIR, "shopee", "ouro", "dados_shopee.json"),
        os.path.join(DATA_DIR, "mercado_livre", "ouro", "dados_meli.json")
    ]
    for f in arquivos_json:
        if os.path.exists(f):
            with open(f, 'r', encoding='utf-8') as file:
                try:
                    todos_dados.extend(json.load(file))
                except json.JSONDecodeError:
                    pass
    if todos_dados:
        df = pd.DataFrame(todos_dados)
        if "preco" in df.columns:
            df['preco'] = pd.to_numeric(df['preco'], errors='coerce').fillna(0)
        if "vendas_quantidade" in df.columns:
            df['vendas_quantidade'] = pd.to_numeric(df['vendas_quantidade'], errors='coerce').fillna(0)
            
        # Deduplica globalmente pela URL do anúncio (preserva o item com mais vendas)
        if "url_anuncio" in df.columns:
            df = df.sort_values(by="vendas_quantidade", ascending=False)
            df = df.drop_duplicates(subset=["url_anuncio"], keep="first")
            
        return df
    return pd.DataFrame()


def load_insights():
    insights_path = os.path.join(DATA_DIR, "ouro", "insights_executivos.json")
    if os.path.exists(insights_path):
        try:
            with open(insights_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception:
            return None
    return None

# Header com Botão de Modo Escuro Visível
col_head1, col_head2 = st.columns([4, 1])

with col_head1:
    st.markdown("<h1 class='premium-title'>✨ Biscuit Scraper Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p class='premium-subtitle'>Plataforma de inteligência avançada para monitoramento do mercado de Biscuit.</p>", unsafe_allow_html=True)

with col_head2:
    st.write("")
    st.write("")
    modo_escuro = st.toggle("🌙 Modo Escuro", value=False)

if modo_escuro:
    st.markdown("""
        <style>
        .stApp {
            background-color: #121214 !important;
            color: #F4F4F5 !important;
        }
        div[data-testid="metric-container"] {
            background: rgba(30, 30, 35, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        div[data-testid="metric-container"] * {
            color: #F4F4F5 !important;
        }
        .ai-card {
            background: linear-gradient(135deg, rgba(255,107,53,0.15) 0%, rgba(255,192,0,0.15) 100%) !important;
            color: #F4F4F5 !important;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp {
            background-color: #FAFAFA !important;
            color: #18181B !important;
        }
        div[data-testid="metric-container"] {
            background: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid rgba(0, 0, 0, 0.08) !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Criar Tabs (Adicionado Aba de Insights)
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard Analítico", "🧠 Insights da IA", "⚙️ Configurações", "🚀 Centro de Extração"])

# ================================
# TAB 1: VISÃO GERAL (DASHBOARD)
# ================================
with tab1:
    df = load_data()
    
    if df.empty:
        st.info("Nenhum dado encontrado. Vá até o 'Centro de Extração' para buscar os dados das lojas.")
    else:
        # Filtros no Centro da Tela
        with st.expander("🎛️ Filtros Avançados", expanded=False):
            col_f1, col_f2, col_f3 = st.columns(3)
            
            with col_f1:
                loja_selecionada = st.selectbox("Escolha a Loja:", ["Todas", "Mercado Livre", "Shopee"], index=0)
            
            termos = df["termo_busca"].unique().tolist()
            with col_f2:
                termo_selecionado = st.multiselect("Filtrar por Termo", termos, default=termos)
            
            preco_min, preco_max = float(df["preco"].min()), float(df["preco"].max())
            if preco_min == preco_max: preco_min = 0.0
            with col_f3:
                filtro_preco = st.slider("Faixa de Preço (R$)", min_value=preco_min, max_value=preco_max, value=(preco_min, preco_max))
        
        # Filtro de Loja
        if loja_selecionada == "Mercado Livre":
            df_loja = df[df["plataforma"] == "mercado_livre"]
        elif loja_selecionada == "Shopee":
            df_loja = df[df["plataforma"] == "shopee"]
        else:
            df_loja = df.copy()
            
        df_filtrado = df_loja[
            (df_loja["termo_busca"].isin(termo_selecionado)) &
            (df_loja["preco"] >= filtro_preco[0]) & (df_loja["preco"] <= filtro_preco[1])
        ]
        
        # Métricas Premium
        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Anúncios Encontrados", f"{len(df_filtrado)}")
        col2.metric("💰 Preço Médio (R$)", f"R$ {df_filtrado['preco'].mean():.2f}" if len(df_filtrado) > 0 else "R$ 0,00")
        col3.metric("🔥 Total de Vendas Estimadas", f"{df_filtrado['vendas_quantidade'].sum():,}")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        colA, colB = st.columns(2)
        
        # Detecta tema atual do streamlit (Light ou Dark)
        # O plotly por si só já se adapta se deixarmos o template padrão ou o "streamlit"
        
        with colA:
            contagem = df_filtrado["plataforma"].value_counts().reset_index()
            contagem.columns = ["Plataforma", "Quantidade"]
            fig_pie = px.pie(contagem, values="Quantidade", names="Plataforma", title="Market Share (Anúncios por Loja)", hole=0.45, 
                             color_discrete_sequence=["#FF6B35", "#3B82F6", "#4CAF50"])
            fig_pie.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=16)
            fig_pie.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=50, b=10, l=10, r=10))
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with colB:
            vendas_termo = df_filtrado.groupby("termo_busca")["vendas_quantidade"].sum().reset_index()
            vendas_termo = vendas_termo.sort_values(by="vendas_quantidade", ascending=False).head(10)
            fig_bar = px.bar(vendas_termo, x="vendas_quantidade", y="termo_busca", orientation='h', 
                             title="Top 10 Nichos mais Vendidos", color="vendas_quantidade", 
                             color_continuous_scale="Oryel") # Oryel combina com laranja/amarelo
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=50, b=10, l=10, r=10))
            st.plotly_chart(fig_bar, use_container_width=True)
            
        st.subheader("Relação: Preço x Quantidade de Vendas")
        fig_scatter = px.scatter(df_filtrado, x="preco", y="vendas_quantidade", color="plataforma", 
                                 hover_data=["titulo", "termo_busca"], size_max=12, opacity=0.7,
                                 color_discrete_sequence=["#FF6B35", "#3B82F6", "#4CAF50"])
        fig_scatter.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        st.divider()
        st.subheader("Base de Dados Completa")
        
        col_search, col_export = st.columns([4, 1])
        with col_search:
            busca_query = st.text_input("🔍 Pesquisar por título do produto:", placeholder="Digite para filtrar os resultados...")
            
        if busca_query:
            df_final = df_filtrado[df_filtrado["titulo"].str.contains(busca_query, case=False, na=False)]
        else:
            df_final = df_filtrado.copy()
            
        with col_export:
            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exportar CSV",
                data=csv,
                file_name='dados_filtrados_biscuit.csv',
                mime='text/csv',
                use_container_width=True
            )
            
        st.dataframe(
            df_final[["plataforma", "termo_busca", "titulo", "preco", "vendas_quantidade", "url_anuncio"]].sort_values(by="vendas_quantidade", ascending=False),
            use_container_width=True,
            column_config={
                "url_anuncio": st.column_config.LinkColumn("Link Direto"),
                "preco": st.column_config.NumberColumn("Preço (R$)", format="%.2f")
            }
        )

# ================================
# TAB 2: INSIGHTS DA IA
# ================================
with tab2:
    st.markdown("### 🧠 Insights Executivos")
    st.write("Relatórios gerados automaticamente pela Inteligência Artificial após cada varredura.")
    st.divider()
    
    insights = load_insights()
    
    if insights:
        st.caption(f"Última atualização: {insights.get('atualizado_em', 'Desconhecida')}")
        
        modulos = insights.get('modulos', [])
        
        # Renderização dinâmica dos módulos da IA
        for i in range(0, len(modulos), 2):
            col_ia1, col_ia2 = st.columns(2)
            
            mod_1 = modulos[i]
            with col_ia1:
                st.markdown(f"""
                <div class="ai-card">
                    <h4>{mod_1['titulo']}</h4>
                    <p>{mod_1['resumo']}</p>
                </div>
                """, unsafe_allow_html=True)
                if mod_1['tipo'] == 'vendedores':
                    st.dataframe(pd.DataFrame(mod_1['itens']), use_container_width=True)
                elif mod_1['tipo'] in ['produtos', 'palavras_chave']:
                    st.dataframe(pd.DataFrame(mod_1['itens']), use_container_width=True)
                else:
                    st.json(mod_1['itens'])
            
            if i + 1 < len(modulos):
                mod_2 = modulos[i+1]
                with col_ia2:
                    st.markdown(f"""
                    <div class="ai-card">
                        <h4>{mod_2['titulo']}</h4>
                        <p>{mod_2['resumo']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if mod_2['tipo'] == 'faixas_preco':
                        fig = px.bar(pd.DataFrame(mod_2['itens']), x='faixa', y='vendas', color='vendas', color_continuous_scale="Oryel")
                        st.plotly_chart(fig, use_container_width=True)
                    elif mod_2['tipo'] == 'plataformas':
                        fig = px.pie(pd.DataFrame(mod_2['itens']), values='vendas', names='plataforma', hole=0.5, color_discrete_sequence=["#FF6B35", "#3B82F6"])
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        for item in mod_2['itens']:
                            st.info(list(item.values())[0])
            st.write("---")
            
    else:
        st.warning("Nenhum Insight da IA encontrado. Vá até a aba 'Centro de Extração' e rode os scrapers para gerar o primeiro relatório!")


# ================================
# TAB 3: CONFIGURAÇÕES
# ================================
with tab3:
    st.markdown("### ⚙️ Treinamento do Robô")
    st.write("Configure como a plataforma deve buscar os dados na internet.")
    st.divider()
    
    col_c1, col_c2, col_c3 = st.columns(3)
    
    with col_c1:
        st.markdown("#### 🎯 Alvos (Termos de Busca)")
        st.write(f"Atualmente buscando **{len(st.session_state.config.get('TERMOS_BUSCA', []))}** termos.")
        if st.button("✏️ Editar Termos", use_container_width=True):
            dialog_termos()
            
    with col_c2:
        st.markdown("#### 🚫 Filtro Negativo")
        st.write(f"Atualmente bloqueando **{len(st.session_state.config.get('PALAVRAS_NEGATIVAS', []))}** palavras.")
        if st.button("✏️ Editar Palavras Negativas", use_container_width=True):
            dialog_negativas()
            
    with col_c3:
        st.markdown("#### 📄 Profundidade (Páginas)")
        st.write("Quantas páginas navegar em cada busca:")
        
        max_pgs = st.slider("Páginas por termo:", min_value=1, max_value=10, 
                            value=st.session_state.config.get("MAX_PAGINAS", 1), 
                            label_visibility="collapsed")
        
        if max_pgs != st.session_state.config.get("MAX_PAGINAS"):
            st.session_state.config["MAX_PAGINAS"] = max_pgs
            update_config()

# ================================
# TAB 4: EXECUTAR
# ================================
with tab4:
    st.markdown("### 🚀 Iniciar Varredura de Mercado")
    st.write("Inicie os rastreadores web. Eles vão navegar silenciosamente, extrair os dados e acionar a IA no final para cruzar informações.")
    
    plataforma_run = st.radio("Selecione o Alvo:", ["Ambas (Mercado Livre + Shopee)", "Apenas Mercado Livre", "Apenas Shopee"], horizontal=True)
    
    if st.button("▶️ Iniciar Rastreadores Automáticos (IA Incluída)", type="primary", use_container_width=True):
        st.divider()
        
        flag = "--plataforma todos"
        if plataforma_run == "Apenas Mercado Livre": flag = "--plataforma meli"
        elif plataforma_run == "Apenas Shopee": flag = "--plataforma shopee"
            
        cmd = f'"{sys.executable}" -u src/main.py {flag}'
        
        with st.status("🕵️‍♀️ Varrendo as plataformas de e-commerce e rodando Inteligência Artificial...", expanded=True) as status:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, encoding="utf-8", errors="replace")
            
            for linha in process.stdout:
                st.write(linha.strip())
                if "Acessando" in linha or "Termo de busca" in linha or "Processando página" in linha:
                    status.update(label=f"🔄 Processando: {linha.strip()}", state="running")
                elif "IA" in linha or "Insights" in linha:
                    status.update(label=f"🧠 Módulo de Inteligência Artificial: {linha.strip()}", state="running")
                
            process.stdout.close()
            return_code = process.wait()
            
            if return_code == 0:
                status.update(label="🎉 Rastreamento e Geração de Insights Finalizados com Sucesso!", state="complete", expanded=False)
                st.success("Tudo pronto! Vá para a aba '🧠 Insights da IA' para conferir o novo relatório executivo.")
                st.balloons()
            else:
                status.update(label="❌ Ocorreu um erro durante a varredura.", state="error", expanded=True)
                st.error("Verifique os logs acima para entender o que deu errado.")
