// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  modules: [
    'nuxt-security',
    '@nuxt/eslint'
  ],
  security: {
    corsHandler: {
      origin: '*', // Adjust this in production
      methods: ['GET', 'POST', 'PATCH', 'DELETE']
    }
  },
  runtimeConfig: {
    databaseUrl: process.env.DATABASE_URL,
    jwtSecret: process.env.JWT_SECRET
  }
})
