import { createClient } from '@supabase/supabase-js'

let supabaseInstance: any = null

export function useSupabase() {
  if (!supabaseInstance) {
    const config = useRuntimeConfig()
    const url = config.public.supabaseUrl || ''
    const key = config.public.supabaseAnonKey || ''
    
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
