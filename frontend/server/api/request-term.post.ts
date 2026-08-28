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

  const termo = String(body?.termo || '').trim()
  const motivo = String(body?.motivo || '').trim()
  const nicho = String(body?.nicho || '').trim()

  if (!termo || termo.length < 2) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Por favor, informe o termo ou palavra-chave que deseja solicitar.'
    })
  }

  // 2. Busca lista atual de solicitações na tabela de configurações
  const { data: configData } = await supabaseServer
    .from('configuracoes_scraper')
    .select('solicitacoes_termos, termos_busca')
    .eq('user_id', targetUserId)
    .limit(1)
    .maybeSingle()

  const currentRequests: any[] = Array.isArray(configData?.solicitacoes_termos) ? configData.solicitacoes_termos : []
  const currentTerms: string[] = Array.isArray(configData?.termos_busca) ? configData.termos_busca : []

  if (currentTerms.map(t => t.toLowerCase()).includes(termo.toLowerCase())) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Este termo já está sendo monitorado ativamente no robô.'
    })
  }

  const newRequest = {
    id: `req_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
    termo,
    motivo: motivo || 'Solicitação de novo produto/termo pelo cliente',
    nicho: nicho || '',
    solicitante_email: user?.email || 'cliente@plataforma.com',
    solicitante_id: targetUserId,
    data_solicitacao: new Date().toISOString(),
    status: 'pendente'
  }

  const updatedRequests = [newRequest, ...currentRequests.slice(0, 49)]

  // 3. Salva a nova solicitação no Supabase
  const { error } = await supabaseServer
    .from('configuracoes_scraper')
    .upsert({
      user_id: targetUserId,
      solicitacoes_termos: updatedRequests,
      updated_at: new Date().toISOString()
    }, { onConflict: 'user_id' })

  if (error) {
    console.error('Erro ao salvar solicitação:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Erro ao registrar solicitação no banco de dados.'
    })
  }

  return {
    success: true,
    message: 'Solicitação de novo termo enviada com sucesso ao administrador!',
    solicitacao: newRequest
  }
})
