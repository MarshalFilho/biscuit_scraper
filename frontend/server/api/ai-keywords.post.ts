// In-memory rate limiting map: IP -> { count, lastRequestTime, resetTime }
const rateLimitMap = new Map<string, { count: number; lastRequestTime: number; resetTime: number }>()

const RATE_LIMIT_WINDOW_MS = 60 * 60 * 1000 // 1 hora
const MAX_REQUESTS_PER_WINDOW = 15 // Máximo de 15 chamadas por hora por IP/Usuário
const COOLDOWN_SECONDS = 10 // Cooldown de 10s entre chamadas

export default defineEventHandler(async (event) => {
  // 1. Identifica IP do cliente para proteção de cota
  const clientIp = getRequestHeader(event, 'x-forwarded-for') || 
                   getRequestHeader(event, 'x-real-ip') || 
                   event.node.req.socket.remoteAddress || 
                   'unknown_client'

  const now = Date.now()
  let clientLimit = rateLimitMap.get(clientIp)

  if (!clientLimit || now > clientLimit.resetTime) {
    clientLimit = { count: 0, lastRequestTime: 0, resetTime: now + RATE_LIMIT_WINDOW_MS }
    rateLimitMap.set(clientIp, clientLimit)
  }

  // Checagem de Cooldown (anti-spam de cliques rápidos)
  const timeSinceLast = (now - clientLimit.lastRequestTime) / 1000
  if (timeSinceLast < COOLDOWN_SECONDS) {
    const waitTime = Math.ceil(COOLDOWN_SECONDS - timeSinceLast)
    throw createError({
      statusCode: 429,
      statusMessage: `⚠️ Por favor, aguarde ${waitTime} segundos antes de solicitar novas sugestões da IA.`
    })
  }

  // Checagem de Cota Máxima por Janela
  if (clientLimit.count >= MAX_REQUESTS_PER_WINDOW) {
    const minutesLeft = Math.ceil((clientLimit.resetTime - now) / 60000)
    throw createError({
      statusCode: 429,
      statusMessage: `⚠️ Limite de segurança de IA atingido (máx. ${MAX_REQUESTS_PER_WINDOW} consultas/hora). Tente novamente em ${minutesLeft} minutos.`
    })
  }

  const body = await readBody(event)
  
  // Sanitização e validação de tamanho de texto
  let niche = String(body?.niche || 'Geral').trim()
  if (niche.length > 60) {
    niche = niche.substring(0, 60)
  }
  if (!niche) {
    niche = 'Geral'
  }

  const currentTerms = Array.isArray(body?.currentTerms) ? body.currentTerms.slice(0, 15) : []
  const blacklist = Array.isArray(body?.blacklist) ? body.blacklist.slice(0, 30) : []
  const maxSuggestions = Math.min(8, Math.max(1, Number(body?.maxSuggestions) || 6))

  // Registra uso
  clientLimit.count += 1
  clientLimit.lastRequestTime = now

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
          const parsed = JSON.parse(text)
          return {
            ...parsed,
            remainingQuota: MAX_REQUESTS_PER_WINDOW - clientLimit.count
          }
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

  return {
    sugestoes: fallbacks.slice(0, maxSuggestions),
    remainingQuota: MAX_REQUESTS_PER_WINDOW - clientLimit.count
  }
})
