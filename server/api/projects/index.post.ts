import { defineEventHandler, readBody, createError } from 'h3'
import prisma from '../../utils/prisma'
import { z } from 'zod'

const projectSchema = z.object({
  name: z.string().min(1),
  slug: z.string().min(1),
  sqlServer: z.object({
    host: z.string().min(1),
    port: z.number().default(1433),
    database: z.string().min(1),
    username: z.string().min(1),
    password: z.string().min(1)
  })
})

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  
  const validation = projectSchema.safeParse(body)
  if (!validation.success) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Invalid project data',
      data: validation.error.errors
    })
  }

  const { name, slug, sqlServer } = validation.data

  try {
    const project = await prisma.project.create({
      data: {
        name,
        slug,
        databaseConnections: {
          create: {
            type: 'SQLSERVER',
            ...sqlServer
          }
        }
      },
      include: {
        databaseConnections: true
      }
    })

    return {
      success: true,
      project
    }
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error)
    if (typeof error === 'object' && error !== null && 'code' in error && error.code === 'P2002') {
      throw createError({
        statusCode: 409,
        statusMessage: 'Project slug or API Key already exists',
      })
    }
    throw createError({
      statusCode: 500,
      statusMessage: 'Error creating project',
      data: message
    })
  }
})
