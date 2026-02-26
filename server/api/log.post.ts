import fs from 'node:fs'
import path from 'node:path'
import { defineEventHandler, readBody } from 'h3'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const logsDir = path.resolve(process.cwd(), 'logs')
  const date = new Date().toISOString().split('T')[0]
  const logPath = path.join(logsDir, `frontend_client_${date}.log`)

  if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true })
  }

  const logEntry = {
    timestamp: new Date().toISOString(),
    level: body.level || 'INFO',
    module: 'nuxt-client',
    route: body.route || 'unknown',
    message: body.message,
    details: body.details || {}
  }

  fs.appendFileSync(logPath, `${JSON.stringify(logEntry)}\n`, 'utf-8')

  return { success: true }
})
