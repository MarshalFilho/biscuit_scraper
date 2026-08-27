import { createClient } from '@supabase/supabase-js'

let supabaseInstance: any = null

export function useSupabase() {
  if (!supabaseInstance) {
    const config = useRuntimeConfig()
    const url = config.public.supabaseUrl || 'https://tqyhsxgsauwdzkepfqnr.supabase.co'
    const key = config.public.supabaseAnonKey || 'sb_publishable_kqWoyeju_tYLSzZQfs_FPw_bNrxXr4f'
    
    supabaseInstance = createClient(url, key, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true
      }
    })
  }
  return supabaseInstance
}
