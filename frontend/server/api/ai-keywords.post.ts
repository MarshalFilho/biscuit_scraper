import { createClient } from '@supabase/supabase-js'

const RATE_LIMIT_WINDOW_MS = 3 * 60 * 60 * 1000 // 3 horas
const MAX_REQUESTS_PER_WINDOW = 2 // Máximo de 2 chamadas a cada 3 horas por conta
const COOLDOWN_SECONDS = 20 // Cooldown de 20s entre chamadas

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const supabaseUrl = config.public.supabaseUrl || process.env.SUPABASE_URL || 'https://tqyhsxgsauwdzkepfqnr.supabase.co'
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY || config.supabaseServiceRoleKey || process.env.SUPABASE_KEY || config.public.supabaseAnonKey

  const supabaseServer = createClient(supabaseUrl, serviceRoleKey, {
    auth: { persistSession: false }
  })

  // 1. Identifica usuário autenticado via JWT Bearer Token ou body
  const authHeader = getRequestHeader(event, 'authorization')
  let authenticatedUserId: string | null = null

  if (authHeader && authHeader.startsWith('Bearer ')) {
    const token = authHeader.replace('Bearer ', '').trim()
    const { data: { user } } = await supabaseServer.auth.getUser(token)
    if (user) {
      authenticatedUserId = user.id
    }
  }

  const body = await readBody(event)
  const targetUserId = authenticatedUserId || body?.userId

  const now = Date.now()
  let userHistory: number[] = []

  // 2. Consulta histórico de uso da IA no Banco de Dados (Supabase)
  if (targetUserId) {
    const { data: userConfig } = await supabaseServer
      .from('configuracoes_scraper')
      .select('regras_categoria')
      .eq('user_id', targetUserId)
      .limit(1)
      .maybeSingle()

    if (userConfig && Array.isArray(userConfig.regras_categoria)) {
      // Filtra timestamps dentro da janela de 3 horas
      userHistory = userConfig.regras_categoria
        .map((item: any) => typeof item === 'number' ? item : item?.timestamp)
        .filter((ts: any) => typeof ts === 'number' && (now - ts) < RATE_LIMIT_WINDOW_MS)
    }

    // Checagem de Cooldown (última chamada)
    if (userHistory.length > 0) {
      const lastCall = Math.max(...userHistory)
      const timeSinceLast = (now - lastCall) / 1000
      if (timeSinceLast < COOLDOWN_SECONDS) {
        const waitTime = Math.ceil(COOLDOWN_SECONDS - timeSinceLast)
        throw createError({
          statusCode: 429,
          statusMessage: `COOLDOWN:${waitTime}`
        })
      }
    }

    // Checagem de Cota Máxima no Banco (2 a cada 3 horas)
    if (userHistory.length >= MAX_REQUESTS_PER_WINDOW) {
      const oldestCall = Math.min(...userHistory)
      const resetTime = oldestCall + RATE_LIMIT_WINDOW_MS
      const minutesLeft = Math.max(1, Math.ceil((resetTime - now) / 60000))
      const hoursLeft = Math.floor(minutesLeft / 60)
      const minsRemainder = minutesLeft % 60
      const timeText = hoursLeft > 0 ? `${hoursLeft}h ${minsRemainder}min` : `${minutesLeft}min`

      throw createError({
        statusCode: 429,
        statusMessage: `RATE_LIMIT:${timeText}`
      })
    }
  }

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

  const geminiKey = config.geminiApiKey || process.env.GEMINI_API_KEY
  let generatedSuggestions: any[] | null = null

  if (geminiKey) {
    // Modelos ordenados pelo menor custo por token (Flash Lite e Flash)
    const models = ['gemini-2.5-flash-lite', 'gemini-1.5-flash-8b', 'gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-3.6-flash']
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
          if (parsed?.sugestoes && Array.isArray(parsed.sugestoes)) {
            generatedSuggestions = parsed.sugestoes
            break
          }
        }
      } catch (e: any) {
        console.warn(`Erro ao conectar ao modelo ${modelName} no /api/ai-keywords:`, e?.message || e)
      }
    }
  }

  if (!generatedSuggestions) {
    // Fallback inteligente
    generatedSuggestions = [
      { termo: `${niche} personalizado`, motivo: "Alta busca por itens customizados no e-commerce" },
      { termo: `topo de bolo ${niche}`, motivo: "Forte tração em festas e aniversários" },
      { termo: `lembrancinha ${niche}`, motivo: "Volume recorrente em kits atacado" },
      { termo: `chaveiro ${niche}`, motivo: "Ticket acessível e giro rápido" },
      { termo: `vela ${niche}`, motivo: "Item indispensável em comemorações infantis" },
      { termo: `kit festa ${niche}`, motivo: "Maior ticket médio por pedido" }
    ].filter(s => !currentTerms.includes(s.termo) && !blacklist.some(b => s.termo.toLowerCase().includes(b.toLowerCase()))).slice(0, maxSuggestions)
  }

  // 3. Registra a requisição no Banco de Dados (Supabase) para o usuário
  if (targetUserId) {
    userHistory.push(now)
    await supabaseServer
      .from('configuracoes_scraper')
      .upsert({
        user_id: targetUserId,
        regras_categoria: userHistory,
        updated_at: new Date().toISOString()
      }, { onConflict: 'user_id' })
  }

  return {
    sugestoes: generatedSuggestions,
    remainingQuota: Math.max(0, MAX_REQUESTS_PER_WINDOW - (userHistory.length || 1))
  }
})
