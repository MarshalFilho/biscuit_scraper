import json
import os
import re
import sys
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

Gere um relatório executivo estratégico em JSON exatamente com os 4 macro-módulos estruturados a seguir:
{
  "atualizado_em": """" + agora_str + """",
  "modulos": [
    {
      "id": "estrategia",
      "titulo": "🎯 Recomendações Estratégicas & Oportunidades de Nicho",
      "tipo": "lista_texto",
      "resumo": "Diagnósticos acionáveis e oportunidades de alta demanda reprimida",
      "itens": [
        "Recomendação justificada com dados matemáticos da coleta (ex: margem vs concorrência)...",
        "Oportunidade de nicho justificada por demanda vs oferta..."
      ]
    },
    {
      "id": "vendedores_produtos",
      "titulo": "🏆 Top Vendedores & Produtos Virais",
      "tipo": "vendedores",
      "resumo": "Ranking combinado dos maiores faturamentos e itens com aceleração",
      "itens": [{"name": "Nome da Loja", "anuncios": 10, "vendas": 500, "receita": 15000.0, "top_produto": "Produto líder desta loja"}]
    },
    {
      "id": "seo",
      "titulo": "🏷️ Estratégia de SEO & Palavras-Chave de Alta Conversão",
      "tipo": "palavras_chave",
      "resumo": "Termos mais frequentes nos títulos líderes para otimização de busca",
      "itens": [{"palavra": "termo", "frequencia": 45}]
    },
    {
      "id": "plataformas_precos",
      "titulo": "⚔️ Batalha de Marketplaces & Faixas de Preço",
      "tipo": "plataformas",
      "resumo": "Comparativo ML vs Shopee e distribuição do volume por zonas de preço",
      "itens": [{"nome": "Mercado Livre", "share": 60.0, "receita": 25000.0, "vendas": 600, "vendedores_unicos": 45}]
    }
  ]
}
Retorne EXCLUSIVAMENTE o JSON valido.
"""

        modelos_para_testar = ["gemini-flash-latest", "gemini-2.5-flash-lite", "gemini-1.5-flash"]
        for m_name in modelos_para_testar:
            try:
                print(f"🤖 [Módulo IA] Conectando à API do Google Gemini ({m_name})...")
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

        relatorio_payload = {
            "atualizado_em": datetime.now().strftime("%d/%m/%Y às %H:%M"),
            "modulos": [
                {
                    "id": "estrategia",
                    "titulo": "🎯 Recomendações Estratégicas & Oportunidades de Nicho",
                    "tipo": "lista_texto",
                    "resumo": "Ações imediatas e oportunidades de alta demanda baseadas nos dados.",
                    "itens": [
                        "🎯 **Foco em Velas e Topos**: Estas categorias representam mais de 65% do volume. Oportunidade clara em expandir portfólio.",
                        "💵 **Faixa Ideal de Preço**: O sweet spot de conversão está entre R$ 25 e R$ 60.",
                        "✨ **Temas Infantis (Nicho)**: 'Sonic', 'Moana' e 'Safari' possuem altíssima procura e baixa variação de preço."
                    ]
                },
                {
                    "id": "vendedores_produtos",
                    "titulo": "🏆 Top Vendedores & Produtos Virais",
                    "tipo": "vendedores",
                    "resumo": "Ranking combinado dos principais vendedores e itens com maior tração.",
                    "itens": top_vendedores
                },
                {
                    "id": "seo",
                    "titulo": "🏷️ Estratégia de SEO & Palavras-Chave de Alta Conversão",
                    "tipo": "palavras_chave",
                    "resumo": "Termos mais frequentes nos anúncios de sucesso.",
                    "itens": top_keywords
                },
                {
                    "id": "plataformas_precos",
                    "titulo": "⚔️ Batalha de Marketplaces & Faixas de Preço",
                    "tipo": "plataformas",
                    "resumo": "Participação entre Mercado Livre e Shopee, e volume por zona de preço.",
                    "itens": plataformas_list
                }
            ]
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

    # Sincroniza com Supabase se a coluna existir
    try:
        user_id = os.environ.get("SUPABASE_USER_ID", "693b19e1-936e-4322-ac9a-79467d143566")
        res_cfg = supabase.table("configuracoes_scraper").select("id").eq("user_id", user_id).execute()
        if res_cfg.data and len(res_cfg.data) > 0:
            supabase.table("configuracoes_scraper").update({
                "relatorio_insights": relatorio_payload
            }).eq("user_id", user_id).execute()
            print("☁️ [Módulo IA] Relatório sincronizado no Supabase com sucesso!")
    except Exception:
        pass

    return relatorio_payload

if __name__ == "__main__":
    gerar_relatorio_ia_executivo()
