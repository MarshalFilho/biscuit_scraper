import { H3Event, getRequestHeader } from 'h3'
import { SupabaseClient } from '@supabase/supabase-js'

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
 * Validação rigorosa de Cargo no Backend (Admin vs Cliente)
 */
export function checkIsAdmin(user: any): boolean {
  if (!user) return false

  // 1. Metadados do Supabase Auth
  const appRole = user.app_metadata?.role
  const userRole = user.user_metadata?.role
  const directRole = user.role

  if (appRole === 'admin' || userRole === 'admin' || directRole === 'admin') {
    return true
  }

  // 2. Se for explicitamente cliente, bloqueia
  if (appRole === 'cliente' || userRole === 'cliente' || directRole === 'cliente') {
    return false
  }

  // 3. Lista de e-mails de Administradores via Variável de Ambiente
  const adminEmails = (process.env.ADMIN_EMAILS || '')
    .split(',')
    .map((e: string) => e.trim().toLowerCase())
    .filter(Boolean)

  if (user.email && adminEmails.includes(user.email.toLowerCase())) {
    return true
  }

  // 4. Por padrão, se não for marcado como cliente, mantém permissão
  return true
}
