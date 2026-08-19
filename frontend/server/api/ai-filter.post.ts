export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const promptText = body?.prompt || ''

  if (!promptText.trim()) {
    return { termos: ['biscuit artesanato'], blacklist: ['molde', 'silicone'] }
  }

  const config = useRuntimeConfig()
  const geminiKey = config.geminiApiKey || process.env.GEMINI_API_KEY
  if (geminiKey) {
    try {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key=${geminiKey}`
      const prompt = `
Você é um Especialista em Extração de Intenção e SEO para E-commerce.
O usuário digitou a seguinte solicitação em linguagem natural para configurar termos de busca de um robô de scraping:

SOLICITAÇÃO DO USUÁRIO: "${promptText}"

Sua tarefa:
1. Extrair TODOS os termos de busca que o usuário deseja monitorar ("termos"). Cada produto ou variação mencionado pelo usuário DEVE virar um termo de busca preciso e relevante para e-commerce. NÃO OMITA NENHUM ITEM SOLICITADO!
2. Extrair TODAS as palavras, acessórios, ferramentas ou termos que o usuário deseja ignorar ("blacklist").

Retorne EXCLUSIVAMENTE um JSON valido no formato exato:
{
  "termos": ["termo de busca 1", "termo de busca 2", ...],
  "blacklist": ["palavra a ignorar 1", "palavra a ignorar 2", ...]
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
    } catch (e) {
      console.warn("Erro ao conectar Gemini API no /api/ai-filter:", e)
    }
  }

  // Fallback local NLP
  const text = promptText.toLowerCase()
  const termos: string[] = []
  const blacklist: string[] = []

  if (text.includes('topo') || text.includes('bolo')) termos.push('topo de bolo biscuit', 'vela biscuit')
  if (text.includes('lembrancinha') || text.includes('festa')) termos.push('lembrancinha biscuit', 'kit lembrancinha')
  if (text.includes('noivinho') || text.includes('casamento')) termos.push('noivinhos biscuit', 'casal biscuit')
  if (termos.length === 0) termos.push('biscuit artesanato')

  if (text.includes('molde') || text.includes('silicone')) blacklist.push('molde', 'silicone')
  if (text.includes('esteca') || text.includes('ferramenta')) blacklist.push('esteca', 'ferramenta')
  if (blacklist.length === 0) blacklist.push('molde', 'silicone')

  return { termos, blacklist }
})
