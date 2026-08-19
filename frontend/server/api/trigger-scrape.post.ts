import { exec } from 'child_process'
import path from 'path'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const plataforma = body?.plataforma || 'todos'

  const config = useRuntimeConfig()
  const gcpUrl = process.env.GCP_CLOUD_RUN_URL

  // 1. Se houver URL do Google Cloud Run configurada, chama o Webhook da nuvem
  if (gcpUrl) {
    try {
      const res = await $fetch<any>(`${gcpUrl}/trigger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: { plataforma }
      })
      return { success: true, message: '🚀 Raspagem ativada com sucesso no Google Cloud!', data: res }
    } catch (err: any) {
      console.warn("Erro ao chamar Google Cloud Run, usando fallback local/Supabase:", err)
    }
  }

  // 2. Fallback: Executa o script Python localmente via subprocesso
  const rootDir = path.resolve(process.cwd(), '..')
  const scriptPath = path.join(rootDir, 'src', 'main.py')

  return new Promise((resolve) => {
    const command = `py "${scriptPath}" --plataforma ${plataforma}`
    exec(command, { cwd: rootDir }, (error, stdout, stderr) => {
      if (error) {
        resolve({ success: false, error: error.message })
      } else {
        resolve({ success: true, message: 'Raspagem local finalizada com sucesso!', output: stdout })
      }
    })
  })
})
