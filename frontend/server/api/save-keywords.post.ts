import { createClient } from '@supabase/supabase-js'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const userId = body?.userId
  const terms = Array.isArray(body?.terms) ? body.terms : []
  const blacklist = Array.isArray(body?.blacklist) ? body.blacklist : []

  if (!userId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'ID do usuário não fornecido.'
    })
  }

  if (terms.length === 0) {
    throw createError({
      statusCode: 400,
      statusMessage: 'É necessário manter pelo menos 1 termo ativo.'
    })
  }

  const config = useRuntimeConfig()
  const supabaseUrl = config.public.supabaseUrl || process.env.SUPABASE_URL || 'https://tqyhsxgsauwdzkepfqnr.supabase.co'
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY || config.supabaseServiceRoleKey || process.env.SUPABASE_KEY || config.public.supabaseAnonKey

  const supabaseServer = createClient(supabaseUrl, serviceRoleKey, {
    auth: { persistSession: false }
  })

  // Upsert seguro no Supabase com service role / server client
  const { data, error } = await supabaseServer
    .from('configuracoes_scraper')
    .upsert({
      user_id: userId,
      termos_busca: terms.slice(0, 15),
      blacklist: blacklist.slice(0, 50),
      status_scraper: '⚙️ Configurações de termos atualizadas pelo usuário.',
      updated_at: new Date().toISOString()
    }, { onConflict: 'user_id' })
    .select()

  if (error) {
    console.error('Erro no /api/save-keywords:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Erro ao salvar no banco de dados: ' + error.message
    })
  }

  return {
    success: true,
    data
  }
})
