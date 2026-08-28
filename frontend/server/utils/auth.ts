import { H3Event, getRequestHeader } from 'h3'
import { SupabaseClient } from '@supabase/supabase-js'

export type UserRole = 'admin' | 'pro' | 'basic'

/**
 * Extrai e valida o usuário autenticado via Bearer Token JWT do Supabase
 */
export async function getAuthenticatedUser(event: H3Event, supabaseServer: SupabaseClient) {
  const authHeader = getRequestHeader(event, 'authorization')
  if (authHeader && authHeader.startsWith('Bearer ')) {
    const token = authHeader.replace('Bearer ', '').trim()
    const { data: { user }, error } = await supabaseServer.auth.getUser(token)
    if (user && !error) {
      return user
    }
  }
  return null
}

/**
 * Identifica o Cargo do Usuário (Admin, Pro, Basic)
 */
export function getUserRole(user: any): UserRole {
  if (!user) return 'basic'

  const appRole = String(user.app_metadata?.role || '').toLowerCase()
  const userRole = String(user.user_metadata?.role || '').toLowerCase()
  const directRole = String(user.role || '').toLowerCase()

  if (appRole === 'admin' || userRole === 'admin' || directRole === 'admin') return 'admin'
  if (appRole === 'pro' || userRole === 'pro' || directRole === 'pro') return 'pro'
  if (appRole === 'basic' || userRole === 'basic' || directRole === 'basic' || appRole === 'light' || userRole === 'light' || appRole === 'cliente') return 'basic'

  const email = (user.email || '').toLowerCase()
  const adminEmails = (process.env.ADMIN_EMAILS || 'adm@gmail.com')
    .split(',')
    .map((e: string) => e.trim().toLowerCase())
    .filter(Boolean)

  if (adminEmails.includes(email)) return 'admin'

  const proEmails = ['marshalfilho@gmail.com', 'isadora@gmail.com']
  if (proEmails.includes(email)) return 'pro'

  return 'basic'
}

/**
 * Verifica se o usuário tem permissão para alterar termos manualmente
 * - Admin: Sim (Ilimitado)
 * - Pro: Sim (Ilimitado para si mesmo)
 * - Basic: Não (Apenas solicita)
 */
export function checkCanManageKeywords(user: any): boolean {
  const role = getUserRole(user)
  return role === 'admin' || role === 'pro'
}

/**
 * Retorna a cota diária de consultas de IA por cargo
 * - Admin: 10/dia
 * - Pro: 5/dia
 * - Basic: 0
 */
export function getAiDailyQuota(user: any): number {
  const role = getUserRole(user)
  if (role === 'admin') return 10
  if (role === 'pro') return 5
  return 0
}
