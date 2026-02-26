import fs from 'node:fs'
import path from 'node:path'
import { defineNitroPlugin } from 'nitropack/runtime/plugin'

export default defineNitroPlugin((nitroApp) => {
  const logsDir = path.resolve(process.cwd(), 'logs')
  
  if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true })
  }

  const getLogPath = () => {
    const date = new Date().toISOString().split('T')[0]
    return path.join(logsDir, `frontend_${date}.log`)
  }

  const writeLog = (level: string, message: any, event?: any) => {
    const timestamp = new Date().toISOString()
    const logEntry = {
      timestamp,
      level,
      module: 'nuxt-server',
      route: event?.path || 'unknown',
      message: typeof message === 'string' ? message : JSON.stringify(message),
      details: event ? {
        method: event.method,
        headers: event.headers
      } : {}
    }

    fs.appendFileSync(getLogPath(), `${JSON.stringify(logEntry)}\n`, 'utf-8')
  }

  // Hook into errors
  nitroApp.hooks.hook('error', (error, { event }) => {
    writeLog('ERROR', error.stack || error.message, event)
  })

  // Hook into requests (optional, but good for "robust" logging)
  nitroApp.hooks.hook('render:response', (response, { event }) => {
    if (event.path.startsWith('/api/') || response.statusCode >= 400) {
      writeLog(response.statusCode >= 400 ? 'ERROR' : 'INFO', `Response sent for ${event.path}`, event)
    }
  })
})
