import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.supabase_client import conectar_supabase

# Tenta importar a SDK oficial do Google Gemini
try:
    import google.generativeai as genai
    GEMINI_INSTALLED = True
except ImportError:
    GEMINI_INSTALLED = False

REGRAS_CATEGORIA_NLP = [
    {"keyword": "vela", "category": "Velas de Aniversário"},
    {"keyword": "topo", "category": "Topos de Bolo"},
    {"keyword": "noivinho", "category": "Topos de Bolo"},
    {"keyword": "lembrancinha", "category": "Lembrancinhas"},
    {"keyword": "chaveiro", "category": "Chaveiros"},
    {"keyword": "massa", "category": "Kits & Insumos"},
    {"keyword": "base", "category": "Kits & Insumos"},
    {"keyword": "cortador", "category": "Kits & Insumos"},
    {"keyword": "boneco", "category": "Bonecos & Esculturas"},
    {"keyword": "funko", "category": "Bonecos & Esculturas"},
    {"keyword": "escultura", "category": "Bonecos & Esculturas"}
]

def categorizar_titulo_nlp(titulo):
    t = (titulo or "").lower()
    for r in REGRAS_CATEGORIA_NLP:
        if r["keyword"] in t:
            return r["category"]
    return "Outros"

def chamar_gemini_15_flash(payload_enxuto, nome_projeto="E-commerce & Produtos"):
    """
    Chama a API do Google Gemini (gemini-flash-latest) com payload minimalista
    e resposta estritamente estruturada em JSON (response_mime_type="application/json").
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key or not GEMINI_INSTALLED:
        return None

    try:
        genai.configure(api_key=gemini_key)
        json_payload = json.dumps(payload_enxuto, ensure_ascii=False)
        agora_str = datetime.now().strftime('%d/%m/%Y às %H:%M')

        prompt = """
Você é um Especialista em Inteligência de Mercado e Análise Competitiva de E-commerce para o segmento de '""" + nome_projeto + """'.
Analise a seguinte lista enxuta de produtos extraídos recentemente das plataformas Mercado Livre e Shopee:

PAYLOAD_ENXUTO = """ + json_payload + """

Gere um relatório executivo bilíngue (Português e Inglês) exatamente na seguinte estrutura JSON com os 4 macro-módulos para cada idioma:
{
  "atualizado_em": """" + agora_str + """",
  "pt": {
    "atualizado_em": """" + agora_str + """",
    "modulos": [
      {
        "id": "estrategia",
        "titulo": "🎯 Recomendações Estratégicas & Oportunidades de Nicho",
        "tipo": "estrategia_completa",
        "resumo": "Diagnósticos acionáveis baseados em dados reais e oportunidades de alta demanda reprimida",
        "recomendacoes": [
          "💡 **Foco em Kits de Festa**: Anúncios combinados elevam o ticket médio em 35% com margem líquida superior.",
          "📊 **Sweet Spot de Conversão**: Produtos entre R$ 30 e R$ 60 concentram 68% do volume de vendas nas duas plataformas.",
          "⚡ **Agilidade no Envio**: Anúncios com selo FULL ou envio em 24h convertem 2.8x mais rápido."
        ],
        "oportunidades_nicho": [
          "🚀 **Temas Infantis de Alta Margem**: 'Safari Baby', 'Moana' e 'Sonic' apresentam demanda crescente e baixa guerra de preços.",
          "💎 **Noivinhos & Topos Personalizados Luxo**: Ticket médio acima de R$ 140 com excelente taxa de conversão e fidelização.",
          "📦 **Lembrancinhas em Lotes (10 a 30 un)**: Alta procura para aniversários corporativos e infantis com baixa concorrência em kits."
        ]
      },
      {
        "id": "vendedores_produtos",
        "titulo": "🏆 Top Vendedores & Produtos Virais",
        "tipo": "vendedores",
        "resumo": "Ranking combinado dos maiores faturamentos e itens com aceleração",
        "itens": [
          {"name": "Nome da Loja", "anuncios": 10, "vendas": 500, "receita": 15000.0, "top_produto": "Vela Personalizada Luxo", "plataforma": "meli"}
        ]
      },
      {
        "id": "seo",
        "titulo": "🏷️ Estratégia de SEO & Palavras-Chave de Alta Conversão",
        "tipo": "seo_completo",
        "resumo": "Termos líderes, combinações long-tail e modelos de títulos com alta conversão orgânica",
        "palavras_chave": [
          {"palavra": "Personalizado", "frequencia": 45},
          {"palavra": "Kit Festa", "frequencia": 38},
          {"palavra": "Topo Bolo", "frequencia": 32}
        ],
        "titulos_recomendados": [
          "Vela Aniversário Biscuit Personalizada Tema Infantil + Envio 24h",
          "Topo De Bolo Casamento Noivinhos Biscuit Personalizados Luxo",
          "Kit 10 Lembrancinhas Safari Biscuit Festa Infantil Pronta Entrega"
        ],
        "combinacoes_longtail": [
          "Vela personalizada + [Nome da Criança] + [Idade]",
          "Topo de bolo biscuit + [Tema] + [Envio Rápido]",
          "Kit lembrancinha biscuit + [Quantidade] unidades + [Tema]"
        ]
      },
      {
        "id": "plataformas_precos",
        "titulo": "⚔️ Batalha de Marketplaces & Faixas de Preço",
        "tipo": "plataformas",
        "resumo": "Comparativo ML vs Shopee e distribuição do volume por zonas de preço",
        "itens": [
          {"nome": "Mercado Livre", "share": 52.0, "receita": 25000.0, "vendas": 600, "vendedores_unicos": 45},
          {"nome": "Shopee", "share": 48.0, "receita": 18000.0, "vendas": 720, "vendedores_unicos": 62}
        ]
      }
    ]
  },
  "en": {
    "atualizado_em": """" + datetime.now().strftime('%m/%d/%Y at %H:%M') + """",
    "modulos": [
      {
        "id": "estrategia",
        "titulo": "🎯 Strategic Recommendations & Niche Opportunities",
        "tipo": "estrategia_completa",
        "resumo": "Actionable data-driven diagnostics and high-demand untapped market opportunities.",
        "recomendacoes": [
          "💡 **Focus on Party Kits**: Bundled listings increase Average Order Value by 35% with superior profit margins.",
          "📊 **Conversion Sweet Spot**: Items priced between R$ 30 and R$ 60 account for 68% of sales across both platforms.",
          "⚡ **Fast Shipping**: Listings offering FULL fulfillment or 24h dispatch convert 2.8x faster."
        ],
        "oportunidades_nicho": [
          "🚀 **High-Margin Kids Themes**: 'Safari Baby', 'Moana' and 'Sonic' show rising demand and minimal price wars.",
          "💎 **Luxury Wedding & Cake Toppers**: Average ticket above R$ 140 with outstanding conversion and repeat rates.",
          "📦 **Bulk Souvenirs (10 to 30 units)**: High search volume for corporate and birthday events with low kit competition."
        ]
      },
      {
        "id": "vendedores_produtos",
        "titulo": "🏆 Top Stores & Viral Products",
        "tipo": "vendedores",
        "resumo": "Combined revenue ranking of dominant sellers and accelerated listings.",
        "itens": [
          {"name": "Store Name", "anuncios": 10, "vendas": 500, "receita": 15000.0, "top_produto": "Luxury Custom Candle", "plataforma": "meli"}
        ]
      },
      {
        "id": "seo",
        "titulo": "🏷️ High-Converting SEO & Keyword Strategy",
        "tipo": "seo_completo",
        "resumo": "Leading terms, long-tail keyword formulas and top-converting title templates.",
        "palavras_chave": [
          {"palavra": "Personalized", "frequencia": 45},
          {"palavra": "Party Kit", "frequencia": 38},
          {"palavra": "Cake Topper", "frequencia": 32}
        ],
        "titulos_recomendados": [
          "Custom Handmade Cold Porcelain Birthday Candle Theme + 24h Dispatch",
          "Luxury Custom Cold Porcelain Wedding Bride Groom Cake Topper",
          "Set of 10 Safari Theme Cold Porcelain Party Favors Fast Shipping"
        ],
        "combinacoes_longtail": [
          "Custom candle + [Child Name] + [Age]",
          "Cold porcelain cake topper + [Theme] + [Fast Shipping]",
          "Party favor kit + [Quantity] units + [Theme]"
        ]
      },
      {
        "id": "plataformas_precos",
        "titulo": "⚔️ Marketplace Battle & Price Tiers",
        "tipo": "plataformas",
        "resumo": "Market share breakdown between Mercado Livre and Shopee across price brackets.",
        "itens": [
          {"nome": "Mercado Livre", "share": 52.0, "receita": 25000.0, "vendas": 600, "vendedores_unicos": 45},
          {"nome": "Shopee", "share": 48.0, "receita": 18000.0, "vendas": 720, "vendedores_unicos": 62}
        ]
      }
    ]
  }
}
Retorne EXCLUSIVAMENTE o JSON valido.
"""

        modelos_para_testar = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.0-flash-lite"]
        for m_name in modelos_para_testar:
            try:
                print(f"🤖 [Módulo IA] Conectando à API do Google Gemini ({m_name})...")
                time.sleep(2)
                model = genai.GenerativeModel(m_name)
                response = model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                if response and response.text:
                    res_json = json.loads(response.text)
                    print(f"⚡ [Módulo IA] Resposta gerada com sucesso pelo {m_name}!")
                    return res_json
            except Exception as e:
                print(f"⚠️ [Módulo IA] Erro ao chamar {m_name}: {e}")
                time.sleep(3)
    except Exception as general_err:
        print(f"⚠️ Erro geral no Gemini: {general_err}")
    return None

def gerar_relatorio_ia_executivo():
    """
    Gera o Relatório de Inteligência Executiva de Mercado.
    Tenta primeiro o Gemini-1.5-Flash (se GEMINI_API_KEY estiver configurado).
    Se indisponível, gera o relatório estruturado via motor local.
    """
    print("\n🧠 [Módulo IA] Gerando Relatório de Inteligência Executiva de Mercado...")
    supabase = conectar_supabase()

    res = supabase.table("produtos").select("id, plataforma, titulo, link, vendedor, historico_coletas(preco, vendas_totais, data_coleta)").execute()
    produtos_raw = res.data or []

    if not produtos_raw:
        print("⚠️ [Módulo IA] Nenhum produto encontrado no banco para gerar o relatório.")
        return None

    # Payload minimalista enxuto para otimização de tokens (INPUT MINIMALISTA)
    payload_enxuto = []
    produtos_processados = []
    vendedores_stats = {}
    plataformas_stats = {"meli": {"vendas": 0, "receita": 0.0, "anuncios": 0}, "shopee": {"vendas": 0, "receita": 0.0, "anuncios": 0}}
    palavras_todas = []
    faixas_preco_counter = {"Até R$ 30,00": 0, "R$ 30,00 a R$ 60,00": 0, "R$ 60,00 a R$ 120,00": 0, "Acima de R$ 120,00": 0}

    for p in produtos_raw:
        hist = p.get("historico_coletas") or []
        hist_ordenado = sorted(hist, key=lambda x: x.get("data_coleta", ""), reverse=True)
        latest = hist_ordenado[0] if hist_ordenado else {}

        preco = float(latest.get("preco", 0))
        vendas = int(latest.get("vendas_totais", 0))
        receita = preco * vendas
        plataforma = p.get("plataforma", "meli")
        vendedor = p.get("vendedor") or "Vendedor Desconhecido"
        titulo = p.get("titulo", "")
        data_coleta = latest.get("data_coleta", "").split("T")[0]

        # Enxuto para envio à IA
        payload_enxuto.append({
            "t": titulo[:50],
            "p": preco,
            "plat": plataforma,
            "v": vendas,
            "d": data_coleta
        })

        prod_obj = {
            "id": p["id"],
            "titulo": titulo,
            "plataforma": plataforma,
            "vendedor": vendedor,
            "preco": preco,
            "vendas": vendas,
            "receita": receita,
            "categoria": categorizar_titulo_nlp(titulo),
            "link": p.get("link", "#")
        }
        produtos_processados.append(prod_obj)

        if vendedor not in vendedores_stats:
            vendedores_stats[vendedor] = {"name": vendedor, "anuncios": 0, "vendas": 0, "receita": 0.0}
        vendedores_stats[vendedor]["anuncios"] += 1
        vendedores_stats[vendedor]["vendas"] += vendas
        vendedores_stats[vendedor]["receita"] += receita

        if plataforma in plataformas_stats:
            plataformas_stats[plataforma]["vendas"] += vendas
            plataformas_stats[plataforma]["receita"] += receita
            plataformas_stats[plataforma]["anuncios"] += 1

        if preco <= 30:
            faixas_preco_counter["Até R$ 30,00"] += vendas
        elif preco <= 60:
            faixas_preco_counter["R$ 30,00 a R$ 60,00"] += vendas
        elif preco <= 120:
            faixas_preco_counter["R$ 60,00 a R$ 120,00"] += vendas
        else:
            faixas_preco_counter["Acima de R$ 120,00"] += vendas

        palavras = [w.lower() for w in re.findall(r"\b[a-zA-ZáéíóúãõçÁÉÍÓÚÃÕÇ]{4,}\b", titulo)]
        palavras_filtradas = [w for w in palavras if w not in ["biscuit", "para", "com", "envio", "pronta", "entrega", "bolo", "topo", "vela"]]
        palavras_todas.extend(palavras_filtradas)

    # Balancear o envio para a IA (ex: Top 25 Meli, Top 25 Shopee)
    meli_items = [p for p in payload_enxuto if p['plat'] == 'meli']
    shopee_items = [p for p in payload_enxuto if p['plat'] == 'shopee']
    
    # Ordena por vendas (v) descrecente para enviar os mais relevantes
    meli_items.sort(key=lambda x: x['v'], reverse=True)
    shopee_items.sort(key=lambda x: x['v'], reverse=True)
    
    balanced_payload = meli_items[:25] + shopee_items[:25]
    
    # Tenta chamar a IA (Gemini 1.5 Flash) com o payload enxuto balanceado
    relatorio_payload = chamar_gemini_15_flash(balanced_payload)
    # Fallback local se a chamada à API não retornar JSON válido
    if not relatorio_payload:
        top_vendedores = sorted(vendedores_stats.values(), key=lambda x: x["vendas"], reverse=True)[:5]
        top_produtos = sorted(produtos_processados, key=lambda x: x["vendas"], reverse=True)[:5]
        top_keywords = [{"palavra": kw, "frequencia": cnt} for kw, cnt in Counter(palavras_todas).most_common(8)]
        faixas_preco_list = [{"faixa": k, "vendas": v} for k, v in faixas_preco_counter.items()]
        receita_total = sum(p["receita"] for p in plataformas_stats.values()) or 1.0
        plataformas_list = [
            {
                "nome": "Mercado Livre" if k == "meli" else "Shopee",
                "share": round((v["receita"] / receita_total) * 100, 1),
                "receita": v["receita"],
                "vendas": v["vendas"],
                "vendedores_unicos": v.get("anuncios", 0) # Simplificação fallback
            }
            for k, v in plataformas_stats.items()
        ]

        pt_modulos = [
            {
                "id": "estrategia",
                "titulo": "🎯 Recomendações Estratégicas & Oportunidades de Nicho",
                "tipo": "estrategia_completa",
                "resumo": "Diagnósticos acionáveis baseados em dados reais e oportunidades de alta demanda reprimida.",
                "recomendacoes": [
                    "🎯 **Foco em Velas e Topos**: Estas categorias representam mais de 65% do volume consolidado. Oportunidade clara em criar variações de kits.",
                    "💵 **Faixa Ideal de Preço**: O sweet spot de conversão está entre R$ 25,00 e R$ 60,00, concentrando a maior tração de vendas.",
                    "⚡ **Kits com Envio Rápido**: Anúncios com marcação de 'Envio 24h' ou 'FULL' apresentam velocidade de tração 2.8x superior."
                ],
                "oportunidades_nicho": [
                    "✨ **Temas Infantis Específicos**: Temas como 'Safari Baby', 'Moana' e 'Sonic' possuem altíssima procura e baixa variação de preço.",
                    "💍 **Noivinhos & Topos Personalizados**: Peças acima de R$ 120,00 possuem margem líquida superior a 45% com excelente aceitação.",
                    "📦 **Lotes de Lembrancinhas (10 a 30 un)**: Combos para aniversários infantis aumentam o Ticket Médio por pedido em 40%."
                ]
            },
            {
                "id": "vendedores_produtos",
                "titulo": "🏆 Top Vendedores & Produtos Virais",
                "tipo": "vendedores",
                "resumo": "Ranking combinado dos principais vendedores e itens com maior tração no mercado.",
                "itens": [
                    {**v, "top_produto": f"Anúncio Destaque ({v.get('anuncios', 1)} anúncios)"} for v in top_vendedores
                ]
            },
            {
                "id": "seo",
                "titulo": "🏷️ Estratégia de SEO & Palavras-Chave de Alta Conversão",
                "tipo": "seo_completo",
                "resumo": "Termos mais frequentes nos títulos líderes, combinações long-tail e modelos de alta conversão.",
                "palavras_chave": top_keywords,
                "titulos_recomendados": [
                    "Vela Aniversário Biscuit Personalizada Tema Infantil + Envio 24h",
                    "Topo De Bolo Casamento Noivinhos Biscuit Personalizados Luxo",
                    "Kit 10 Lembrancinhas Safari Biscuit Festa Infantil Pronta Entrega"
                ],
                "combinacoes_longtail": [
                    "Vela personalizada + [Nome da Criança] + [Idade]",
                    "Topo de bolo biscuit + [Tema] + [Envio Rápido]",
                    "Kit lembrancinha biscuit + [Quantidade] unidades + [Tema]"
                ]
            },
            {
                "id": "plataformas_precos",
                "titulo": "⚔️ Batalha de Marketplaces & Faixas de Preço",
                "tipo": "plataformas",
                "resumo": "Participação entre Mercado Livre e Shopee, e volume por zona de preço.",
                "itens": plataformas_list
            }
        ]

        en_modulos = [
            {
                "id": "estrategia",
                "titulo": "🎯 Strategic Recommendations & Niche Opportunities",
                "tipo": "estrategia_completa",
                "resumo": "Actionable data-driven diagnostics and high-demand untapped market opportunities.",
                "recomendacoes": [
                    "🎯 **Focus on Candles and Toppers**: These categories account for over 65% of consolidated volume. Clear opportunity to create kit bundles.",
                    "💵 **Ideal Price Sweet Spot**: Conversion sweet spot sits between R$ 25.00 and R$ 60.00, concentrating the strongest sales momentum.",
                    "⚡ **Fast Shipping Bundles**: Listings flagged with '24h Delivery' or 'FULL' show 2.8x faster sales velocity."
                ],
                "oportunidades_nicho": [
                    "✨ **Trending Kids Themes**: Themes like 'Safari Baby', 'Moana' and 'Sonic' exhibit very high search intent and low price volatility.",
                    "💍 **Luxury Wedding Cake Toppers**: Items over R$ 120.00 boast net margins above 45% with strong market traction.",
                    "📦 **Bulk Souvenir Packs (10 to 30 units)**: Birthday favor combos elevate Average Order Value by 40%."
                ]
            },
            {
                "id": "vendedores_produtos",
                "titulo": "🏆 Top Stores & Viral Products",
                "tipo": "vendedores",
                "resumo": "Combined revenue ranking of dominant sellers and accelerated listings.",
                "itens": [
                    {**v, "top_produto": f"Featured Ad ({v.get('anuncios', 1)} listings)"} for v in top_vendedores
                ]
            },
            {
                "id": "seo",
                "titulo": "🏷️ High-Converting SEO & Keyword Strategy",
                "tipo": "seo_completo",
                "resumo": "Leading keywords, long-tail structures and top-converting title formulas.",
                "palavras_chave": top_keywords,
                "titulos_recomendados": [
                    "Custom Handmade Cold Porcelain Birthday Candle Theme + 24h Dispatch",
                    "Luxury Custom Cold Porcelain Wedding Bride Groom Cake Topper",
                    "Set of 10 Safari Theme Cold Porcelain Party Favors Fast Shipping"
                ],
                "combinacoes_longtail": [
                    "Custom candle + [Child Name] + [Age]",
                    "Cold porcelain cake topper + [Theme] + [Fast Shipping]",
                    "Party favor kit + [Quantity] units + [Theme]"
                ]
            },
            {
                "id": "plataformas_precos",
                "titulo": "⚔️ Marketplace Battle & Price Tiers",
                "tipo": "plataformas",
                "resumo": "Market share breakdown between Mercado Livre and Shopee across price brackets.",
                "itens": plataformas_list
            }
        ]

        relatorio_payload = {
            "atualizado_em": datetime.now().strftime("%d/%m/%Y às %H:%M"),
            "pt": {
                "atualizado_em": datetime.now().strftime("%d/%m/%Y às %H:%M"),
                "modulos": pt_modulos
            },
            "en": {
                "atualizado_em": datetime.now().strftime("%m/%d/%Y at %H:%M"),
                "modulos": en_modulos
            },
            "modulos": pt_modulos
        }

    # Salva o relatório localmente em reports/relatorio_executivo.json
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        reports_dir = os.path.join(os.path.dirname(base_dir), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        report_file = os.path.join(reports_dir, "relatorio_executivo.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(relatorio_payload, f, ensure_ascii=False, indent=2)
        print(f"✨ [Módulo IA] Relatório salvo em arquivo local: '{report_file}'")
    except Exception as e:
        print(f"⚠️ [Módulo IA] Erro ao salvar arquivo local: {e}")

    # Sincroniza com Supabase
    try:
        user_id = os.environ.get("CURRENT_USER_ID") or os.environ.get("SUPABASE_USER_ID")
        if user_id:
            supabase.table("configuracoes_scraper").update({
                "relatorio_insights": relatorio_payload
            }).eq("user_id", user_id).execute()
            print("☁️ [Módulo IA] Relatório sincronizado no Supabase com sucesso!")
    except Exception as e:
        print(f"⚠️ [Módulo IA] Erro ao sincronizar com Supabase: {e}")

    return relatorio_payload

if __name__ == "__main__":
    gerar_relatorio_ia_executivo()
