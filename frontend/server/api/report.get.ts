import fs from 'fs'
import path from 'path'

export default defineEventHandler((event) => {
  try {
    const reportPath = path.resolve(process.cwd(), '../reports/relatorio_executivo.json')
    if (fs.existsSync(reportPath)) {
      const content = fs.readFileSync(reportPath, 'utf-8')
      return JSON.parse(content)
    }
  } catch (e) {
    console.warn("Erro ao ler relatorio_executivo.json local:", e)
  }
  return null
})
