// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  modules: [
    'nuxt-security',
    '@nuxt/eslint',
    '@primevue/nuxt-module',
    '@nuxtjs/tailwindcss'
  ],
  primevue: {
    options: {
      ripple: true,
      inputVariant: 'filled'
    },
    autoImport: true
  },
  css: [
    'primeicons/primeicons.css'
  ],
  security: {
    corsHandler: {
      origin: '*', // Adjust this in production
      methods: ['GET', 'POST', 'PATCH', 'DELETE']
    }
  },
  runtimeConfig: {
    public: {
      apiUrl: process.env.API_URL || 'http://localhost:8000'
    }
  }
})
