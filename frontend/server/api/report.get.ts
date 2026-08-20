import fs from 'fs'
import path from 'path'
import { createClient } from '@supabase/supabase-js'

export default defineEventHandler(async (event) => {
  // 1. Tenta ler local se estiver em dev
  try {
    const reportPath = path.resolve(process.cwd(), '../reports/relatorio_executivo.json')
    if (fs.existsSync(reportPath)) {
      const content = fs.readFileSync(reportPath, 'utf-8')
      return JSON.parse(content)
    }
  } catch (e) {}

  // 2. Tenta ler do Supabase se estiver na Vercel / Nuvem
  try {
    const config = useRuntimeConfig()
    const supabaseUrl = config.public.supabaseUrl || process.env.SUPABASE_URL
    const supabaseKey = config.public.supabaseAnonKey || process.env.SUPABASE_KEY

    if (supabaseUrl && supabaseKey) {
      const supabase = createClient(supabaseUrl, supabaseKey)
      const { data } = await supabase.from('configuracoes_scraper').select('relatorio_insights').limit(1).single()
      if (data && data.relatorio_insights) {
        return data.relatorio_insights
      }
    }
  } catch (e) {
    console.warn("Nao foi possivel buscar relatorio_insights no Supabase:", e)
  }

  return null
})
