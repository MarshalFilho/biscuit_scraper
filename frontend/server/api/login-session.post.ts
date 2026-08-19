import { exec } from 'child_process'
import path from 'path'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const plataforma = body?.plataforma || 'todos'

  const rootDir = path.resolve(process.cwd(), '..')
  const scriptPath = path.join(rootDir, 'src', 'main.py')

  return new Promise((resolve) => {
    // Executa o script Python com a flag --login
    const command = `py "${scriptPath}" --login`
    
    exec(command, { cwd: rootDir }, (error, stdout, stderr) => {
      if (error) {
        console.error("Erro ao executar login_session:", error)
        resolve({ success: false, error: error.message, output: stderr })
      } else {
        resolve({ success: true, message: `Sessão de login para ${plataforma} iniciada/atualizada com sucesso!`, output: stdout })
      }
    })
  })
})
