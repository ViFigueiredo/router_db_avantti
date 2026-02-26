import { defineEventHandler, readBody, createError } from 'h3'
import { getSqlServerConnection, executeQuery } from '../../utils/sqlserver'
import { z } from 'zod'

const querySchema = z.object({
  sql: z.string().min(1),
  params: z.record(z.any()).optional()
})

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  
  const validation = querySchema.safeParse(body)
  if (!validation.success) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Invalid query body',
      data: validation.error.errors
    })
  }

  const { sql, params } = validation.data
  const sqlConfig = event.context.sqlConfig

  try {
    const pool = await getSqlServerConnection({
      id: sqlConfig.id,
      host: sqlConfig.host,
      port: sqlConfig.port,
      database: sqlConfig.database,
      username: sqlConfig.username,
      password: sqlConfig.password
    })

    const data = await executeQuery(pool, sql, params)

    return {
      success: true,
      data
    }
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error)
    console.error('SQL Server Query Error:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Error executing SQL query',
      data: message
    })
  }
})
