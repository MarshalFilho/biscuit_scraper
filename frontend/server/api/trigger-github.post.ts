export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const token = config.githubToken || process.env.GITHUB_PAT

  if (!token) {
    throw createError({
      statusCode: 500,
      statusMessage: 'Variável GITHUB_PAT não encontrada no .env ou runtimeConfig.'
    })
  }

  try {
    await $fetch('https://api.github.com/repos/MarshalFilho/biscuit_scraper/dispatches', {
      method: 'POST',
      headers: {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': `Bearer ${token}`,
        'User-Agent': 'Biscuit-Scraper-Dashboard'
      },
      body: {
        event_type: 'disparo_supabase'
      }
    })

    return { success: true, message: 'Disparo enviado com sucesso ao GitHub Actions!' }
  } catch (error: any) {
    console.error('Erro ao acionar GitHub Actions:', error)
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.message || 'Falha ao comunicar com o GitHub Actions'
    })
  }
})
