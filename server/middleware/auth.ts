import { defineEventHandler, getHeader, createError } from 'h3'
import prisma from '../utils/prisma'

export default defineEventHandler(async (event) => {
  // Only protect /api routes
  if (!event.path.startsWith('/api/')) return

  // Skip auth for project creation if needed, or implement a master key
  // For now, let's assume all /api/query routes need an API Key
  if (event.path.startsWith('/api/query')) {
    const apiKey = getHeader(event, 'x-api-key')

    if (!apiKey) {
      throw createError({
        statusCode: 401,
        statusMessage: 'API Key missing',
      })
    }

    const project = await prisma.project.findUnique({
      where: { apiKey },
      include: {
        databaseConnections: {
          where: { type: 'SQLSERVER' }
        }
      }
    })

    if (!project) {
      throw createError({
        statusCode: 401,
        statusMessage: 'Invalid API Key',
      })
    }

    if (!project.databaseConnections.length) {
      throw createError({
        statusCode: 400,
        statusMessage: 'No SQL Server configuration found for this project',
      })
    }

    // Attach project and config to context
    event.context.project = project
    event.context.sqlConfig = project.databaseConnections[0]
  }
})
