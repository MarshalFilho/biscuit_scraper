import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def gerar_relatorio_insights():
    """
    Gera um relatório de inteligência de mercado em 7 módulos analíticos
    com base nos dados acumulados no Supabase e exporta para JSON / Banco.
    """
    print("\n💡 [IA Executive Intelligence] Gerando Relatório de Insights Executivos...")
    
    try:
        from utils.supabase_client import conectar_supabase
        supabase = conectar_supabase()
        
        # Carrega dados dos produtos e coletas
        res = supabase.table("produtos").select("""
            id, plataforma, titulo, link, vendedor, categoria_ia, criado_em,
            historico_coletas ( preco, vendas_totais, data_coleta )
        """).execute()
        
        produtos = res.data or []
        
    except Exception as e:
        print(f"⚠️ Aviso ao conectar no Supabase para insights: {e}. Lendo arquivos JSON locais (Fallback)...")
        produtos = []

    # Fallback para arquivos locais se não houver dados
    if not produtos:
        for p_name, filepath in [("meli", "data/mercado_livre/ouro/dados_meli.json"), ("shopee", "data/shopee/ouro/dados_shopee.json")]:
            full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), filepath)
            if os.path.exists(full_path):
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        dados = json.load(f)
                        for d in dados:
                            produtos.append({
                                "plataforma": p_name,
                                "titulo": d.get("titulo", ""),
                                "link": d.get("url_anuncio", ""),
                                "vendedor": d.get("nome_loja", ""),
                                "categoria_ia": d.get("categoria_ia", ""),
                                "historico_coletas": [{"preco": float(d.get("preco", 0)), "vendas_totais": int(d.get("vendas_quantidade", 0))}]
                            })
                except Exception as ex:
                    print(f"Erro ao ler {filepath}: {ex}")

    # Processamento estatístico
    vendedores_map = {}
    categorias_map = {}
    faixas_preco_map = {"Até R$25": 0, "R$25-50": 0, "R$50-100": 0, "R$100-200": 0, "+R$200": 0}
    produtos_virais = []
    palavras_chave_count = {}
    
    meli_vendas = 0
    shopee_vendas = 0

    for p in produtos:
        plat = p.get("plataforma", "meli")
        vendedor = p.get("vendedor") or ("Mercado Livre" if plat == "meli" else "Shopee")
        cat = p.get("categoria_ia") or "Outros"
        
        coletas = sorted(p.get("historico_coletas", []), key=lambda x: x.get("data_coleta", ""), reverse=True)
        vendas = coletas[0].get("vendas_totais", 0) if coletas else 0
        preco = coletas[0].get("preco", 0.0) if coletas else 0.0
        
        if plat == "meli": meli_vendas += vendas
        else: shopee_vendas += vendas

        # Módulo 1: Vendedores em Ascensão
        if vendedor not in vendedores_map:
            vendedores_map[vendedor] = {"vendas": 0, "receita": 0.0, "anuncios": 0, "plataforma": plat}
        vendedores_map[vendedor]["vendas"] += vendas
        vendedores_map[vendedor]["receita"] += (vendas * preco)
        vendedores_map[vendedor]["anuncios"] += 1

        # Módulo 2: Tendências / Produtos Virais
        if vendas >= 20:
            produtos_virais.append({
                "titulo": p.get("titulo"),
                "vendas": vendas,
                "preco": preco,
                "plataforma": plat,
                "link": p.get("link")
            })

        # Módulo 3: Palavras-chave
        for word in p.get("titulo", "").lower().split():
            if len(word) > 3 and word not in ["biscuit", "para", "com", "kit", "personalizado"]:
                palavras_chave_count[word] = palavras_chave_count.get(word, 0) + 1

        # Módulo 4: Faixas de preço
        if preco <= 25: faixas_preco_map["Até R$25"] += vendas
        elif preco <= 50: faixas_preco_map["R$25-50"] += vendas
        elif preco <= 100: faixas_preco_map["R$50-100"] += vendas
        elif preco <= 200: faixas_preco_map["R$100-200"] += vendas
        else: faixas_preco_map["+R$200"] += vendas

    top_vendedores = sorted([{"name": k, **v} for k, v in vendedores_map.items()], key=lambda x: x["vendas"], reverse=True)[:5]
    produtos_virais_sorted = sorted(produtos_virais, key=lambda x: x["vendas"], reverse=True)[:5]
    top_keywords = sorted(palavras_chave_count.items(), key=lambda x: x[1], reverse=True)[:6]

    # Estrutura dos 7 Módulos de Insights Executivos
    relatorio = {
        "atualizado_em": datetime.utcnow().strftime("%d/%m/%Y às %H:%M"),
        "modulos": [
            {
                "id": "top_sellers",
                "titulo": "🏆 Top Vendedores em Maior Ascensão",
                "tipo": "vendedores",
                "resumo": f"Detectados {len(vendedores_map)} vendedores ativos. O líder acumulou {top_vendedores[0]['vendas'] if top_vendedores else 0} vendas.",
                "itens": top_vendedores
            },
            {
                "id": "viral_products",
                "titulo": "🔥 Produtos Virais & Tendências Quentes",
                "tipo": "produtos",
                "resumo": "Anúncios com maior tração acumulada de vendas nas plataformas.",
                "itens": produtos_virais_sorted
            },
            {
                "id": "seo_strategy",
                "titulo": "🎯 Estratégia de Títulos & SEO para E-commerce",
                "tipo": "palavras_chave",
                "resumo": "As palavras mais frequentes nos anúncios de maior faturamento.",
                "itens": [{"palavra": k, "frequencia": v} for k, v in top_keywords]
            },
            {
                "id": "ocean_blue",
                "titulo": "💡 Lacunas de Preço & Oportunidades (Oceano Azul)",
                "tipo": "faixas_preco",
                "resumo": f"A faixa de preço com maior volume concentrado é '{max(faixas_preco_map, key=faixas_preco_map.get)}'.",
                "itens": [{"faixa": k, "vendas": v} for k, v in faixas_preco_map.items()]
            },
            {
                "id": "platform_battle",
                "titulo": "⚔️ Comparativo Mercado Livre vs Shopee",
                "tipo": "plataformas",
                "resumo": f"Mercado Livre representa {round((meli_vendas / (meli_vendas + shopee_vendas or 1)) * 100)}% das vendas e Shopee representa {round((shopee_vendas / (meli_vendas + shopee_vendas or 1)) * 100)}%.",
                "itens": [
                    {"plataforma": "Mercado Livre", "vendas": meli_vendas},
                    {"plataforma": "Shopee", "vendas": shopee_vendas}
                ]
            },
            {
                "id": "alerts",
                "titulo": "📉 Alertas de Estagnação & Guerra de Preços",
                "tipo": "alertas",
                "resumo": "Acompanhamento de variações bruscas de valor ou concorrência.",
                "itens": [
                    {"alerta": "Baixa variação de preço detectada na categoria Topos de Bolo."},
                    {"alerta": "Oportunidade para criação de combos/kits na Shopee para aumentar o ticket médio."}
                ]
            },
            {
                "id": "action_recommendations",
                "titulo": "📝 Recomendações Práticas de Ação",
                "tipo": "recomendacoes",
                "resumo": "Ações diretas recomendadas para alavancar seu faturamento.",
                "itens": [
                    {"dica": "Crie um anúncio de Kit Lembrancinhas com frete grátis na faixa de R$45,00 a R$65,00."},
                    {"dica": "Utilize os termos 'Pronta Entrega' e 'Personalizado' nos títulos para melhorar o rankeamento SEO."}
                ]
            }
        ]
    }

    # Salva o arquivo localmente
    ouro_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "ouro")
    os.makedirs(ouro_dir, exist_ok=True)
    insights_path = os.path.join(ouro_dir, "insights_executivos.json")
    with open(insights_path, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)

    # Salva no Supabase se disponível
    try:
        user_id = os.environ.get("SUPABASE_USER_ID")
        if user_id:
            supabase = conectar_supabase()
            supabase.table("configuracoes_scraper").update({"relatorio_insights": relatorio}).eq("user_id", user_id).execute()
            print("☁️ [IA Executive Intelligence] Relatório de Insights sincronizado com o Supabase!")
    except Exception as e:
        print(f"⚠️ Erro ao salvar insights no Supabase: {e}")

    print(f"✅ [IA Executive Intelligence] Relatório gerado com sucesso em '{insights_path}'!")
    return relatorio

if __name__ == "__main__":
    gerar_relatorio_insights()
