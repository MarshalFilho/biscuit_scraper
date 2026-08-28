export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const niche = body?.niche || 'Biscuit e Artesanato'
  const currentTerms = body?.currentTerms || []
  const blacklist = body?.blacklist || []
  const maxSuggestions = body?.maxSuggestions || 8

  const config = useRuntimeConfig()
  const geminiKey = config.geminiApiKey || process.env.GEMINI_API_KEY

  if (geminiKey) {
    const models = ['gemini-3.6-flash', 'gemini-3.5-flash-lite', 'gemini-2.5-flash']
    for (const modelName of models) {
      try {
        const url = `https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent?key=${geminiKey}`
        const prompt = `
Você é um Especialista Sênior em Inteligência de Mercado e SEO para E-commerce (Mercado Livre e Shopee).
O usuário deseja expandir seus termos de monitoramento de vendas para o seu nicho.

NICHO DO USUÁRIO: "${niche}"
TERMOS JÁ MONITORADOS: ${JSON.stringify(currentTerms)}
PALAVRAS NEGATIVAS / BLACKLIST A IGNORAR: ${JSON.stringify(blacklist)}
MÁXIMO DE SUGESTÕES SOLICITADAS: ${maxSuggestions}

Sua missão:
1. Sugerir até ${maxSuggestions} termos de busca estratégicos, altamente pesquisados por compradores no Mercado Livre e Shopee dentro desse nicho.
2. Não sugerir termos já existentes em "TERMOS JÁ MONITORADOS".
3. Não sugerir termos que contenham qualquer palavra da "BLACKLIST".
4. Fornecer uma breve justificativa estratégica para cada sugestão (ex: "Alta demanda para festas infantis").

Retorne EXCLUSIVAMENTE um JSON válido no formato exato:
{
  "sugestoes": [
    {
      "termo": "nome do termo de busca",
      "motivo": "justificativa curta de mercado"
    }
  ]
}
`
        const res = await $fetch<any>(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: {
            contents: [{ parts: [{ text: prompt }] }],
            generationConfig: { responseMimeType: 'application/json' }
          }
        })

        const text = res?.candidates?.[0]?.content?.parts?.[0]?.text
        if (text) {
          return JSON.parse(text)
        }
      } catch (e: any) {
        console.warn(`Erro ao conectar ao modelo ${modelName} no /api/ai-keywords:`, e?.message || e)
      }
    }
  }

  // Fallback inteligente caso a chave da API falhe
  const fallbacks = [
    { termo: `${niche} personalizado`, motivo: "Alta busca por itens customizados no e-commerce" },
    { termo: `topo de bolo ${niche}`, motivo: "Forte tração em festas e aniversários" },
    { termo: `lembrancinha ${niche}`, motivo: "Volume recorrente em kits atacado" },
    { termo: `chaveiro ${niche}`, motivo: "Ticket acessível e giro rápido" },
    { termo: `vela ${niche}`, motivo: "Item indispensável em comemorações infantis" },
    { termo: `kit festa ${niche}`, motivo: "Maior ticket médio por pedido" }
  ].filter(s => !currentTerms.includes(s.termo) && !blacklist.some(b => s.termo.toLowerCase().includes(b.toLowerCase())))

  return { sugestoes: fallbacks.slice(0, maxSuggestions) }
})
