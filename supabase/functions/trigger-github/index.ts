import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Trata requisições de preflight CORS do navegador
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const githubToken = Deno.env.get('GITHUB_PAT')
    if (!githubToken) {
      throw new Error('Secret GITHUB_PAT não foi configurado no Supabase.')
    }

    const response = await fetch('https://api.github.com/repos/MarshalFilho/biscuit_scraper/dispatches', {
      method: 'POST',
      headers: {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': `Bearer ${githubToken}`,
        'User-Agent': 'Supabase-Edge-Function'
      },
      body: JSON.stringify({
        event_type: 'disparo_supabase'
      })
    })

    if (!response.ok) {
      const errBody = await response.text()
      throw new Error(`Erro na API do GitHub (${response.status}): ${errBody}`)
    }

    return new Response(
      JSON.stringify({ success: true, message: 'GitHub Actions ativado com sucesso!' }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 200 }
    )
  } catch (error: any) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 400 }
    )
  }
})
