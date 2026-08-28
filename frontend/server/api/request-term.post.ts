import { createClient } from '@supabase/supabase-js'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const supabaseUrl = config.public.supabaseUrl || process.env.SUPABASE_URL || 'https://tqyhsxgsauwdzkepfqnr.supabase.co'
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY || config.supabaseServiceRoleKey || process.env.SUPABASE_KEY || config.public.supabaseAnonKey

  const supabaseServer = createClient(supabaseUrl, serviceRoleKey, {
    auth: { persistSession: false }
  })

  // 1. Validação de usuário autenticado
  const user = await getAuthenticatedUser(event, supabaseServer)
  const body = await readBody(event)
  const targetUserId = user?.id || body?.userId

  if (!targetUserId) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Acesso não autorizado. Sessão de usuário inválida ou expirada.'
    })
  }

  // 2. Carrega configuração atual do usuário
  const { data: configData, error: fetchErr } = await supabaseServer
    .from('configuracoes_scraper')
    .select('regras_categoria, termos_busca')
    .eq('user_id', targetUserId)
    .limit(1)
    .maybeSingle()

  if (fetchErr) {
    console.error('Erro ao buscar configuracoes do usuario:', fetchErr)
  }

  // Parse seguro de regras_categoria (pode ser array antigo de timestamps ou objeto)
  let rawCategoryRules = configData?.regras_categoria
  let rateLimit: any[] = []
  let currentPendingRequest: any = null

  if (Array.isArray(rawCategoryRules)) {
    rateLimit = rawCategoryRules
  } else if (rawCategoryRules && typeof rawCategoryRules === 'object') {
    rateLimit = Array.isArray(rawCategoryRules.rate_limit) ? rawCategoryRules.rate_limit : []
    currentPendingRequest = rawCategoryRules.solicitacao_pendente || null
  }

  // 3. Ação: CANCELAR / EXCLUIR SOLICITAÇÃO EXISTENTE
  if (body?.action === 'cancel') {
    const updatedCategoryRules = {
      rate_limit: rateLimit,
      solicitacao_pendente: null
    }

    const { error: cancelErr } = await supabaseServer
      .from('configuracoes_scraper')
      .upsert({
        user_id: targetUserId,
        regras_categoria: updatedCategoryRules,
        updated_at: new Date().toISOString()
      }, { onConflict: 'user_id' })

    if (cancelErr) {
      console.error('Erro ao cancelar solicitação:', cancelErr)
      throw createError({
        statusCode: 500,
        statusMessage: 'Erro ao cancelar solicitação no banco de dados.'
      })
    }

    return {
      success: true,
      message: 'Solicitação cancelada com sucesso.',
      solicitacao: null
    }
  }

  // 4. Ação: CRIAR OU EDITAR SOLICITAÇÃO
  const termo = String(body?.termo || '').trim()
  const motivo = String(body?.motivo || '').trim()
  const nicho = String(body?.nicho || '').trim()

  if (!termo || termo.length < 2) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Por favor, informe o termo ou palavra-chave que deseja solicitar.'
    })
  }

  const currentTerms: string[] = Array.isArray(configData?.termos_busca) ? configData.termos_busca : []
  if (currentTerms.map(t => t.toLowerCase()).includes(termo.toLowerCase())) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Este termo já está cadastrado e monitorado no robô.'
    })
  }

  const newOrUpdatedRequest = {
    id: currentPendingRequest?.id || `req_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
    termo,
    motivo: motivo || 'Solicitação de novo produto/termo pelo cliente',
    nicho: nicho || '',
    solicitante_email: user?.email || 'cliente@plataforma.com',
    solicitante_id: targetUserId,
    data_solicitacao: currentPendingRequest?.data_solicitacao || new Date().toISOString(),
    data_atualizacao: new Date().toISOString(),
    status: 'pendente'
  }

  const updatedCategoryRules = {
    rate_limit: rateLimit,
    solicitacao_pendente: newOrUpdatedRequest
  }

  // 5. Salva no Supabase
  const { error: saveErr } = await supabaseServer
    .from('configuracoes_scraper')
    .upsert({
      user_id: targetUserId,
      regras_categoria: updatedCategoryRules,
      updated_at: new Date().toISOString()
    }, { onConflict: 'user_id' })

  if (saveErr) {
    console.error('Erro ao salvar solicitação:', saveErr)
    throw createError({
      statusCode: 500,
      statusMessage: 'Erro ao registrar solicitação no banco de dados: ' + saveErr.message
    })
  }

  return {
    success: true,
    message: currentPendingRequest ? 'Solicitação atualizada com sucesso!' : 'Solicitação enviada com sucesso ao administrador!',
    solicitacao: newOrUpdatedRequest
  }
})
