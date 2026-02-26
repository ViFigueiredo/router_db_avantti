export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.config.errorHandler = (error, instance, info) => {
    const route = useRoute()
    
    // Log to console for development
    console.error('Client Error:', error)

    // Send to our server-side logging endpoint
    $fetch('/api/log', {
      method: 'POST',
      body: {
        level: 'ERROR',
        route: route.path,
        message: error instanceof Error ? error.message : String(error),
        details: {
          stack: error instanceof Error ? error.stack : '',
          info,
          component: instance?.$options?.name || 'unknown'
        }
      }
    }).catch(e => console.error('Failed to send log to server:', e))
  }

  // Also catch unhandled rejections
  if (process.client) {
    window.addEventListener('unhandledrejection', (event) => {
      const route = useRoute()
      $fetch('/api/log', {
        method: 'POST',
        body: {
          level: 'ERROR',
          route: route.path,
          message: 'Unhandled Promise Rejection',
          details: {
            reason: event.reason
          }
        }
      }).catch(e => console.error('Failed to send rejection log to server:', e))
    })
  }
})
