import { spawn } from 'child_process'
import path from 'path'

let activeProcess: any = null

export default defineEventHandler(async (event) => {
  const body = await readBody(event).catch(() => ({}))
  const plataforma = body?.plataforma || 'todos'

  if (activeProcess) {
    return {
      success: false,
      message: 'O scraper já está rodando em segundo plano no servidor local.'
    }
  }

  try {
    const projectRoot = path.resolve(process.cwd(), '..')
    const mainScript = path.join(projectRoot, 'src', 'main.py')

    console.log(`🚀 [API Local] Iniciando disparo do backend Python: py -u ${mainScript} --plataforma ${plataforma}`)

    activeProcess = spawn('py', ['-u', mainScript, '--plataforma', plataforma], {
      cwd: projectRoot,
      env: { ...process.env, PYTHONUNBUFFERED: '1', PYTHONIOENCODING: 'utf-8' }
    })

    activeProcess.stdout?.on('data', (data: any) => {
      console.log(`[Python Stdout]: ${data.toString().trim()}`)
    })

    activeProcess.stderr?.on('data', (data: any) => {
      console.error(`[Python Stderr]: ${data.toString().trim()}`)
    })

    activeProcess.on('close', (code: number) => {
      console.log(`✅ [API Local] Processo Python encerrado com código: ${code}`)
      activeProcess = null
    })

    return {
      success: true,
      message: `Scraper acionado com sucesso no backend local (Plataforma: ${plataforma})!`
    }
  } catch (error: any) {
    console.error('Erro ao acionar o scraper local:', error)
    activeProcess = null
    throw createError({
      statusCode: 500,
      statusMessage: error.message || 'Falha ao executar o script Python local.'
    })
  }
})
