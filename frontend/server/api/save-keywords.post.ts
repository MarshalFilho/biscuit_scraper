import { createClient } from '@supabase/supabase-js'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const supabaseUrl = config.public.supabaseUrl || process.env.SUPABASE_URL || 'https://tqyhsxgsauwdzkepfqnr.supabase.co'
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY || config.supabaseServiceRoleKey || process.env.SUPABASE_KEY || config.public.supabaseAnonKey

  const supabaseServer = createClient(supabaseUrl, serviceRoleKey, {
    auth: { persistSession: false }
  })

  // 1. Validação estrita de Autenticação JWT (Bearer Token)
  const user = await getAuthenticatedUser(event, supabaseServer)
  const body = await readBody(event)
  const targetUserId = user?.id || body?.userId

  if (!targetUserId) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Acesso não autorizado. Sessão de usuário inválida ou expirada.'
    })
  }

  // 2. Validação de Cargo no Backend (Admin e Pro permitidos; Light bloqueado)
  if (user && !checkCanManageKeywords(user)) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Acesso negado: Usuários do plano Light não têm permissão para alterar termos diretamente. Por favor, envie uma solicitação ao administrador.'
    })
  }

  // Previne tentativa de salvar dados para outro usuário
  if (user && body?.userId && user.id !== body.userId) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Acesso negado: Você só pode modificar as configurações da sua própria conta.'
    })
  }

  const terms = Array.isArray(body?.terms) ? body.terms : []
  const blacklist = Array.isArray(body?.blacklist) ? body.blacklist : []
  const solicitacoes = Array.isArray(body?.solicitacoes_termos) ? body.solicitacoes_termos : undefined

  if (terms.length === 0) {
    throw createError({
      statusCode: 400,
      statusMessage: 'É necessário manter pelo menos 1 termo ativo.'
    })
  }

  const payloadToSave: any = {
    user_id: targetUserId,
    termos_busca: terms.slice(0, 15),
    blacklist: blacklist.slice(0, 50),
    status_scraper: '⚙️ Configurações de termos atualizadas pelo administrador.',
    updated_at: new Date().toISOString()
  }

  if (solicitacoes !== undefined) {
    payloadToSave.solicitacoes_termos = solicitacoes.slice(0, 50)
  }

  // Upsert seguro no Supabase com validação
  const { data, error } = await supabaseServer
    .from('configuracoes_scraper')
    .upsert(payloadToSave, { onConflict: 'user_id' })
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
